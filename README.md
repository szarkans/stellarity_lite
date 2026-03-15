![Stellarity lite title](https://cdn.modrinth.com/data/cached_images/9cbb36aa9b7f9fd0754f2cd98f9e18226f5d5cd2.png)

This is a **fork** of [Stellarity](https://modrinth.com/datapack/stellarity) (made by **kohara**) - a datapack that completely overhauls **The End**, adding **23 new biomes**, redesigned **Strongholds** and **new structures** in The End!  
This version contains only WorldGen part of it and is fully community-driven. **No support/bug-fixes/updates guaranteed.**

### Try it yourself - <https://modrinth.com/datapack/stellarity-lite/settings/description>

***

![Preview of one new biome presented in Stellarity Lite](https://cdn.modrinth.com/data/bZgeDzN8/images/b77957d0f75bfb1484e0f5d27fa01ade76217d45.png)

## Features

<details>
<summary>WorldGen</summary>

![Stellarity's The End generation](https://cdn.modrinth.com/data/NsYxnUJm/images/0209ab9483fe97c1b8ba417e7dd9502602f01144.png)

A total of 23 new biomes, including 4 rehauled vanilla end biomes!

Biomes in Stellarity have 4 categories:

- Fields - open and mostly covered with grass.
- Barrens - usually hilly and desolate, featuring a low variety of blocks in their generation.
- Forests - forests.
- Frozen - sub-variants of existing biomes, featuring a sad white color palette, or in other words just frozen.

Islands are also no longer bound to one Y level, meaning that the terrain shape has a huge variety of shapes.

![Stellarity's The End generation](https://cdn.modrinth.com/data/NsYxnUJm/images/228a449903d7ad1044f7b0f6ddb722b48b0145ee.webp)

![Stellarity's The End generation](https://cdn.modrinth.com/data/NsYxnUJm/images/28efd23dadb32e7b5778c28ffe101625900d4afa.webp)

</details>

<details>
<summary>Structures</summary>

![1](https://i.imgur.com/H6SuHHh.png)

Strongholds have been redesigned completely. The walls of this fortress are home to the Illagers who guard the End Portals.

![https://imgur.com/34PJ0oZ](https://imgur.com/34PJ0oZ.png)

Strongholds are about 5x larger and feature huge amounts of the aforementioned Illagers who can also drop a few new items that might help you while fighting the Ender Dragon.

![https://i.imgur.com/fbg3HIb.png](https://i.imgur.com/fbg3HIb.png)

End Cities have been redesigned from ground up in order to increase their difficulty and reinforce their position of endgame structures. Inspired by Trial Chambers, they are filled with Trial Spawners which spawn upgraded versions of the Overworld mobs and drop keys used to open Vaults. Just in case the City Trials weren't difficult enough, almost every tower contains a protective End Crystal which prevents nearby players from placing or breaking blocks.

![https://i.imgur.com/ypTJ6bL.png](https://i.imgur.com/ypTJ6bL.png)

Both large and functional structures as well as small ambient ones have also been scattered across The End to give it some more life, lore and personality. Because it badly needed those. Yes, that is a Village in The End. Yes, Villagers sell different things there.

</details>

## Installation

### Singleplayer
Just put datapack in `datapacks` folder!

### Multiplayer
Just put datapack in `datapacks` folder, and make sure to set `enable-command-blocks` to `true` in `server.properties` file

### Modded
Just put mod in `mods` folder, duhh

## Help
If you need help with Stellarity: Lite - contact me at:  
- `@szarkans` at Discord  
- `@szarkan` at Telegram
- Create issue in [Stellarity Lite Repository on Github](https://github.com/szarkans/stellarity_lite)!

If you want to learn more about **original** Stellarity - check out [its Modrinth page](https://modrinth.com/datapack/stellarity)

<details>
<summary>Current bugs</summary>

Known bugs as of `3.0.5.9` version:  
- Crystal beams not spawning on dragon summon on 1.21-1.21.1 versions (there's no fix unfortunately)
- Lag spike on entering end portal for the first time
  
Found any other bugs? Contact `@szarkans` at Discord or `@szarkan` at Telegram.
</details>

***

## Compatibility

<details>
<summary>Fully incompatible</summary>
  
- 🔴 BetterEnd - causes a huge amount of micro-biomes to generate scattered around the dimension. It also makes some small changes that break some of the workarounds I need to do in order to make this data pack work. For context, doing some of the stuff I'm doing is repeatedly hitting the game with a baseball bat and joining it with super glue.  

- 🔴 YUNG's Better End Island - there is really no way to make these 2 projects compatible since they both handle the main island changes in different ways. Compatibility is planned for 1.21.4 and onwards.  

- 🔴 Probably any other custom Dragon fight datapacks/mods.

</details>

<details>
<summary>Partially incompatible</summary>
  
- 🟡 Quark - make sure to disable unlocking all recipes in the config.

- 🟡 Enlightend - I've had reports that Stellarity's biome take priority over Enlightend's, making the latter unable to generate. You can fix it by manually editing Stellarity's `the_end.json` file. Just simply replace some biomes (preferably ones that look similar to the one you want to replace them with!) with Enlightend's biomes and you should be good to go. It might take a few attempts to get it perfectly and not create micro-biomes.  

- 🟡 End's Phantasm - same problem as Enlightend which can be fixed the same way.  
</details>
