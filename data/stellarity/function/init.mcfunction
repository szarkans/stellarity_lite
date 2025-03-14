## Misc
# Temporar variables OR things that don't need its own variable
scoreboard objectives add stellarity.misc dummy
scoreboard objectives add stellarity.misc2 dummy
scoreboard objectives add stellarity.misc3 dummy
scoreboard objectives add stellarity.misc4 dummy
scoreboard objectives add stellarity.misc.end_portal_animation dummy
scoreboard objectives add stellarity.misc.end_portal_bg_loop dummy

scoreboard objectives add stellarity.misc.motion.x1 dummy
scoreboard objectives add stellarity.misc.motion.x2 dummy
scoreboard objectives add stellarity.misc.motion.y1 dummy
scoreboard objectives add stellarity.misc.motion.y2 dummy
scoreboard objectives add stellarity.misc.motion.z1 dummy
scoreboard objectives add stellarity.misc.motion.z2 dummy

scoreboard objectives add stellarity.misc.loop.2t dummy
scoreboard objectives add stellarity.misc.loop.3t dummy
scoreboard objectives add stellarity.misc.loop.5t dummy
scoreboard objectives add stellarity.misc.loop.1s dummy
scoreboard objectives add stellarity.misc.loop.10s dummy
scoreboard objectives add stellarity.misc.loop.15s dummy

# Ender Dragon
scoreboard objectives add stellarity.dragon.times_killed dummy
scoreboard objectives add stellarity.dragon.screenshake dummy
scoreboard objectives add stellarity.dragon.respawn_animation_progress dummy
scoreboard objectives add stellarity.dragon.perch_cooldown dummy
scoreboard objectives add stellarity.dragon.health dummy
scoreboard objectives add stellarity.dragon.health_percent dummy
scoreboard objectives add stellarity.dragon.health_old dummy
scoreboard objectives add stellarity.dragon.time_chainfiring dummy
scoreboard objectives add stellarity.dragon.shulker_hell dummy
scoreboard objectives add stellarity.dragon.heartbeat dummy
scoreboard objectives add stellarity.dragon.ball_of_blight_cooldown dummy

## Creating teams
team add stellarity.purple_glow
team modify stellarity.purple_glow color dark_purple

team add stellarity.golden_glow
team modify stellarity.golden_glow color gold

team add stellarity.spirit_glow
team modify stellarity.spirit_glow color aqua

team add stellarity.homing_targets
team modify stellarity.homing_targets color aqua

team add stellarity.rave_glow
team modify stellarity.rave_glow color red

team add stellarity.phantom_glow
team modify stellarity.phantom_glow color green

team add stellarity.eol.night_glow
team modify stellarity.eol.night_glow color light_purple

team add stellarity.eol.day_glow
team modify stellarity.eol.day_glow color yellow

team add stellarity.dragons_eye.pacified
team modify stellarity.dragons_eye.pacified friendlyFire true
team modify stellarity.dragons_eye.pacified seeFriendlyInvisibles false
team modify stellarity.dragons_eye.pacified collisionRule pushOtherTeams

team add stellarity.dragon.pacify_others
team modify stellarity.dragon.pacify_others friendlyFire false

## Bossbars
# Ender Dragon
bossbar add stellarity:ender_dragon {"translate":"entity.minecraft.ender_dragon","color":"#BF00C8"}
bossbar set stellarity:ender_dragon color pink
bossbar set stellarity:ender_dragon players
bossbar set stellarity:ender_dragon max 300
bossbar set stellarity:ender_dragon style progress
bossbar set stellarity:ender_dragon visible true
# 'Crystals Left'
bossbar add stellarity:crystal_count {"translate":"stellarity.bossbars.crystals_left","fallback":"Crystals Left: %s","color":"#4C0081"}
bossbar set stellarity:crystal_count color purple
bossbar set stellarity:crystal_count visible true
bossbar set stellarity:crystal_count players
bossbar set stellarity:crystal_count max 10
bossbar set stellarity:crystal_count style notched_10
