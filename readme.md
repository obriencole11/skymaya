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

## Command Reference

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



