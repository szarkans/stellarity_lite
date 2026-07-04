# Dimension Type Format Changes

The `dimension_type` JSON schema changed significantly between 1.21.10 and 1.21.11.

## Pre-1.21.11 Format (formats ≤ 88 — used in `1_21_9/` overlay)

Fields at top level:
```json
{
  "ambient_light": 0.25,
  "bed_works": false,
  "coordinate_scale": 1,
  "effects": "minecraft:the_end",
  "fixed_time": 6000,
  "has_ceiling": false,
  "has_raids": true,
  "has_skylight": true,
  "height": 256,
  "infiniburn": "#minecraft:infiniburn_end",
  "logical_height": 256,
  "min_y": 0,
  "monster_spawn_block_light_limit": 0,
  "monster_spawn_light_level": 15,
  "natural": false,
  "piglin_safe": false,
  "respawn_anchor_works": false,
  "ultrawarm": false
}
```

## 1.21.11+ Format (formats ≥ 94.1 — used in base `data/` layer)

Many fields were moved into a new `attributes` map. The `effects` field was removed; replaced by `skybox` and `timelines`.

```json
{
  "ambient_light": 0.25,
  "attributes": {
    "minecraft:audio/ambient_sounds": { "mood": { ... } },
    "minecraft:audio/background_music": { "default": { ... } },
    "minecraft:gameplay/bed_rule": {
      "can_set_spawn": "never",
      "can_sleep": "never",
      "explodes": true
    },
    "minecraft:gameplay/respawn_anchor_works": false,
    "minecraft:visual/fog_color": "#181318",
    "minecraft:visual/sky_color": "#000000",
    "minecraft:visual/sky_light_color": "#e580ff",
    "minecraft:visual/sky_light_factor": 0.0
  },
  "coordinate_scale": 1.0,
  "has_ceiling": false,
  "has_fixed_time": true,
  "has_skylight": true,
  "height": 256,
  "infiniburn": "#minecraft:infiniburn_end",
  "logical_height": 256,
  "min_y": 0,
  "monster_spawn_block_light_limit": 0,
  "monster_spawn_light_level": 15,
  "skybox": "end",
  "timelines": "#minecraft:in_end"
}
```

### Migrated fields

| Old (≤88) | New (≥94.1) |
|---|---|
| `effects: "minecraft:the_end"` | `skybox: "end"` |
| `sky_color` (implicit via effects) | `attributes["minecraft:visual/sky_color"]` |
| `fog_color` (implicit via effects) | `attributes["minecraft:visual/fog_color"]` |
| `bed_works` | `attributes["minecraft:gameplay/bed_rule"]` |
| `respawn_anchor_works` | `attributes["minecraft:gameplay/respawn_anchor_works"]` |
| `ultrawarm` | split across multiple attributes |
| `piglin_safe` | `attributes["minecraft:gameplay/piglin_safe"]` |
| `has_raids` | `attributes["minecraft:gameplay/has_raids"]` |
| `natural` | removed / migrated |
| `fixed_time` | `has_fixed_time: true` + clock/timeline |

### Why the overlay exists

1.21.10 (format 88) loads `1_21_9/data/minecraft/dimension_type/the_end.json` (old format).
1.21.11+ (format ≥ 94.1) loads `data/minecraft/dimension_type/the_end.json` (new format).
Loading the new format in 1.21.10 causes: `Failed to parse … No key sky_color in MapLike[...]`.

## 26.1 Lighting Attributes

Three new visual attributes were added in 26.1:

| Attribute key | Default | End value | Notes |
|---|---|---|---|
| `minecraft:visual/ambient_light_color` | `#000000` | `#3f473f` | **Critical** — default is black, omitting causes total darkness in The End |
| `minecraft:visual/block_light_tint` | `#FFD88C` | (same) | Warm yellow tint on torchlight; no End-specific override needed |
| `minecraft:visual/night_vision_color` | `#999999` | (same) | Night Vision tint; no End-specific override needed |

`ambient_light_color` **must be set explicitly** in any custom End dimension_type targeting 26.1+, because the fallback is `#000000` (pure black), which zeroes out all ambient illumination.

The top-level `ambient_light: 0.25` field is still present and controls the light *level*, while `ambient_light_color` controls the *colour/tint* of that light. In 26.1, both are required for correct rendering.

## Biome `effects` field

As of 1.21.11, biome effects (fog_color, sky_color, water_color, music, etc.) can also be moved to `attributes`. However, the old `biome.effects.*` format remains accepted for backwards compatibility in 1.21.11 and 26.x. Stellarity biomes still use the old format — no migration needed until the old format is removed.
