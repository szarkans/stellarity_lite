### Scoreboard Details ###
# stellarity.dragon.times_killed - the number of times the dragon is killed ## Bound to the portal marker.
# #respawn_crystal_count stellarity.misc - number of respawn crystals on the podium ## Global scoreboard not bound to an entity.
# stellarity.dragon.respawn_animation_progress - timer for respawn animation ## Bound to the portal marker.

## Generation
# Generate the deactivated portal with ender dragon.
execute if entity @s[tag=fe.deactivated] run function far_end:structures/exit_portal/deactivated/animation_no_dragon
execute if entity @s[tag=fe.deactivated.spawn_dragon] run function far_end:structures/exit_portal/deactivated/animation

# Generate the activated portal once the dragon is killed.
execute if entity @p[predicate=stellarity:locations/dragons_den/in_main_area] if entity @s[tag=fe.activated] unless entity @e[type=minecraft:ender_dragon,tag=fe.mob,tag=fe.ender_dragon] run function far_end:structures/exit_portal/activated/animation

## Respawn stuff
# Count the number of respawn Crystals placed
execute unless entity @e[type=minecraft:ender_dragon] run function stellarity:mobs/dragon/spawn/conditions
# # Start the respawn animation
execute if entity @s[tag=fe.respawn] run function stellarity:mobs/dragon/spawn/animation

# Remove certain tags and add different ones once Dragon is dead
execute if entity @s[tag=fe.in_dragon_fight] unless entity @e[type=minecraft:ender_dragon,tag=fe.mob,tag=fe.ender_dragon,distance=..300] run function far_end:structures/exit_portal/dragon/presence

execute unless score @s[tag=!fe.in_dragon_fight] stellarity.dragon.times_killed matches 1.. run function stellarity:mobs/dragon/spawn/respawn_crystal/illumnate_spot

# # Post generation for Altar of the Accursed
# # Can't really do it with pure Worldgen sadly
# # Or I could, but definitely not in the way I would want to
execute if entity @s[tag=!stellarity.post_gen.initialized] in minecraft:the_end run function stellarity:post_gen/initialize

# # Dragon Screenshake
# execute if entity @s[tag=fe.respawn] as @a[tag=stellarity.dragon.screenshake] at @s run function stellarity:mobs/dragon/spawn/screenshake/tick_up
# execute if entity @s[tag=!fe.respawn] as @a[tag=stellarity.dragon.screenshake] at @s run function stellarity:mobs/dragon/spawn/screenshake/tick_down

execute if score #stellarity.dragon.ash_duration stellarity.misc matches 1.. run function stellarity:mobs/dragon/ash

## Vanilla podium purge (≤1.21.x — vanilla dragon fight cannot be disabled before 26.1)
# The vanilla fight re-places its bedrock fountain at the heightmap top of (0,0)
# whenever it cannot find its own portal pattern. Detect and erase it.
execute positioned 0 0 0 positioned over motion_blocking_no_leaves positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:bedrock if entity @s[distance=9..] run function far_end:structures/exit_portal/podium_cleanup
