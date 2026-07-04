# Pack Format Versions

Reference for Minecraft Java Edition data pack formats used by Stellarity Lite.

## Format → Version Table

| pack_format | Minecraft Version |
|---|---|
| 48 | 1.21 – 1.21.1 |
| 57 | 1.21.2 – 1.21.3 |
| 61 | 1.21.4 |
| 71 | 1.21.5 |
| 80 | 1.21.6 |
| 81 | 1.21.7 – 1.21.8 |
| 88.0 | 1.21.9 – 1.21.10 |
| 94.1 | 1.21.11 |
| 101.1 | 26.1 – 26.1.2 |
| 107.1 | 26.2 |

Starting with 1.21.9, pack formats use a decimal minor version. Non-breaking changes increment the minor; breaking changes increment the major.

## Current pack.mcmeta

- **pack_format**: 107.1 (26.2, current target)
- **min_format**: 81 (1.21.7)
- **max_format**: 108
- **supported_formats**: `[81, 108]`
- **Overlay `1_21_9/`**: formats 81–88 (1.21.7 – 1.21.10) — full copy, pre-1.21.11 formats
- **Overlay `1_21_7/`**: format 81 only (1.21.7 – 1.21.8) — 6-file patch stacked ON TOP of `1_21_9/` (listed after it in pack.mcmeta, see "Overlay System"); reverts two 1.21.9 renames, see "1.21.9 Breaking Changes"
- **Overlay `1_21_11/`**: formats 89–100 (1.21.11) — full copy, tested clean on Paper 1.21.11
- **Overlay `26_2/`**: formats 107–108 (26.2+) — `dimension_type` (adds `default_clock`) + 83 generated configured_feature copies + 1 predicate (see "26.2 Breaking Changes" below); tested clean on vanilla 26.2
- **Base `data/`**: serves 26.1.x (format 101.1) directly; tested on Paper 26.1.2

The old full-copy `26_2/` tree (stale, pre-random_patch-migration) is archived at `_old/26_2_full_copy_data/`.

## pack.mcmeta Overlay Syntax — DUAL SYNTAX REQUIRED

**≤1.21.8 (format ≤81) uses a different overlay-entry schema**: it requires the `formats` key (`{"min_inclusive": N, "max_inclusive": M}`) and fails with `Couldn't load overlays metadata: No key formats` on the 1.21.9+ `min_format`/`max_format` keys. When that happens **no overlays apply at all** and old versions read the raw base — hundreds of misleading downstream errors. Both parsers ignore each other's keys, so every overlay entry in this pack carries BOTH syntaxes (wiki explicitly sanctions this for backward-compat packs). Same idea as keeping `pack_format`+`supported_formats` alongside `min_format`/`max_format` in the `pack` section.

**Stacking order**: overlays are applied in list order, the first applied first — so a LATER entry overrides an earlier one for the same file. `1_21_7` is listed after `1_21_9` and wins for format 81.

## 1.21.9 Breaking Changes (reverted for 1.21.7–1.21.8 in `1_21_7/` overlay)

Renames introduced in 1.21.9 — the `1_21_9/` overlay content uses the NEW names (correct for 1.21.9–1.21.10), so format 81 needs the small `1_21_7/` patch overlay with the OLD names:
- Block `minecraft:chain` → `minecraft:iron_chain`. Affects: `minecraft:climbable` + `stellarity:_worldgen/frozen_spikes/everything_but_dripstone` block tags, `the_hallow/lanterns` configured feature, `post_gen/end_city/{top_tower,base_roof}/chains` mcfunctions (setblock/fill commands).
- Noise router field `initial_density_without_jaggedness` → `preliminary_surface_level` (value unchanged: `stellarity:initial_density`). `1_21_7/`'s `noise_settings/end.json` carries **both** keys — each version ignores the unknown one.

## 1.21.11 Breaking Changes (fixed in `1_21_11/` + `26_2/` overlays)

**Game rules renamed** (25w44a): all game rules moved into a registry and renamed from camelCase to snake_case resource locations. `globalSoundEvents` → `global_sound_events`. Affects `stellarity/function/sfx/end_portal/open_animation/finish.mcfunction` (the only gamerule usage in the pack). The `1_21_9/` overlay keeps camelCase (correct for ≤1.21.10).

Also in 1.21.11: `doFireTick`/`allowFireTicksAwayFromPlayer` removed, replaced by `minecraft:fire_spread_radius_around_player` (not used by this pack).

## Vanilla Exit Portal Duplication Bug (fixed)

**Symptom**: vanilla bedrock fountain spawns on top of / next to the custom exit portal.

**Mechanism** (verified via `EnderDragonFight` bytecode of 26.1.2 + live server experiments):
- The custom exit portal + its `Exit Portal` marker come from **worldgen** (structure NBT), not from the crystal-trigger in `far_end:structures/replace/exit_portal` (that trigger never fires on modern versions — the vanilla podium spawns without any crystal).
- When a player enters the End, the vanilla dragon fight runs `scanState()` → `findExitPortal()` (block-pattern scan). The custom portal doesn't match the vanilla pattern → `spawnExitPortal()` places the vanilla podium at the **heightmap top of (0,0)** and spawns a vanilla dragon. The same re-placement happens on dragon death (`setDragonKilled`) and on crystal-respawn scans (`tryRespawn`). The pack's butcher already cleans vanilla gateways but never cleaned the podium.

**Fix**:
- **26.x (base + `26_2/`)**: `has_ender_dragon_fight: false` in `dimension_type` (field added 26.1 snap3) — vanilla fight, podium, vanilla dragon and vanilla gateways never exist. The pack is self-sufficient: it summons its own dragon (`stellarity:mobs/dragon/spawn/summon` via the crystal ritual) and manages its own gateways.
- **`1_21_9/` + `1_21_11/`** (field unavailable): every-tick check appended to `far_end:structures/exit_portal/main` — if a bedrock block sits at the heightmap top of (0,0) **9+ blocks away from the marker** (custom portal contains bedrock too — the distance guard protects it), `far_end:structures/exit_portal/podium_cleanup` erases the podium (egg/torches first to avoid item drops, then end_portal, then bedrock).

## Java Requirements

- MC ≤1.21.11 servers: Java 21+ (works on Windows `jdk-24` at `C:\Program Files\Java\jdk-24`)
- MC 26.1+ servers: **Java 25+** (Temurin 25 unpacked at `_servers/jdk-25.0.3+9/`)

## Server Test Harness (`_servers/`)

`python3 _servers/test.py <1.21.8|1.21.11|26.1.2|26.2>` — builds the datapack zip, wipes the world, boots the server (Windows `java.exe` from WSL, `-Xmx2G`), waits for "Done", forceloads End chunk (0,0) via RCON, stops gracefully, prints a deduplicated error summary (stack traces stripped). Full log: `_servers/<ver>/server.log`. Server cores: Paper for 1.21.8/1.21.11/26.1.2 (download more via `https://fill.papermc.io/v3/projects/paper/versions/<ver>/builds/latest`), vanilla `server.jar` for 26.2 (its inner jar is extracted to `_servers/26.2/ref/server-26.2.jar` — grep it for ground-truth worldgen/advancement formats). Tests bind fixed ports — run sequentially, never in parallel.

## Adding a New Version

1. Check the wiki for the new version's `pack_format`.
2. If the format requires file changes (e.g. JSON schema change): create a new overlay directory (e.g. `1_22_x/`) with only the changed files, then add an entry to `pack.mcmeta` `overlays.entries`.
3. If no file changes are needed: just update `pack_format`, `max_format`, and `supported_formats` in `pack.mcmeta`.
4. Always check `_docs/dimension-type-format.md` and `_docs/structure-format.md` for known schema breaks.

## Overlay System

Overlays override base-layer files for specific format ranges. The base `data/` folder is the default and should target the **latest** Minecraft version. Older versions that need different files get overlays.

Current overlays:
- `1_21_9/` — formats 81–88 (1.21.7 – 1.21.10); full copy with pre-1.21.11 formats (camelCase gamerules, old `dimension_type`).
- `1_21_7/` — format 81 only (1.21.7 – 1.21.8); 6-file patch listed AFTER `1_21_9` so it stacks on top: chain/iron_chain + noise router key renames (see "1.21.9 Breaking Changes").
- `1_21_11/` — formats 89–100 (1.21.11); full copy with snake_case gamerules and 1.21.11 `dimension_type`.
- `26_2/` — formats 107–108 (26.2+); only `dimension_type` (adds `default_clock`). All other 26.x migrations (forest_rock → block_blob, random_patch removal, entity predicate format) live in the base layer, which 26.1.x loads directly.

The `_old/` directory holds retired overlays (not active in pack.mcmeta) kept for historical reference.

## 26.1.2 Breaking Changes (fixed in base layer)

The following types were **removed** in 26.1 and must not appear in base-layer configured_feature files:
- `minecraft:random_patch` — replace with inner feature in CF; move `tries` → `count` modifier and `xz_spread`/`y_spread` → `random_offset` modifier in placed_feature
- `minecraft:flower` — same migration as `random_patch`

The following types were **renamed or modified** in 26.1:
- `minecraft:forest_rock` → `minecraft:block_blob`, now requires `can_place_on` block predicate — converted in base with `"can_place_on": {"type": "minecraft:true"}` (preserves old unrestricted behavior). 8 usages across 6 files (tuff, oasis rocks ×2, end_midlands/rocks, the_hallow/rock, warped_marsh/slime).
- `#minecraft:concrete_powders` block tag does **not exist yet** in 26.1.2 — in ≤26.1 the vanilla tag is the **singular** `#minecraft:concrete_powder`; 26.2 renamed it to the plural. `stellarity:dune_speed_procs_speed_bonus` inlines the 16 concrete powder block ids instead, which works on every version.
- `minecraft:time_check` loot condition: **required `clock` field added** (26.1 snap3, clocks/timelines system). Built-in world clocks in 26.1.2 are **`minecraft:overworld` and `minecraft:the_end` only** (verified via `WorldClocks.class` in the vanilla jar — the wiki's `minecraft:day` example does NOT exist in 26.1.2/26.2; the 26.2 `default_clock` uses `minecraft:the_end`). Affected: `stellarity:predicate/mobs/eol/is_daytime.json`, `wings_is_daytime.json` → `"clock": "minecraft:overworld"` (old format kept in `1_21_9/` and `1_21_11/` overlays).
- `minecraft:huge_red_mushroom` — now requires `can_place_on` block predicate in config
- `minecraft:disk` with rule-based `state_provider` — now requires explicit `"type": "minecraft:rule_based"` field

New required field in `dimension_type`:
- `has_ender_dragon_fight: true` (or false) — added in 26.1.2

New `attributes` entries that must be added explicitly (no-attribute default is `#000000`, i.e. no ambient light):
- `minecraft:visual/ambient_light_color: "#3f473f"` — End's ambient tint; default is `#000000` (black = no ambient light), so omitting it causes total darkness
- `minecraft:visual/block_light_tint` — defaults to `#FFD88C` (warm yellow) across all dimensions; no End-specific override needed
- `minecraft:visual/night_vision_color` — defaults to `#999999`; no End-specific override needed

## 26.2 Breaking Changes (handled via `26_2/` overlay)

Base `data/` keeps the 26.1 formats; every file that breaks on 26.2 gets a converted copy in `26_2/`. The copies are **generated** by `_servers/migrate_26_2.py` — after editing base configured_features, re-run it to regenerate the overlay. All conversions were verified against the vanilla 26.2 jar's own worldgen JSONs (`_servers/26.2/ref/server-26.2.jar`, extracted from the bundler `server.jar`), because the wiki does not document several of them.

**`minecraft:tree` configured features (86 configs, the big one — NOT on the wiki):**
- `dirt_provider` + `force_dirt` are replaced by required **`below_trunk_provider`** (a BlockStateProvider)
- Conversion: `force_dirt: true` → the old dirt_provider used directly (vanilla `azalea_tree.json` pattern); `force_dirt: false`/absent → dirt_provider wrapped in `minecraft:rule_based_state_provider` with `if_true: not(#minecraft:cannot_replace_below_tree_trunk)` (vanilla `oak.json` pattern)

**`minecraft:root_system`** (5 configs): new required `level_test_distance` and `max_level_deviation` — vanilla uses `0` for both (behavior-preserving).

**`minecraft:lake`** (2 configs): new required block predicates `can_place_feature`, `can_replace_with_air_or_fluid`, `can_replace_with_barrier` — copied vanilla `lake_lava.json` defaults (`true`, `not(#features_cannot_replace)`, `not(#lava_pool_stone_cannot_replace)`).

**`minecraft:large_dripstone`** (1 config): `replaceable_blocks` (optional in 26.1) is now **required** — set to the old default `#minecraft:dripstone_replaceable_blocks`.

**Tag renamed**: `#minecraft:concrete_powder` → `#minecraft:concrete_powders` (26.2 snap3). Affected `prismatic_dunes/rare_grass_patch.json` (`replaceable` field).

**Missing tag references are now hard errors**: in ≤26.1 a block predicate referencing a nonexistent block tag loaded silently; 26.2 fails registry loading with `Missing tag`. This exposed a latent pack bug: `far_end:amethyst/vegetation/hanging_amethyst` referenced `#stellarity:amethyst_forest/diorite_and_calcite`, which never existed. Fixed by creating the tag in **base** (`diorite` + `calcite`) — on ≤26.1 this also makes the hanging-amethyst feature actually work as intended.

**Entity predicate format** (changed in 26.2 snap3):
- Every top-level key in an entity predicate is now a namespaced component id; fields *inside* a component stay bare
- `type_specific` with `"type": "<entity_type>"` → component key `"minecraft:type_specific/<type>"`; `type` → `minecraft:entity_type`; unknown keys are now **rejected** (previously ignored)
- Bare legacy keys like `nbt`, `flags`, `distance` keep working (they resolve into the `minecraft:` namespace)
- Affected file: `stellarity/predicate/items/spirit_dagger/looking_at_spirit.json` (overridden in `26_2/`); vanilla reference: `advancement/adventure/spyglass_at_parrot.json` in the 26.2 jar

**Other 26.2 changes not affecting this pack:**
- `minecraft:pointed_dripstone` → `minecraft:speleothem`, `minecraft:dripstone_cluster` → `minecraft:speleothem_cluster` (features not used; the pointed_dripstone *block* id is unchanged)
- `minecraft:weird_scaled_sampler` density function removed, replaced by `interval_select` (not used)
- `noise_gradient` surface rule removed (not used)
- Team/waypoint color arguments strictly `lowercase_with_underscores` (pack already complies)
