
[![License](https://img.shields.io/github/license/IoeCmcomc/NBSTool "License")](https://opensource.org/licenses/MIT "License")
[![GitHub issues](https://img.shields.io/github/issues/IoeCmcomc/NBSTool)](https://github.com/IoeCmcomc/NBSTool/issues)
![GitHub all releases](https://img.shields.io/github/downloads/IoeCmcomc/NBSTool/total)
![GitHub repo size](https://img.shields.io/github/repo-size/IoeCmcomc/NBSTool)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/IoeCmcomc/NBSTool.svg)](http://isitmaintained.com/project/IoeCmcomc/NBSTool "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/IoeCmcomc/NBSTool.svg)](http://isitmaintained.com/project/IoeCmcomc/NBSTool "Percentage of issues still open")
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FIoeCmcomc%2FNBSTool&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)


------------

<div align="center">

![logo](https://raw.githubusercontent.com/IoeCmcomc/NBSTool/master/ui/256x256.png)

 ***NBSTool* is a program which provides some convenient tools to work with .nbs ([Open Note Block Studio](https://github.com/OpenNBS/OpenNoteBlockStudio "Open Note Block Studio")) files.**
 
 ![demo](https://user-images.githubusercontent.com/53734763/198820281-9e361913-d8ee-4667-9939-d21263b2f297.gif)

</div>

------------

## Features
- Work with multiple files;
- Open old formats (such as .mcsp2);
- Available tools/operations:
   - Modify header information and change between versions;
   - Arrange notes by instruments;
   - Hard-apply layer volumes and/or panning to notes;
   - Insert image as silent notes for decoration purpose.
- Import from MIDI files:
   -   Only type 1 MIDI files are tested;
   -   Support importing note velocity, note panning and note fine-pitch;
   -   Allow importing MIDI notes as multiple successive NBS notes;
     -   These trailing note' velocity can be fading out of having a specified value;
     -   Allow applying stereo effect to trailing notes;
   -   Can automatically expand distance between notes to fit as many note as possible.
- Import from JSON files;
- Export to other formats:
  - MIDI conversion does not support custom instruments;
  - JSON export files are useful to understand how .nbs files are stored internally;
  - Export to audio:
    - Supported formats: MP3, WAV, OGG and FLAC.
  - Export to Impulse Tracker files (.it) with custom instruments;
  - Exporting to audo and .it files requires [ffmpeg](https://ffmpeg.org/ "ffmpeg") to render audio. On Windows, ffmpeg have already been shipped with the program. On Linux, you need to install `ffmpeg` to use this feature;
  - Datapack export (this is for my personal use, currently not documented).

## Download
Go to the [Releases](https://github.com/IoeCmcomc/NBSTool/releases/latest "Releases") page to download the latest version.

After extracting the downloaded ZIP file to a folder, run the executable (nbstool.exe on Windows, nbstool or nbstool.bin on Linux) to use the program.

## Issues
To report issues, please go to [Issues](https://github.com/IoeCmcomc/NBSTool/issues "Issues") page. For questions and suggestions, the [Discussion](https://github.com/IoeCmcomc/NBSTool/discussions "Discussion") page is the right place.
