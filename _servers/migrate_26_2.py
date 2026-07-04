#!/usr/bin/env python3
"""Generate 26_2/ overlay copies of base files that break on MC 26.2.

Conversions (verified against vanilla 26.2 jar data):
- tree: dirt_provider/force_dirt -> below_trunk_provider
    force_dirt true  -> bare provider (vanilla azalea_tree.json)
    force_dirt false -> rule_based wrapper with not(#cannot_replace_below_tree_trunk) (vanilla oak.json)
- root_system: + level_test_distance: 0, max_level_deviation: 0 (vanilla rooted_azalea_tree.json)
- lake: + can_place_feature / can_replace_with_air_or_fluid / can_replace_with_barrier (vanilla lake_lava.json)
- large_dripstone: + replaceable_blocks: #minecraft:dripstone_replaceable_blocks (old default, now required)
- "#minecraft:concrete_powder" -> "#minecraft:concrete_powders" (tag renamed in 26.2 snap3)
"""
import json
from pathlib import Path

ROOT = Path("/mnt/c/Users/narko/Desktop/CATCRAFT/stellarity_lite")
SRC = ROOT / "data"
DST = ROOT / "26_2" / "data"

NOT_TAG = lambda tag: {"type": "minecraft:not",
                       "predicate": {"type": "minecraft:matching_block_tag", "tag": tag}}

def fix_tree(cfg):
    if "dirt_provider" not in cfg:
        return False
    prov = cfg.pop("dirt_provider")
    force = cfg.pop("force_dirt", False)
    cfg["below_trunk_provider"] = prov if force else {
        "type": "minecraft:rule_based_state_provider",
        "rules": [{"if_true": NOT_TAG("minecraft:cannot_replace_below_tree_trunk"), "then": prov}],
    }
    return True

def walk(node):
    changed = False
    if isinstance(node, dict):
        cfg = node.get("config")
        if isinstance(cfg, dict):
            t = node.get("type")
            if t == "minecraft:tree":
                changed |= fix_tree(cfg)
            elif t == "minecraft:root_system" and "level_test_distance" not in cfg:
                cfg["level_test_distance"] = 0
                cfg["max_level_deviation"] = 0
                changed = True
            elif t == "minecraft:lake" and "can_place_feature" not in cfg:
                cfg["can_place_feature"] = {"type": "minecraft:true"}
                cfg["can_replace_with_air_or_fluid"] = NOT_TAG("minecraft:features_cannot_replace")
                cfg["can_replace_with_barrier"] = NOT_TAG("minecraft:lava_pool_stone_cannot_replace")
                changed = True
            elif t == "minecraft:large_dripstone" and "replaceable_blocks" not in cfg:
                cfg["replaceable_blocks"] = "#minecraft:dripstone_replaceable_blocks"
                changed = True
        for k, v in list(node.items()):
            if isinstance(v, (dict, list)):
                changed |= walk(v)
            elif v == "#minecraft:concrete_powder":
                node[k] = "#minecraft:concrete_powders"
                changed = True
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                changed |= walk(v)
            elif v == "#minecraft:concrete_powder":
                node[i] = "#minecraft:concrete_powders"
                changed = True
    return changed

count = 0
for f in sorted(SRC.rglob("*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    if walk(data):
        out = DST / f.relative_to(SRC)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        count += 1
        print(f.relative_to(ROOT))
print(f"--- {count} files written to 26_2/")
