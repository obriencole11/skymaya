# SkyMaya
Maya scripts for Skyrim rigging and animation. Uses [ck-cmd](https://github.com/aerisarn/ck-cmd) for creation kit asset import and export.

![Skywind Logo](/images/TESR_full_alpha.png)

## Introduction
SkyMaya is a collection of python scripts for Maya that make Skyrim asset import and export more accessible to Maya animators and riggers. Originally built for [Skywind](https://tesrskywind.com/)'s animation department, these tools could be used by any Skyrim modding project.

The main goal of these scripts is to streamline the process of creating Skyrim assets and improve the quality-of-life for our animators. While standalone tools like [ck-cmd](https://github.com/aerisarn/ck-cmd) and [hkxcmd](https://github.com/figment/hkxcmd) are excellent and accessible to a wide community, they often require a technical familiarity outside the comfort level of our animators. Additionally these tools often require Maya-specific work-arounds and "gotchas" that are better handled in a Maya-specific enviroment.

Under-the-hood this repository is bundled with a copy of ck-cmd which handles all creation kit asset conversion. Outside of this application everything is written for use within Autodesk Maya.

## Installation
1. Download and extract the project source code.
2. Copy the contents of skymaya-master to you local Maya scripts directory. This will likely be under your Documents directory: `C:\Users\%USER%\Documents\maya\%VERSION%`

## Features and Limitations
Currently SkyMaya supports the creation of custom rigs, skins and animations for use in Skyrim. However we unfortunately do not have a simple process for creating and modifying creature behavior projects. While this doesn't prevent us from creating new skins and animations, we are limited by the behaviors of vanilla Skyrim creatures and characters.

While custom behaviors are technically possible they are outside of the scope of these scripts. For testing purposes however we recomend replacing existing Skyrim creatures. This will make testing in game a lot easier and accessible for animators.

Practically however this means we're operating under the following constraints:
1. Animations cannot be added or removed.
2. Animation durations cannot be changed.
3. AI behavior cannot be modified.

## Project Structure
Skyrim uses a standardized structure for all creature and character assets. SkyMaya is designed to work within this structure for its source assets. While this structure may be awkward for those unfamiliar with the Skyrim workflow, it has numerous benefits. For one it allows the user to work inside their Skyrim directory. This means after files are exported they're already setup for testing in game. Additionally this structure allows our scripts to assume where files are located. For example animation conversion in ck-cmd requires several different skyrim files, by using this structure we can assume their locations so the user does not need to select them for every export.

Because this structure is so important and the behavior limitations detailed above, it is recomended users work off of existing creature and character projects for the time being. Skyrim files can be easily extracted with a [BSA Unpacker](https://www.nexusmods.com/skyrimspecialedition/mods/974).

## Command Reference
While the scripts are designed to be used in shelf buttons, all commands can be run standalone in Maya's **python** script editor or command line. Running standalone will allow for default arguments to be set.

### ![Import Rig Icon](/icons/importrig.png) Import Rig

```
from skymaya import main
main.importRig()
```

### ![Retarget Rig Icon](/icons/retargetrig.png) Retarget Rig

TODO

### ![Add Joint Icon](/icons/addskeleton.png) Add Joint(s)

TODO

### ![Export Rig Icon](/icons/exportrig.png) Export Rig

TODO

### ![Texture Skin Icon](/icons/textureskin.png) Texture Skin

TODO

### ![Retarget Skin Icon](/icons/retargetskin.png) Retarget Skin

TODO

### ![Export Skin Icon](/icons/exportskin.png) Export Skin

TODO

### ![Import Animation Icon](/icons/importanim.png) Import Animation

TODO

### ![Retarget Animation Icon](/icons/retargetanim.png) Retarget Animation(s)

TODO

### ![Export Animation Icon](/icons/exportanim.png) Export Animation(s)

TODO



