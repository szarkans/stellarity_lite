# Erases the vanilla exit-portal podium that the vanilla dragon fight re-places
# at the heightmap top of (0,0) (fight init, dragon death, or crystal respawn scan).
# Executed positioned at the podium's top bedrock block, only when it is 9+ blocks
# away from the exit portal marker, so the custom portal (which also contains
# bedrock) is never touched.
# Removal order matters: egg and torches first so nothing pops off as an item drop.
fill ~-1 ~ ~-1 ~1 ~2 ~1 air replace minecraft:dragon_egg
fill ~-4 ~-4 ~-4 ~4 ~2 ~4 air replace minecraft:torch
fill ~-4 ~-4 ~-4 ~4 ~2 ~4 air replace minecraft:wall_torch
fill ~-4 ~-4 ~-4 ~4 ~2 ~4 air replace minecraft:end_portal
fill ~-4 ~-4 ~-4 ~4 ~2 ~4 air replace minecraft:bedrock
