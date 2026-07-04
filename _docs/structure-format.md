# Structure Format & Known Issues

## terrain_adaptation Values

Used in `data/stellarity/worldgen/structure/*.json`:

| Value | Effect |
|---|---|
| `"none"` | Structure pasted as-is, no terrain modification |
| `"beard_thin"` | Smooth terrain blend outward from structure bounding box |
| `"beard_box"` | Rectangular box carved from terrain below/around structure |
| `"bury"` | Structure buried into terrain (used for vanilla stronghold) |

## Current Structure Definitions

| Structure | Type | terrain_adaptation | Notes |
|---|---|---|---|
| campsite | jigsaw | beard_thin | |
| chapel_of_light | jigsaw | beard_thin | size 6, max_distance 80 |
| desert_ruin | jigsaw | none | Intentionally half-buried via start_height -3 |
| fishing_hut | jigsaw | beard_thin | |
| fossil | nether_fossil | beard_box | Underground, above_bottom 2 |
| obsidian_spike | jigsaw | beard_box | Heightmap: MOTION_BLOCKING_NO_LEAVES |
| old_stronghold | stronghold | bury | |
| return_gateway | jigsaw | none | Spawns floating at Y30–70 |
| village | jigsaw | beard_box | size 6, max_distance 116, heightmap OCEAN_FLOOR |

## Known Issue: "Hard Paste" Appearance in End Terrain (Issue #5)

**Symptom**: Large structures (especially village, chapel) appear hard-pasted — abrupt rectangular terrain cuts with no smooth blending into the floating End island terrain.

**Root cause**: `beard_box` adaptation carves a solid rectangular prism under the structure. On End floating islands (which are typically thin), this box cuts through the entire island and produces a harsh straight edge rather than a smooth gradient. This is a vanilla Minecraft limitation — `beard_box` was designed for solid overworld terrain.

**Workaround options** (none applied yet — requires in-game testing):
- Change village `terrain_adaptation` from `beard_box` to `beard_thin` — trades box-carve for smooth fade, may leave floating bits.
- Change village `project_start_to_heightmap` from `OCEAN_FLOOR` to `WORLD_SURFACE` — may improve anchor point in End terrain.
- Use a processor list to gradually replace blocks at structure edges with air (fades the structure into terrain).

Do **not** change `terrain_adaptation` without in-game testing — the visual difference is large and depends on the specific biome's terrain shape.
