# Upstream Worldgen Port + pre-1.21.11 Drop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port upstream Stellarity worldgen (End height 384, island rework, noodle caves, floating_treasure) into Stellarity Lite, drop pre-1.21.11 support, restructure overlays to mirror upstream.

**Architecture:** Three worldgen layers mirroring upstream: base `data/` in 26.2 format (copied verbatim from upstream base), overlay `26_1/` (formats 94–101), overlay `1_21_11/` (format 94, listed after `26_1` so it wins). The `far_end` namespace stays ours (no merge into `stellarity`); its files flip layers only. Functions/scoreboards untouched.

**Tech Stack:** Minecraft datapack (JSON worldgen + mcfunction), no build system. Validation: python3 json parsing, cmp for NBT. System test: Codex drives `_servers/` (1.21.11, 26.1.2, 26.2) per AGENTS.md.

**Spec:** `docs/superpowers/specs/2026-07-05-upstream-gen-port-design.md`

## Global Constraints

- `LITE=/mnt/c/Users/narko/Desktop/CATCRAFT/stellarity_lite` — repo root; all paths below relative to it unless absolute.
- `SCRATCH=/tmp/claude-1000/-mnt-c-Users-narko-Desktop-CATCRAFT-stellarity-lite/4f6f1e9d-8d1f-44a6-b98f-14e4d4f0d3e8/scratchpad` — session scratchpad.
- `ORIG=$SCRATCH/stellarity-orig/datapack` — upstream clone. If missing, re-clone: `git clone --filter=blob:none https://github.com/Prismatic-Shards/Stellarity/ $SCRATCH/stellarity-orig`.
- Shell state does NOT persist between Bash calls: re-define `LITE`, `ORIG`, `SCRATCH` (and `export` them when a python heredoc reads `os.environ`) at the top of every Bash call.
- NEVER run blob-heavy git ops on the ORIG clone (`git log -S`, `--follow`) — it is blobless and they hang.
- Version window: `min_format: 94`, `max_format: 108`. Overlay ranges use dual syntax (`formats{min_inclusive,max_inclusive}` AND `min_format`/`max_format`).
- NEVER co-sign commits (no `Co-Authored-By`) — project rule, applies to every subagent.
- Implementer subagents are Sonnet. Fable is PM only and must not run as a subagent. Server tests run through Codex, results as a digest file.
- Copy files with `cp`/`rsync` from ORIG — never retype JSON by hand.
- Do not touch: `data/*/function/**` (except nothing — no function edits in this plan), `data/awesomedungeonend/`, `data/kohara/` (base), README, LICENSE, `*.zip`, `pack.png`, `_design/`, `_servers/` (except the test report), `.claude/`.
- `netherite_scrap` in floating_treasure loot: count exactly 1 (no set_count).
- Commit at the end of every task; plain `git commit -m`, no `--amend`, no `--no-verify` unless a hook rewrites the command.

---

### Task 1: Drop pre-1.21.11 support

**Files:**
- Delete: `1_21_7/`, `1_21_9/`, `_old/`
- Modify: `pack.mcmeta`

**Interfaces:**
- Produces: pack.mcmeta with only `1_21_11` and `26_2` overlay entries left (both restructured by later tasks); repo without dead overlays.

- [ ] **Step 1: Delete dead directories**

```bash
cd "$LITE" && git rm -rq 1_21_7 1_21_9 _old
```

- [ ] **Step 2: Update pack.mcmeta**

Remove the `1_21_9` and `1_21_7` overlay entries; set `min_format: 94` and `supported_formats: [94, 108]`. Keep `pack_format`, description, and the `1_21_11`/`26_2` entries untouched for now. Edit with python to avoid hand-JSON:

```bash
python3 - <<'EOF'
import json
p='pack.mcmeta'
m=json.load(open(p))
m['pack']['min_format']=94
m['pack']['supported_formats']=[94,108]
m['overlays']['entries']=[e for e in m['overlays']['entries'] if e['directory'] not in ('1_21_7','1_21_9')]
json.dump(m,open(p,'w'),indent='\t')
EOF
```

- [ ] **Step 3: Verify**

```bash
python3 -c "import json; m=json.load(open('pack.mcmeta')); assert m['pack']['min_format']==94; assert [e['directory'] for e in m['overlays']['entries']]==['1_21_11','26_2'], m['overlays']['entries']; print('OK')"
ls -d 1_21_7 1_21_9 _old 2>&1 | grep -c 'No such' # expect 3
```

Expected: `OK`, then `3`.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat!: drop support for MC versions below 1.21.11"
```

---

### Task 2: Replace base worldgen with upstream 26.2

**Files:**
- Replace dirs: `data/minecraft/dimension/`, `data/minecraft/dimension_type/`, `data/minecraft/worldgen/`, `data/stellarity/worldgen/` — all with ORIG's copies.
- Untouched on purpose: `data/far_end/**`, all `function/`, `tags/function/`, loot tables, `data/minecraft/the_end_constants_for_ctl_c_ctrl_v.md`.

**Interfaces:**
- Consumes: ORIG base (`$ORIG/data/...`), 26.2 format (pack_format 107).
- Produces: base worldgen identical to upstream base: height 384, `island_builder`/`shaper_*` DFs, `cave/noodle.json`, no `stellarity:the_void` in the dimension file, floating_treasure worldgen JSONs present (their loot table and NBT arrive in Task 6).

- [ ] **Step 1: Replace the four dirs**

```bash
cd "$LITE"
for d in minecraft/dimension minecraft/dimension_type minecraft/worldgen stellarity/worldgen; do
  git rm -rq "data/$d"
  mkdir -p "data/$(dirname $d)"
  cp -r "$ORIG/data/$d" "data/$d"
done
```

- [ ] **Step 2: Verify content markers**

```bash
grep -o '"height": *384' data/minecraft/worldgen/noise_settings/end.json data/minecraft/dimension_type/the_end.json | wc -l   # expect 2
grep -c the_void data/minecraft/dimension/the_end.json                                    # expect 0
ls data/stellarity/worldgen/density_function/cave/noodle.json data/stellarity/worldgen/density_function/main_island/island_builder.json data/stellarity/worldgen/structure/floating_treasure.json  # all exist
ls data/stellarity/worldgen/configured_feature/ | grep -c '^amethyst$\|^ash$\|^barrens$'   # expect 0 (old names gone)
```

- [ ] **Step 3: Verify all JSON parses**

```bash
python3 - <<'EOF'
import json,glob
fails=[]
for f in glob.glob('data/**/*.json',recursive=True):
    try: json.load(open(f))
    except Exception as e: fails.append((f,str(e)[:80]))
print(fails if fails else 'ALL PARSE OK', len(glob.glob('data/**/*.json',recursive=True)))
EOF
```

Expected: `ALL PARSE OK <count>`.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: port upstream 26.2 worldgen base (height 384, island rework, noodle caves)"
```

---

### Task 3: Flip far_end + predicate layers, dissolve 26_2 overlay

The `26_2/` overlay holds 26.2-format copies that now belong in base; the displaced base versions (26.1 format) move to the new `26_1/` overlay. Only 5 files need the flip — the other ~80 files of `26_2/` (stellarity CFs + minecraft dimension_type) are already superseded by Task 2's upstream copies and are deleted.

**Files:**
- Create: `26_1/data/...` (5 relocated files)
- Modify: base copies of the same 5 paths
- Delete: `26_2/`

The 5 flip paths (relative):
```
data/far_end/worldgen/configured_feature/amethyst/tree/umbrella.json
data/far_end/worldgen/configured_feature/ash/vegetation/land/trees.json
data/far_end/worldgen/configured_feature/tundra/tree/bone_fancy.json
data/far_end/worldgen/configured_feature/tundra/tree/bone_rib.json
data/stellarity/predicate/items/spirit_dagger/looking_at_spirit.json
```

**Interfaces:**
- Produces: base = 26.2-format far_end/predicate; `26_1/` dir exists with the 26.1-format versions; `26_2/` gone. pack.mcmeta still lists `26_2` — Task 5 rewrites the overlays block; the pack is not expected to load between Tasks 3–5.

- [ ] **Step 1: Flip the 5 files**

```bash
cd "$LITE"
for f in \
  data/far_end/worldgen/configured_feature/amethyst/tree/umbrella.json \
  data/far_end/worldgen/configured_feature/ash/vegetation/land/trees.json \
  data/far_end/worldgen/configured_feature/tundra/tree/bone_fancy.json \
  data/far_end/worldgen/configured_feature/tundra/tree/bone_rib.json \
  data/stellarity/predicate/items/spirit_dagger/looking_at_spirit.json; do
  mkdir -p "26_1/$(dirname $f)"
  mv "$f" "26_1/$f"          # old base (26.1 format) -> 26_1 overlay
  mv "26_2/$f" "$f"          # 26.2 format -> base
done
```

- [ ] **Step 2: Delete the rest of 26_2**

```bash
find 26_2 -type f | head -20   # eyeball: only stellarity worldgen CFs + minecraft dimension_type should remain
git rm -rq 26_2 2>/dev/null || rm -rf 26_2
```

If Step 2's `find` shows anything that is NOT `data/stellarity/worldgen/configured_feature/**` or `data/minecraft/dimension_type/the_end.json` — STOP and report instead of deleting.

- [ ] **Step 3: Verify**

```bash
ls 26_1/data/far_end/worldgen/configured_feature/tundra/tree/bone_rib.json 26_1/data/stellarity/predicate/items/spirit_dagger/looking_at_spirit.json
python3 -c "
import json
a=json.load(open('data/far_end/worldgen/configured_feature/tundra/tree/bone_rib.json'))
b=json.load(open('26_1/data/far_end/worldgen/configured_feature/tundra/tree/bone_rib.json'))
assert a!=b, 'base and 26_1 copies identical - flip failed'
print('flip OK')"
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "refactor: flip far_end/predicate layers to 26.2 base, dissolve 26_2 overlay"
```

---

### Task 4: Import upstream overlay_26_1 worldgen subset

**Files:**
- Create in `26_1/`: exactly these 10 files from `$ORIG/overlay_26_1/data/`:

```
stellarity/worldgen/configured_feature/the_hallow/large_lake.json
stellarity/worldgen/configured_feature/the_hallow/crystals.json
stellarity/worldgen/configured_feature/prismatic_dunes/rare_grass_patch.json
stellarity/worldgen/configured_feature/prismatic_dunes/prismatic_cacti.json
stellarity/worldgen/configured_feature/hallowed_tundra/large_lake.json
stellarity/worldgen/configured_feature/frozen_spikes/replace_dripstone.json
stellarity/worldgen/configured_feature/frozen_spikes/large_dripstone.json
stellarity/worldgen/configured_feature/frozen_spikes/ice_spikes.json
stellarity/worldgen/configured_feature/end_midlands/obsidian_spike.json
stellarity/worldgen/configured_feature/crystal_crags/large_crystals.json
```

Do NOT copy `overlay_26_1`'s loot tables (`magma_cube.json`, `pixie.json` — full-pack mob content), advancements, enchantments, predicates, functions, or tags.

**Interfaces:**
- Produces: `26_1/` carrying the 26.1-format worldgen fixes for formats 94–101.

- [ ] **Step 1: Copy the 10 files**

```bash
cd "$LITE"
for f in \
  stellarity/worldgen/configured_feature/the_hallow/large_lake.json \
  stellarity/worldgen/configured_feature/the_hallow/crystals.json \
  stellarity/worldgen/configured_feature/prismatic_dunes/rare_grass_patch.json \
  stellarity/worldgen/configured_feature/prismatic_dunes/prismatic_cacti.json \
  stellarity/worldgen/configured_feature/hallowed_tundra/large_lake.json \
  stellarity/worldgen/configured_feature/frozen_spikes/replace_dripstone.json \
  stellarity/worldgen/configured_feature/frozen_spikes/large_dripstone.json \
  stellarity/worldgen/configured_feature/frozen_spikes/ice_spikes.json \
  stellarity/worldgen/configured_feature/end_midlands/obsidian_spike.json \
  stellarity/worldgen/configured_feature/crystal_crags/large_crystals.json; do
  mkdir -p "26_1/data/$(dirname $f)"
  cp "$ORIG/overlay_26_1/data/$f" "26_1/data/$f"
done
```

- [ ] **Step 2: Verify**

```bash
find 26_1 -name '*.json' | wc -l    # expect 15 (10 upstream CF + 4 far_end + 1 predicate)
python3 -c "
import json,glob
[json.load(open(f)) for f in glob.glob('26_1/**/*.json',recursive=True)]
print('26_1 JSON OK')"
```

- [ ] **Step 3: Commit**

```bash
git add 26_1 && git commit -m "feat: 26_1 overlay with upstream 26.1-format worldgen fixes"
```

---

### Task 5: Rebuild 1_21_11 overlay + final pack.mcmeta

Replace the 1676-file full-copy overlay with: upstream `overlay_1_21_11` (202 files, all worldgen/dimension_type/block-tags) + only those of our old overlay's OTHER files that actually differ from the new base.

**Interfaces:**
- Consumes: new base from Tasks 2–3; `$ORIG/overlay_1_21_11/data`; old overlay preserved at `$SCRATCH/old_1_21_11`.
- Produces: slim `1_21_11/` (~250–300 files); final pack.mcmeta with overlays `[26_1 (94–101), 1_21_11 (94–94)]` — order matters, `1_21_11` listed LAST so it wins at format 94.

- [ ] **Step 1: Stash the old overlay outside the repo**

```bash
cd "$LITE"
SCRATCH=$(dirname "$ORIG")/..   # the session scratchpad dir
mv 1_21_11 "$SCRATCH/old_1_21_11"
```

- [ ] **Step 2: Seed the new overlay with upstream's**

```bash
mkdir 1_21_11
cp -r "$ORIG/overlay_1_21_11/data" 1_21_11/data
find 1_21_11 -type f | wc -l   # expect 202
```

- [ ] **Step 3: Prune-merge the rest of our old overlay**

Rules: skip old-overlay files under `data/minecraft/dimension*`, `data/minecraft/worldgen/`, `data/stellarity/worldgen/` (upstream overlay + new base own those now — but NOT `data/far_end/**`, which upstream doesn't have and we keep). Never overwrite a file Step 2 already placed. Otherwise keep a file only if it differs from the new base (json-compare for .json, byte-compare otherwise).

```bash
SCRATCH=/tmp/claude-1000/-mnt-c-Users-narko-Desktop-CATCRAFT-stellarity-lite/4f6f1e9d-8d1f-44a6-b98f-14e4d4f0d3e8/scratchpad
python3 - "$SCRATCH/old_1_21_11" <<'EOF'
import json, os, sys, filecmp, shutil
old_root = sys.argv[1]
SKIP_PREFIXES = ('data/minecraft/dimension', 'data/minecraft/worldgen/', 'data/stellarity/worldgen/')
kept, dropped, skipped = 0, 0, 0
for dirpath, _, files in os.walk(old_root):
    for name in files:
        src = os.path.join(dirpath, name)
        rel = os.path.relpath(src, old_root)          # e.g. data/stellarity/function/foo.mcfunction
        if rel.replace(os.sep, '/').startswith(SKIP_PREFIXES):
            skipped += 1; continue
        dst = os.path.join('1_21_11', rel)
        if os.path.exists(dst):                        # upstream overlay already provides it
            skipped += 1; continue
        base = rel                                      # same rel path against repo base layer
        same = False
        if os.path.exists(base):
            if base.endswith('.json'):
                try:
                    same = json.load(open(src)) == json.load(open(base))
                except Exception:
                    same = False
            else:
                same = filecmp.cmp(src, base, shallow=False)
        if same:
            dropped += 1
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            kept += 1
print(f'kept={kept} dropped={dropped} skipped={skipped}')
EOF
```

Report the three counts in the task summary. Sanity: kept should be roughly 30–150 (functions with snake_case gamerules, far_end worldgen, a few loot/predicate diffs); if kept > 400, STOP and report — the prune is not working.

- [ ] **Step 4: Final pack.mcmeta**

```bash
python3 - <<'EOF'
import json
m=json.load(open('pack.mcmeta'))
def entry(d, lo, hi):
    return {"directory": d,
            "formats": {"min_inclusive": lo, "max_inclusive": hi},
            "min_format": lo, "max_format": hi}
m['overlays']['entries']=[entry('26_1',94,101), entry('1_21_11',94,94)]
json.dump(m,open('pack.mcmeta','w'),indent='\t')
EOF
python3 -c "import json; e=json.load(open('pack.mcmeta'))['overlays']['entries']; assert [x['directory'] for x in e]==['26_1','1_21_11']; print('mcmeta OK')"
```

- [ ] **Step 5: Verify overlay JSON parses**

```bash
python3 -c "
import json,glob
files=glob.glob('1_21_11/**/*.json',recursive=True)
[json.load(open(f)) for f in files]
print('1_21_11 JSON OK', len(files))"
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "refactor: slim 1_21_11 overlay to true diff, mirror upstream layout"
```

---

### Task 6: floating_treasure — structure, NBT, maps, Lite loot

**Files:**
- Already in base since Task 2: `data/stellarity/worldgen/structure/floating_treasure.json`, `worldgen/structure_set/floating_treasure.json`, `worldgen/template_pool/floating_treasure.json`.
- Create (copy from ORIG base): `data/stellarity/structure/floating_treasure.nbt`, `data/stellarity/tags/worldgen/structure/exploration_map/floating_treasure.json`, `data/stellarity/loot_table/item/explorer_map/floating_treasure.json`
- Overwrite from ORIG base: `data/stellarity/loot_table/shipwreck/maps.json`
- Create (write, do not copy): `data/stellarity/loot_table/floating_treasure.json` and `26_1/data/stellarity/loot_table/floating_treasure.json`

**Interfaces:**
- Consumes: `$ORIG/data/stellarity/loot_table/floating_treasure.json` (pool index 2 = diamond gear pool, reused verbatim).
- Produces: `stellarity:floating_treasure` loot table resolvable on all supported versions; explorer maps to the structure in shipwreck loot.

- [ ] **Step 1: Copy the four upstream files**

```bash
cd "$LITE"
cp "$ORIG/data/stellarity/structure/floating_treasure.nbt" data/stellarity/structure/
mkdir -p data/stellarity/tags/worldgen/structure/exploration_map data/stellarity/loot_table/item/explorer_map
cp "$ORIG/data/stellarity/tags/worldgen/structure/exploration_map/floating_treasure.json" data/stellarity/tags/worldgen/structure/exploration_map/
cp "$ORIG/data/stellarity/loot_table/item/explorer_map/floating_treasure.json" data/stellarity/loot_table/item/explorer_map/
cp "$ORIG/data/stellarity/loot_table/shipwreck/maps.json" data/stellarity/loot_table/shipwreck/maps.json
```

- [ ] **Step 2: Verify the copied files reference nothing missing**

```bash
grep -o 'stellarity:[a-z_/]*' data/stellarity/loot_table/shipwreck/maps.json data/stellarity/loot_table/item/explorer_map/floating_treasure.json | sort -u
```

Expected refs: `stellarity:item/explorer_map/floating_treasure` (exists after Step 1), `stellarity:exploration_map/floating_treasure` (the tag, exists after Step 1). If anything else stellarity-namespaced appears (an item/loot ref that does not exist under `data/stellarity/`), STOP and report.

- [ ] **Step 3: Generate both loot table variants**

```bash
export ORIG=/tmp/claude-1000/-mnt-c-Users-narko-Desktop-CATCRAFT-stellarity-lite/4f6f1e9d-8d1f-44a6-b98f-14e4d4f0d3e8/scratchpad/stellarity-orig/datapack
python3 - <<'EOF'
import json, os, copy
ORIG = os.environ['ORIG']
src = json.load(open(f"{ORIG}/data/stellarity/loot_table/floating_treasure.json"))
diamond_pool = src['pools'][2]          # verbatim upstream: one random diamond item incl. diamond_spear

def item(name, cmin=None, cmax=None, funcs=None):
    e = {"type": "minecraft:item", "weight": 1, "name": f"minecraft:{name}"}
    f = list(funcs or [])
    if cmin is not None:
        f.append({"function": "minecraft:set_count",
                  "count": cmin if cmin == cmax else {"min": cmin, "max": cmax}})
    if f: e["functions"] = f
    return e

def book(ench, lvl):
    return item("enchanted_book", funcs=[
        {"function": "minecraft:set_enchantments", "enchantments": {f"minecraft:{ench}": lvl}}])

books = [book("mending",1), book("unbreaking",3), book("efficiency",4),
         book("protection",4), book("feather_falling",4), book("frost_walker",2)]
key   = [item("ominous_trial_key")]
mix   = [
    item("netherite_scrap"),                          # exactly 1 - user requirement
    item("gold_ingot", 4, 8),
    item("potion", funcs=[{"function": "minecraft:set_potion", "id": "minecraft:luck"}]),
    item("ender_eye", 1, 2),
    item("pufferfish", 1, 3),
    item("golden_carrot", 3, 7),
    item("ochre_froglight", 2, 8),
    item("purpur_block", 6, 12),
    item("purpur_pillar", 4, 8),
    item("end_crystal"),
    item("chorus_fruit", 4, 10),
    item("ender_pearl", 1, 4),
]
out = copy.deepcopy(src)                # keeps type/random_sequence if upstream has them
out['pools'] = [
    {"rolls": 1, "entries": books},
    {"rolls": 1, "entries": key},
    diamond_pool,
    {"rolls": 8, "entries": mix},
]
json.dump(out, open('data/stellarity/loot_table/floating_treasure.json','w'), indent=2)

no_spear = copy.deepcopy(out)           # 26_1 variant: diamond_spear does not exist before 26.2
no_spear['pools'][2]['entries'] = [
    e for e in no_spear['pools'][2]['entries']
    if 'spear' not in json.dumps(e)]
os.makedirs('26_1/data/stellarity/loot_table', exist_ok=True)
json.dump(no_spear, open('26_1/data/stellarity/loot_table/floating_treasure.json','w'), indent=2)
print('base entries pool2:', len(out['pools'][2]['entries']),
      '| 26_1 pool2:', len(no_spear['pools'][2]['entries']))
EOF
```

Expected output: `base entries pool2: 10 | 26_1 pool2: 9`.

- [ ] **Step 4: Verify no full-pack refs remain**

```bash
grep -c 'stellarity:item\|stellarity:void_fishing\|stellarity:block\|gilded' data/stellarity/loot_table/floating_treasure.json 26_1/data/stellarity/loot_table/floating_treasure.json
# expect 0 for both files
```

- [ ] **Step 5: NBT drift report (report only, no copying)**

List upstream structure NBTs that differ from ours, so the PM can decide on a follow-up. Do NOT copy anything beyond floating_treasure.nbt:

```bash
for f in "$ORIG"/data/stellarity/structure/*.nbt "$ORIG"/data/stellarity/structure/**/*.nbt; do
  rel=${f#"$ORIG"/data/stellarity/structure/}
  ours="data/stellarity/structure/$rel"
  if [ ! -f "$ours" ]; then echo "MISSING-IN-LITE: $rel";
  elif ! cmp -s "$f" "$ours"; then echo "DIFFERS: $rel"; fi
done | sort | head -40
```

Include the list in the task summary verbatim.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: floating_treasure structure with Lite-ified loot"
```

---

### Task 7: Static validation gate

**Files:** none created (scratch script only). This is the pre-server sanity gate.

**Interfaces:**
- Consumes: final repo state from Tasks 1–6.
- Produces: PASS/FAIL digest; blocks Task 8 on FAIL.

- [ ] **Step 1: Full JSON parse of every layer**

```bash
python3 -c "
import json,glob
fails=[]
for root in ('data','26_1','1_21_11'):
    for f in glob.glob(root+'/**/*.json',recursive=True):
        try: json.load(open(f))
        except Exception as e: fails.append((f,str(e)[:60]))
print(fails if fails else 'PARSE OK')"
```

- [ ] **Step 2: Reference integrity for the new content**

```bash
python3 - <<'EOF'
import json, os
errs = []
# floating_treasure chain
st = json.load(open('data/stellarity/worldgen/structure/floating_treasure.json'))
assert st['start_pool'].startswith('stellarity:'), st['start_pool']
tp = json.load(open('data/stellarity/worldgen/template_pool/floating_treasure.json'))
for el in tp['elements']:
    loc = el['element'].get('location','')
    if loc and not os.path.exists(f"data/stellarity/structure/{loc.split(':')[1]}.nbt"):
        errs.append(f"missing NBT {loc}")
# every biome's placed features exist (base layer)
for b in os.listdir('data/stellarity/worldgen/biome'):
    biome = json.load(open(f'data/stellarity/worldgen/biome/{b}'))
    for step in biome.get('features', []):
        for pf in step:
            ns, path = pf.split(':')
            if ns in ('stellarity','minecraft','far_end'):
                p = f"data/{ns}/worldgen/placed_feature/{path}.json"
                if ns == 'minecraft' and not os.path.exists(p):
                    continue  # vanilla-provided placed features are fine
                if ns != 'minecraft' and not os.path.exists(p):
                    errs.append(f"{b}: missing {pf}")
print(errs if errs else 'REFS OK')
EOF
```

- [ ] **Step 3: the_void really gone from dimension, still defined as biome**

```bash
grep -c the_void data/minecraft/dimension/the_end.json          # expect 0
ls data/stellarity/worldgen/biome/the_void.json                  # exists (harmless orphan, mirrors upstream)
```

- [ ] **Step 4: Commit nothing; report digest**

No commit (no file changes). Report PARSE/REFS results and any anomalies.

---

### Task 8: AGENTS.md + Codex server tests

**Files:**
- Create: `AGENTS.md` (repo root)
- Output artifact: `_servers/last_test_report.md` (written by Codex, not committed)

**Interfaces:**
- Consumes: validated repo from Task 7; `_servers/{1.21.11,26.1.2,26.2}` server dirs, bundled JDK `_servers/jdk-25.0.3+9`, `_servers/rcon.py`.
- Produces: committed AGENTS.md; test report digest. Failures loop back as fix tasks (Sonnet), then rerun.

- [ ] **Step 1: Write AGENTS.md**

```markdown
# AGENTS.md — Stellarity Lite test protocol

Stellarity: Lite is a Minecraft datapack (worldgen-only End overhaul). You are the test runner.
Do not modify pack files. Your deliverable is ONE file: `_servers/last_test_report.md`.

## Test servers
`_servers/<version>/` for versions: `1.21.11`, `26.1.2`, `26.2`. Java: `_servers/jdk-25.0.3+9/bin/java`.
RCON helper: `_servers/rcon.py` — read it first to learn its CLI.

## Per-server procedure
1. Install pack: copy repo root (only `pack.mcmeta`, `pack.png`, `data/`, `26_1/`, `1_21_11/`) into
   `<server>/world/datapacks/stellarity_lite/`. Delete any stale copy first. Delete the server's old
   `world/DIM1` (End dimension) so the End regenerates.
2. Start: `cd _servers/<version> && ../jdk-25.0.3+9/bin/java -Xmx2G -jar server*.jar nogui`,
   wait for "Done" in log (timeout 5 min).
3. Checks (via rcon + `logs/latest.log`):
   a. Log has NO lines matching `Couldn't parse|Failed to load|error loading|Missing` for
      namespaces stellarity/far_end/minecraft worldgen or loot tables. Vanilla unrelated warnings are OK.
   b. `execute in minecraft:the_end run locate structure stellarity:floating_treasure` — found.
   c. Same for `minecraft:stronghold` and `minecraft:end_city` (both overridden by the pack).
   d. `execute in minecraft:the_end positioned 0 100 0 run locate biome stellarity:dragons_den` — found near 0,0.
   e. Height: `execute in minecraft:the_end run setblock 100 300 100 minecraft:stone` succeeds
      (would fail with "out of world" on a 256-height End).
   f. `loot spawn 100 301 100 loot stellarity:floating_treasure` — no error in response/log.
4. Stop server (`stop` via rcon), free the port before the next one.

## Report format (`_servers/last_test_report.md`)
Max 60 lines total. Per server: `## <version> — PASS|FAIL`, then only failed checks with <=5-line
log excerpts. End with a one-line overall verdict. No full logs, no play-by-play.
```

Write exactly this content (fenced block above) to `AGENTS.md`.

- [ ] **Step 2: Commit AGENTS.md**

```bash
git add AGENTS.md && git commit -m "docs: AGENTS.md test protocol for Codex runs"
```

- [ ] **Step 3: Run Codex (PM runs this — one command)**

```bash
cd "$LITE" && codex exec --full-auto "Follow AGENTS.md: run the full test protocol for all three servers and write _servers/last_test_report.md" 
```

Timeout: allow up to 30 min (three server boots). Run in background and poll the report file.

- [ ] **Step 4: Read the report, triage**

Read `_servers/last_test_report.md`. PASS on all three → done. Any FAIL → PM turns each failure into a fix task for a Sonnet subagent, then re-run Step 3 (Codex can be told to re-test only the failed server).

---

### Task 9: Documentation update

**Files:**
- Modify: `CLAUDE.md` (Version Compatibility section, Key Files section)
- Modify: `_docs/pack-format-versions.md` (overlay table)

**Interfaces:**
- Consumes: final layer layout from Tasks 1–5.
- Produces: docs matching reality.

- [ ] **Step 1: CLAUDE.md — Version Compatibility section**

Replace the section body with:

```markdown
The pack targets 1.21.11+ via the overlay system:

- **Base layer** (`data/`) — 26.2 worldgen formats (pack_format 107+), mirrors upstream base
- **`26_1/data/`** — overlay for formats `94–101` (1.21.11 + 26.1): 26.1-format worldgen fixes
- **`1_21_11/data/`** — overlay for format `94` only (1.21.11), listed AFTER `26_1` so it wins on overlap

`pack.mcmeta`: `min_format: 94`, `max_format: 108`. Worldgen layers mirror upstream
(Prismatic-Shards/Stellarity `datapack/`): base = their base, our overlays = worldgen subset of
their `overlay_26_1`/`overlay_1_21_11`. To sync with a new upstream release: diff their datapack
against ours, copy changed worldgen files per layer.
```

Also fix in Key Files: `data/minecraft/worldgen/noise_settings/the_end.json` → `data/minecraft/worldgen/noise_settings/end.json`, and add `AGENTS.md — Codex test protocol` to the docs list.

- [ ] **Step 2: _docs/pack-format-versions.md**

Update the overlay table to the three-layer scheme above (keep the format↔version table and the stacking-order note — the note's example changes from `1_21_7`/`1_21_9` to `26_1`/`1_21_11`). Add a line: "pre-1.21.11 support dropped 2026-07; last supporting commit tagged in git history."

- [ ] **Step 3: Verify + commit**

```bash
grep -c '1_21_9' CLAUDE.md _docs/pack-format-versions.md   # expect 0 in CLAUDE.md; _docs may keep one historical mention
git add CLAUDE.md _docs/pack-format-versions.md && git commit -m "docs: update layer scheme after upstream port"
```

---

## Self-Review Notes

- Spec §1→Task 1+5, §2→Tasks 2,4,5, §3→Task 3, §4→Task 6, §5→Tasks 2,7, §7→Task 8, §8→Task 9. Covered.
- Deviation from spec §4: upstream's `overlay_26_1` loot files turned out to be mob loot (magma_cube, pixie), NOT a no-spear floating_treasure — upstream did not solve diamond_spear on <26.2. We solve it ourselves with the `26_1` loot variant (Task 6 Step 3). Outcome matches spec's table anyway.
- Old `1_21_11` overlay survives at `$SCRATCH/old_1_21_11` until session end; recoverable from git history after.
