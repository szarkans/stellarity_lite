#function stellarity:items/main_marker

# Exit Portal loop
# Used for stuff like respawn checks, etc.
execute if entity @s[tag=fe.exit_portal] run function far_end:structures/exit_portal/main

# Scheduled checks for End Portal animation
execute if entity @s[tag=stellarity.end_portal_animation,tag=stellarity.end_portal_animation.check_schedule] run function stellarity:sfx/end_portal/checks/base

# Dragon markers
execute if entity @s[tag=stellarity.dragon_fireball] run function stellarity:mobs/dragon/attacks/fireball/main
execute if entity @s[tag=stellarity.dragon.shulkers] run function stellarity:mobs/dragon/attacks/take_off/shulkers/main
execute if entity @s[tag=stellarity.dragon.beam_thingy] run function stellarity:mobs/dragon/beam_thingy/move
execute if entity @s[tag=stellarity.ball_of_blight] run function stellarity:mobs/dragon/attacks/ball_of_blight/main

execute if entity @s[tag=stellarity.end_city.crystal] run function stellarity:post_gen/end_city/crystal/visuals
execute if entity @s[tag=stellarity.end_city.no_beacon] unless block ~ ~ ~ minecraft:beacon run function stellarity:post_gen/end_city/no_beacon
execute if entity @s[tag=stellarity.end_city.small_tower_crystal] run function stellarity:post_gen/end_city/crystal/small_tower

execute if entity @s[tag=stellarity.trial_spawner] run function stellarity:post_gen/end_city/trial_spawner_marker_loop
