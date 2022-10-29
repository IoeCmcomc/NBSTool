[![License](https://img.shields.io/github/license/IoeCmcomc/NBSTool "License")](https://opensource.org/licenses/MIT "License")
[![GitHub issues](https://img.shields.io/github/issues/IoeCmcomc/NBSTool)](https://github.com/IoeCmcomc/NBSTool/issues)
![GitHub all releases](https://img.shields.io/github/downloads/IoeCmcomc/NBSTool/total)
![GitHub repo size](https://img.shields.io/github/repo-size/IoeCmcomc/NBSTool)

------------

<div align="center">

![logo](https://raw.githubusercontent.com/IoeCmcomc/NBSTool/master/ui/256x256.png)

 ***NBSTool* is a program which provides some convenient tools to work with .nbs ([Open Note Block Studio](https://github.com/OpenNBS/OpenNoteBlockStudio "Open Note Block Studio")) files.**
 
 ![demo](https://user-images.githubusercontent.com/53734763/198820281-9e361913-d8ee-4667-9939-d21263b2f297.gif)

</div>

------------

## Features
- Work with multiple files;
- Open old formats (such as .mcsp2).
- Modify header information and change between versions;
- Arrange notes by instruments;
- Import from [MuseScore](https://github.com/musescore/MuseScore) files;
  - Only files created by MuseScore 3 are supported;
  - Support the following features:
    - Song title, author, tempo and time signature (with some limits);
    - Most of GM instruments to Minecraft instruments;
    - Percussion instruments (drum set);
    - Dotted, tied and normal notes and rests;
    - Notes' tuning and velocity;
    - Tuplets and notes whose duration less than 16th (by expanding the spaces between notes);
    - Voices.
- Export to JSON, MIDI or audio files:
  - MIDI conversion does not support custom instruments;
  - JSON export files are useful to understand how .nbs files are stored internally;
  - Export to audio:
    - Supported formats: MP3, WAV, OGG and FLAC.
    - Require [ffmpeg](https://ffmpeg.org/ "ffmpeg") to render audio. On Windows, ffmpeg have already been shipped with the program. On Linux, you need to install `ffmpeg` to use this feature;
  - Datapack export (this is for my personal use, currently not documented).

## Download
Go to the [Releases](https://github.com/IoeCmcomc/NBSTool/releases/latest "Releases") page to download the latest version.

After extracting the downloaded ZIP file to a folder, run the executable (NBSTool.exe on Windows, nbstool on Linux) to use the program.

## Issues
To report issues, please go to [Issues](https://github.com/IoeCmcomc/NBSTool/issues "Issues") page. For questions and suggestions, the [Discussion](https://github.com/IoeCmcomc/NBSTool/discussions "Discussion") page is the right place.
