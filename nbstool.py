# This file is a part of:
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██
# __________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


# nuitka-project: --standalone
# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --show-anti-bloat-changes
# nuitka-project: --assume-yes-for-downloads
# nuitka-project: --report=compilation-report.xml
# nuitka-project: --user-package-configuration-file=custom-nuitka-package.config.yml
# nuitka-project: --windows-console-mode=attach
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-icon-from-ico=icon.ico
#    nuitka-project: --windows-product-name=NBSTool
#    nuitka-project: --windows-company-name=IoeCmcomc
#    nuitka-project: --windows-file-version=1.4.0.0
#    nuitka-project: --windows-product-version=1.4.0.0
#    nuitka-project: --windows-file-description=NBSTool


from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import platform
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import uuid
import warnings
import webbrowser
from ast import literal_eval
from asyncio import CancelledError, sleep
from copy import copy, deepcopy
from datetime import timedelta
from importlib.metadata import version
from itertools import repeat
from math import floor, log2
from os import path as os_path
from pathlib import Path
from random import choice, randint
from time import time
from tkinter import BooleanVar, IntVar, StringVar, Variable
from tkinter.filedialog import (askdirectory, askopenfilename,
                                askopenfilenames, asksaveasfilename)
from tkinter.messagebox import showerror, showinfo, showwarning
from typing import (Any, Callable, Coroutine, Deque, Iterable, Literal,
                    Optional, Union)

import pygubu
import pygubu.widgets.combobox
from jsonschema import validate
from loguru import logger
from pygubu import Builder
# Explict imports for PyInstaller
# from pygubu.builder import tkstdwidgets, ttkstdwidgets
from pygubu.widgets import dialog, pathchooserinput
from pygubu.widgets.dialog import Dialog
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.combobox import Combobox as PygubuCombobox
from PIL import Image
from coloraide import Color

# Explict import for Nuitka
import customwidgets.builder

from common import BASE_RESOURCE_PATH, resource_path

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if os.name == 'nt':  # Windows
    # Ensure pydub.utils.which can splits the added ffmpeg path properly
    # Fix for the issue #10
    if not os.environ["PATH"].endswith(os.pathsep):
        os.environ["PATH"] += os.pathsep
    # Add the path of the ffmpeg before the first pydub import statement
    os.environ["PATH"] += resource_path('ffmpeg', 'bin')

from pydub.utils import which

from lyric_parser import lyric2captions
from mcsp2nbs import mcsp2nbs
from midi2nbs import midi2nbs
from musescore2nbs import musescore2nbs
from nbs2audio import nbs2audio
from nbs2impulsetracker import nbs2it
from nbs2midi import nbs2midi
from nbsio import NBS_VERSION, VANILLA_INSTS, Instrument, Layer, NbsSong, Note

__version__ = '1.4.0'

NBS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "header": {
            "type": "object",
            "properties": {
                "length": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 65535
                },
                "file_version": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 255
                },
                "vani_inst": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 65535
                },
                "height": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 65535
                },
                "name": {
                    "type": "string",
                    "maxLength": 4294967295
                },
                "author": {
                    "type": "string",
                    "maxLength": 4294967295
                },
                "orig_author": {
                    "type": "string",
                    "maxLength": 4294967295
                },
                "description": {
                    "type": "string",
                    "maxLength": 4294967295
                },
                "tempo": {
                    "type": "number",
                    "minimun": 0,
                    "maximum": 655.35
                },
                "auto_save": {
                    "type": "boolean"
                },
                "auto_save_time": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 255
                },
                "time_sign": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 255
                },
                "minutes_spent": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 4294967295
                },
                "left_clicks": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 4294967295
                },
                "right_clicks": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 4294967295
                },
                "block_added": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 4294967295
                },
                "block_removed": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 4294967295
                },
                "import_name": {
                    "type": "string",
                    "maxLength": 4294967295
                },
                "loop": {
                    "type": "boolean"
                },
                "loop_max": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 255
                },
                "loop_start": {
                    "type": "integer",
                    "minimun": 0,
                    "maximum": 65535
                }
            },
            "required": [
                "author",
                "auto_save",
                "auto_save_time",
                "block_added",
                "block_removed",
                "description",
                "file_version",
                "height",
                "import_name",
                "left_clicks",
                "length",
                "minutes_spent",
                "name",
                "orig_author",
                "right_clicks",
                "tempo",
                "time_sign",
                "vani_inst"
            ]
        },
        "notes": {
            "type": "array",
            # "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "tick": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 65535
                    },
                    "layer": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 65535
                    },
                    "inst": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 255
                    },
                    "key": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 87
                    },
                    "vel": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 100
                    },
                    "pan": {
                        "type": "integer",
                        "minimun": -100,
                        "maximum": 100
                    },
                    "pitch": {
                        "type": "integer",
                        "minimun": -32768,
                        "maximum": 32767
                    }
                },
                "required": [
                    "inst",
                    "key",
                    "layer",
                    "pan"
                ]
            }
        },
        "layers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "maxLength": 4294967295
                    },
                    "lock": {
                        "type": "boolean"
                    },
                    "volume": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 100
                    },
                    "pan": {
                        "type": "integer",
                        "minimun": -100,
                        "maximum": 100
                    }
                },
                "required": [
                    "name"
                ]
            }
        },
        "custom_instruments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "maxLength": 4294967295
                    },
                    "filePath": {
                        "type": "string",
                        "maxLength": 4294967295
                    },
                    "pitch": {
                        "type": "integer",
                        "minimun": 0,
                        "maximum": 87
                    },
                    "pressKeys": {
                        "type": "boolean"
                    },
                    "sound_id": {
                        "type": "string",
                        "maxLength": 4294967295
                    }
                },
                "required": [
                    "filePath",
                    "name",
                    "pitch",
                    "pressKeys",
                    "sound_id"
                ]
            }
        }
    },
    "required": [
        "custom_instruments",
        "header",
        "layers",
        "notes"
    ]
}

# Taken from Note Block World source code. This shouldn't violate AGPL, though.
# https://github.com/OpenNBS/NoteBlockWorld/blob/main/shared/features/thumbnail/index.ts#L27
NBS_INST_NOTE_COLORS_HEX = (
    '#1964ac',
    '#3c8e48',
    '#be6b6b',
    '#bebe19',
    '#9d5a98',
    '#572b21',
    '#bec65c',
    '#be19be',
    '#52908d',
    '#bebebe',
    '#1991be',
    '#be2328',
    '#be5728',
    '#19be19',
    '#be1957',
    '#575757',
)
NBS_INST_NOTE_COLORS = tuple(Color(color)
                             for color in NBS_INST_NOTE_COLORS_HEX)
NBS_NOTE_COLORS_TO_INST = {color.to_string(
    hex=True): index for index, color in enumerate(NBS_INST_NOTE_COLORS)}

NBSTOOL_FIRST_COMMIT_TIMESTAMP = 1565100420
CONSONANTS = "bcdfghjklmnpqrstvwxyzBCDFGHJLKMNPQRSTVWXYZ"
VOWELS = "ueoai"
NBW_THUMBNAIL_ZOOM_PERCENT_VALUES = (400, 200, 100, 50, 25)
NBW_WIDTH_DIVISOR = 4000
NBW_HEIGHT_DIVISOR = 2400


def genRandomFilename(prefix: str = '') -> str:
    randChars = (item for sublist in (
        (choice(CONSONANTS), choice(VOWELS)) for _ in range(4)) for item in sublist)
    return prefix + ''.join(randChars) + str(
        int(time()) - NBSTOOL_FIRST_COMMIT_TIMESTAMP)


class MainWindow():
    def __init__(self):
        builder: Builder = pygubu.Builder()
        self.builder: Builder = builder
        builder.add_resource_path(BASE_RESOURCE_PATH)
        builder.add_from_file(resource_path('ui/toplevel.ui'))
        self.toplevel: tk.Toplevel = builder.get_object('toplevel')
        self.mainwin: tk.Frame = builder.get_object('mainFrame')
        style = ttk.Style(self.toplevel)
        style.layout('Barless.TNotebook.Tab', [])  # turn off tabs
        style.configure('Barless.TNotebook', borderwidth=0,
                        highlightthickness=0)
        if os.name == 'posix':
            ttk.Style().theme_use('clam')

        self.fileTable: ttk.Treeview = builder.get_object('fileTable')
        applyBtn = builder.get_object('applyBtn')

        self.toplevel.title("NBSTool")
        centerToplevel(self.toplevel)

        self.popupMenu: tk.Menu
        self.initMenuBar()
        self.initVarsAndCallbacksFrom(builder)
        self.initFormatTab()
        self.initHeaderTab()
        self.initFlipTab()
        self.initArrangeTab()
        self.intImportImageTab()
        self.windowBind()

        def on_fileTable_select(event):
            fileTable: ttk.Treeview = event.widget
            if fileTable['selectmode'] == 'none':
                return
            selection: tuple = fileTable.selection()
            selectionLen = len(selection)
            selectionNotEmpty = selectionLen > 0
            if selectionNotEmpty:
                builder.get_object('fileMenu').entryconfig(1, state="normal")
                builder.get_object('saveFilesBtn')["state"] = "normal"
                builder.get_object('removeEntriesBtn')["state"] = "normal"
                self.updateHeaderNotebook(
                    [fileTable.index(item) for item in selection])
                applyBtn["state"] = "normal"
            else:
                builder.get_object('fileMenu').entryconfig(1, state="disabled")
                builder.get_object('saveFilesBtn')["state"] = "disabled"
                builder.get_object('removeEntriesBtn')["state"] = "disabled"
                builder.get_object('headerNotebook').select(0)
                self.selectedFilesVerStr.set("No file are selected.")
                applyBtn["state"] = "disabled"
            exportMenu: tk.Menu = builder.get_object('exportMenu')
            exportMenu.entryconfig(
                0, state="normal" if selectionLen == 1 else "disable")
            exportMenu.entryconfig(
                1, state="normal" if selectionNotEmpty else "disable")
            exportMenu.entryconfig(
                2, state="normal" if selectionNotEmpty else "disable")
            exportMenu.entryconfig(
                3, state="normal" if selectionNotEmpty else "disable")
            exportMenu.entryconfig(
                4, state="normal" if selectionNotEmpty else "disable")

        self.fileTable.bind("<<TreeviewSelect>>", on_fileTable_select)

        self.mainwin.lift()
        self.mainwin.focus_force()
        self.mainwin.grab_set()
        self.mainwin.grab_release()

        self.VERSION = __version__
        self.filePaths = []
        self.songsData = []
        self.selectedFilesVersion = -1

    def initVarsAndCallbacksFrom(self, builder: Builder):
        # These members will be initialized later
        self.selectedFilesVerStr: StringVar
        self.headerLoop: BooleanVar
        self.headerLoopCount: StringVar
        self.headerLoopStart: StringVar
        self.headerAutosave: BooleanVar
        self.headerAutosaveInterval: StringVar
        self.headerMinuteSpent: StringVar
        self.headerLeftClicks: StringVar
        self.headerRightClicks: StringVar
        self.headerBlockAdded: StringVar
        self.headerBlockRemoved: StringVar
        self.arrangeMode: StringVar
        self.flipHorizontallyCheckVar: BooleanVar
        self.flipVerticallyCheckVar: BooleanVar
        self.applyLayerVolCheckVar: BooleanVar
        self.applyLayerPanCheckVar: BooleanVar
        self.groupPerc: BooleanVar
        self.pixelArtImagePathVar: StringVar
        self.imgInsertPosVar: StringVar
        self.imgInsertPosTickVar: IntVar
        self.imgInsertPosLayerVar: IntVar
        self.imgInsertSizePercentVar: IntVar

        builder.import_variables(self)
        builder.connect_callbacks(self)

    def isInteger(self, value: str) -> bool:
        return value == '' or value.isdigit()

    def isRequiredInteger(self, value: str) -> bool:
        return value.isdigit()

    def getSelectedFilesVersion(self, selection: Iterable) -> int:
        fileVersion = -1
        for i in selection:
            header = self.songsData[i].header
            ver: int = header.file_version
            if (ver != fileVersion) and (fileVersion != -1):
                return -1
            fileVersion = ver
        return fileVersion

    def updateHeaderNotebook(self, selection: Iterable) -> None:
        def updateCheckbutton(i: int, var: Variable, widget: ttk.Checkbutton, value: bool) -> bool:
            ret = (i > 0) and (var.get() != value)
            if ret:
                widget.state(['alternate'])
            else:
                var.set(value)
            return not ret

        def updateSpinbox(i: int, var: Variable, value: int) -> None:
            var.set('' if ((i > 0) and (var.get() != str(value))) else value)

        get_object = self.builder.get_object
        notebook: ttk.Notebook = self.builder.get_object('headerNotebook')
        fileVersion = self.getSelectedFilesVersion(selection)
        if fileVersion == -1:
            notebook.select(0)
            self.selectedFilesVerStr.set(
                "Selected file(s) don't have the same version number.")
            self.selectedFilesVersion = -1
            return
        self.selectedFilesVersion = fileVersion
        self.selectedFilesVerStr.set(
            f"Selected file(s) format version: {fileVersion if fileVersion > 0 else 'Classic': >8}")
        notebook.select(1)
        for i, index in enumerate(selection):
            header = self.songsData[index].header
            if fileVersion >= 4:
                loop = header.loop
                checkBox: ttk.Checkbutton = get_object('headerLoopCheck')
                checkBox['state'] = 'normal'
                if updateCheckbutton(i, self.headerLoop, checkBox, loop):
                    updateSpinbox(i, self.headerLoopCount, header.loop_max)
                    updateSpinbox(i, self.headerLoopStart, header.loop_start)
                self.onLoopCheckBtn()
            else:
                # Source: https://stackoverflow.com/questions/24942760/is-there-a-way-to-gray-out-disable-a-tkinter-frame
                for child in get_object('headerLoopFrame').winfo_children():
                    child.configure(state='disable')

            autoSave = header.auto_save
            if updateCheckbutton(i, self.headerAutosave, get_object('headerAutosaveCheck'), autoSave):
                updateSpinbox(i, self.headerAutosaveInterval,
                              header.auto_save_time)
            self.onAutosaveCheckBtn()

            updateSpinbox(i, self.headerMinuteSpent, header.minutes_spent)
            updateSpinbox(i, self.headerLeftClicks, header.left_clicks)
            updateSpinbox(i, self.headerRightClicks, header.right_clicks)
            updateSpinbox(i, self.headerBlockAdded, header.block_added)
            updateSpinbox(i, self.headerBlockRemoved, header.block_removed)

    def onAutosaveCheckBtn(self):
        label = self.builder.get_object('headerAutosaveLabel')
        spinbox = self.builder.get_object('headerAutosaveSpin')
        state = 'normal' if ((not 'alternate' in self.builder.get_object(
            'headerAutosaveCheck').state()) and self.headerAutosave.get()) else 'disabled'
        label['state'] = state
        spinbox['state'] = state

    def onLoopCheckBtn(self):
        checkBox: ttk.Checkbutton = self.builder.get_object('headerLoopCheck')
        loop = self.headerLoop.get()
        state = 'normal' if ((not 'alternate' in self.builder.get_object(
            'headerLoopCheck').state()) and loop) else 'disabled'
        for child in self.builder.get_object('headerLoopFrame').winfo_children():
            if child is not checkBox:
                child.configure(state=state)

    def initMenuBar(self):
        self.menuBar = menuBar = self.builder.get_object('menubar')
        self.toplevel.configure(menu=menuBar)

    def disabledFileTable(self):
        self.fileTable.state(('disabled',))
        self.fileTable['selectmode'] = 'none'

    def enableFileTable(self):
        self.fileTable.state(('!disabled',))
        self.fileTable['selectmode'] = 'extended'

    def openFiles(self, _=None):
        self.fileTable.delete(*self.fileTable.get_children())
        self.filePaths.clear()
        self.songsData.clear()
        self.addFiles()

    def addFileInfo(self, filePath: str, songData: NbsSong) -> None:
        if filePath == '':
            filePath = genRandomFilename('unsaved_')
        header = songData.header
        length = timedelta(seconds=floor(
            header.length / header.tempo)) if header.length > 0 else "Not calculated"
        self.fileTable.insert("", 'end', text=filePath, values=(
            length, header.name, header.author, header.orig_author))

    def addFiles(self, _=None, paths=()):
        types = [("Note Block Studio files", '*.nbs'),
                 ("Minecraft Song Planner v2 files", '*.mcsp2'), ('All files', '*')]
        addedPaths = []
        if len(paths) > 0:
            addedPaths = paths
        else:
            addedPaths = askopenfilenames(filetypes=types)
        if len(addedPaths) == 0:
            return
        self.builder.get_object('applyBtn')['state'] = 'disabled'
        self.disabledFileTable()
        for i, filePath in enumerate(addedPaths):
            try:
                if filePath.endswith('.mcsp2'):
                    songData = mcsp2nbs(filePath)
                elif filePath.endswith('.nbs'):
                    songData = NbsSong(filePath)
                else:
                    raise NotImplementedError(
                        "This file format is not supported. However, you can try importing from the 'Import' menu instead.")
                self.songsData.append(songData)
            except Exception as e:
                showerror("Opening file error",
                          f'Cannot open file "{filePath}"\n{e.__class__.__name__}: {e}')
                logger.exception(e)
                continue
            self.addFileInfo(filePath, songData)
            if i % 3 == 0:
                self.mainwin.update()
        self.filePaths.extend(addedPaths)
        self.enableFileTable()
        self.builder.get_object('applyBtn')['state'] = 'normal'
        self.builder.get_object('fileMenu').entryconfig(2, state="normal" if len(
            self.filePaths) > 0 else "disabled")

    def saveFiles(self, _=None):
        if len(self.filePaths) == 0:
            return
        fileTable = self.fileTable
        if len(selection := fileTable.selection()) > 0:
            if len(selection) == 1:
                i = fileTable.index(selection[0])
                filePath = self.filePaths[i]
                types = [('Note Block Studio files', '*.nbs'),
                         ('All files', '*')]
                fileName = ''
                if filePath != '':
                    fileName = os.path.basename(filePath)
                else:
                    fileName = self.songsData[i].header.import_name
                path = asksaveasfilename(
                    filetypes=types, initialfile=fileName.rsplit('.', 1)[0], defaultextension=".nbs")
                if path == '':
                    return
                if filePath == '':
                    fileTable.item(selection[0], text=os.path.join(path))
                self.builder.get_object('applyBtn')['state'] = 'disabled'
                self.disabledFileTable()
                self.mainwin.update()
                self.songsData[i].write(path)
                self.enableFileTable()
                self.builder.get_object('applyBtn')['state'] = 'normal'
                return

            path = askdirectory(title="Select folder to save")
            if path == '':
                return
            Path(path).mkdir(parents=True, exist_ok=True)
            self.disabledFileTable()
            for item in selection:
                i = fileTable.index(item)
                filePath = self.filePaths[i]
                if filePath == '':
                    fileName = self.songsData[i].header.import_name.rsplit('.', 1)[
                        0]
                    if fileName == '':
                        fileName = genRandomFilename('untitled_')
                    filePath = fileName + '.nbs'
                savedPath = os.path.join(path, filePath)
                fileTable.item(item, text=savedPath)
                self.filePaths[i] = savedPath
                try:
                    self.songsData[i].write(os.path.join(
                        path, os.path.basename(filePath)))
                except Exception as e:
                    showerror("Saving file error",
                              f'Cannot save file "{os_path.join(path, os_path.basename(filePath))}"\n{e.__class__.__name__}: {e}'
                              )
                    logger.exception(e)
            self.enableFileTable()
            self.builder.get_object('applyBtn')['state'] = 'normal'

    def saveAll(self, _=None):
        if len(self.filePaths) == 0:
            return
        path = askdirectory(title="Select folder to save")
        if path == '':
            return
        Path(path).mkdir(parents=True, exist_ok=True)
        self.builder.get_object('applyBtn')['state'] = 'disabled'
        self.disabledFileTable()
        self.mainwin.update()
        items = self.fileTable.get_children()
        for i, filePath in enumerate(self.filePaths):
            try:
                if filePath == '':
                    filePath = self.songsData[i].header.import_name.rsplit('.', 1)[
                        0] + '.nbs'
                    savedPath = os.path.join(path, filePath)
                    self.fileTable.item(items[i], text=savedPath)
                    self.filePaths[i] = savedPath
                self.songsData[i].write(os.path.join(
                    path, os.path.basename(filePath)))
            except Exception as e:
                showerror("Saving file error",
                          f'Cannot save file "{os_path.join(path, os_path.basename(filePath))}"\n{e.__class__.__name__}: {e}')
                logger.exception(e)
        self.enableFileTable()
        self.builder.get_object('applyBtn')['state'] = 'normal'

    def removeSelectedFiles(self):
        if len(self.filePaths) == 0:
            return
        fileTable = self.fileTable
        if len(selection := fileTable.selection()) > 0:
            for item in reversed(selection):
                i = fileTable.index(item)
                fileTable.delete(item)
                del self.filePaths[i]
                del self.songsData[i]
        fileTable.selection_remove(fileTable.selection())

    def initFormatTab(self):
        combobox = self.builder.get_object('formatCombo')
        combobox.configure(
            values=("(not selected)", *range(NBS_VERSION, 1-1, -1), "Classic"))
        combobox.current(0)

    def initHeaderTab(self):
        self.builder.get_object('headerAutosaveCheck').state(['alternate'])
        self.builder.get_object('headerLoopCheck').state(['alternate'])

    def initFlipTab(self):
        self.builder.get_object('flipHorizontallyCheck').state(('!selected',))
        self.builder.get_object('flipVerticallyCheck').state(('!selected',))

    def initArrangeTab(self):
        self.arrangeMode.set('none')
        # self.builder.get_object('arrangeGroupPrec').state(('!selected',))

    def intImportImageTab(self):
        self.pixelArtImagePathVar.set('')
        self.imgInsertPosVar.set('lastLayer')
        pathChooser: PathChooserInput = self.builder.get_object(
            'pixelArtImagePathChooser')
        filetypes = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp'), ('All files', '*')]
        pathChooser.config(filetypes=filetypes, width=200)
        sizeCombo: PygubuCombobox = self.builder.get_object(
            'imgInsertSizeCombo')
        options: list = []
        for zoom in NBW_THUMBNAIL_ZOOM_PERCENT_VALUES:
            # zoom = 400% => width = 10, height = 6
            # zoom = 200% => width = 20, height = 12
            # zoom = 100% => width = 40, height = 24
            width = NBW_WIDTH_DIVISOR // zoom
            height = NBW_HEIGHT_DIVISOR // zoom
            options.append([zoom, f"{width}x{height} ({zoom}%)"])
        sizeCombo.config(values=options)
        sizeCombo.current(100)

    def callMidiImportDialog(self):
        dialogue = MidiImportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callMuseScoreImportDialog(self):
        dialogue = MuseScoreImportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callJsonImportDialog(self):
        dialogue = JsonImportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callDatapackExportDialog(self):
        dialogue = DatapackExportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callMidiExportDialog(self):
        dialogue = MidiExportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callAudioExportDialog(self):
        dialogue = AudioExportDialog(self.toplevel, self)
        dialogue.run()
        del dialogue

    def callJsonExportDialog(self):
        JsonExportDialog(self.toplevel, self).run()

    def callImpulseExportDialog(self):
        ImpulseExportDialog(self.toplevel, self).run()

    def callAboutDialog(self):
        dialogue = AboutDialog(self.toplevel, self)
        del dialogue

    def windowBind(self):
        toplevel = self.toplevel
        mainwin = self.mainwin
        # Keys
        toplevel.bind('<Escape>', self.onClose)
        toplevel.bind('<Control-o>', self.openFiles)
        toplevel.bind('<Control-s>', self.saveFiles)
        toplevel.bind('<Control-Shift-s>', self.saveAll)
        toplevel.bind('<Control-Shift-S>', self.saveAll)

        # Bind class
        for tkclass in ('TButton', 'Checkbutton', 'Radiobutton'):
            mainwin.bind_class(tkclass, '<Return>', lambda e: e.widget.event_generate(
                '<space>', when='tail'))

        mainwin.bind_class("TCombobox", "<Return>",
                           lambda e: e.widget.event_generate('<Down>'))

        for tkclass in ("Entry", "Text", "ScrolledText", "TCombobox"):
            mainwin.bind_class(tkclass, "<Button-3>", self.popupmenus)

        # mainwin.bind_class("TNotebook", "<<NotebookTabChanged>>",
        #                    self._on_tab_changed)

        mainwin.bind_class("Treeview", "<Shift-Down>",
                           self._on_treeview_shift_down)
        mainwin.bind_class("Treeview", "<Shift-Up>",
                           self._on_treeview_shift_up)
        mainwin.bind_class("Treeview", "<Button-1>",
                           self._on_treeview_left_click, add=True)

        # Credit: https://stackoverflow.com/a/63173461/12682038
        def treeview_select_all(event):
            return event.widget.selection_add(event.widget.get_children())

        mainwin.bind_class("Treeview", "<Control-a>", treeview_select_all)
        mainwin.bind_class("Treeview", "<Control-A>", treeview_select_all)

    # Credit: http://code.activestate.com/recipes/580726-tkinter-notebook-that-fits-to-the-height-of-every-/
    def _on_tab_changed(self, event):
        event.widget.update_idletasks()

        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())

    # Credit: https://stackoverflow.com/questions/57939932/treeview-how-to-select-multiple-rows-using-cursor-up-and-down-keys
    def _on_treeview_shift_down(self, event):
        tree: ttk.Treeview = event.widget
        cur_item = tree.focus()
        next_item = tree.next(cur_item)
        if next_item == '':
            return 'break'
        selection = tree.selection()
        if next_item in selection:
            tree.selection_remove(cur_item)
        else:
            tree.selection_add(cur_item)
        tree.selection_add(next_item)
        tree.focus(next_item)
        tree.see(next_item)
        return None

    def _on_treeview_shift_up(self, event):
        tree: ttk.Treeview = event.widget
        cur_item = tree.focus()
        prev_item = tree.prev(cur_item)
        if prev_item == '':
            return 'break'
        selection = tree.selection()
        if prev_item in selection:
            tree.selection_remove(cur_item)
        else:
            tree.selection_add(cur_item)
        tree.selection_add(prev_item)
        tree.focus(prev_item)
        tree.see(prev_item)
        return None

    def _on_treeview_left_click(self, event):
        tree = event.widget
        if tree.identify_row(event.y) == '':
            tree.selection_set(tuple())

    def popupmenus(self, event):
        w = event.widget
        self.popupMenu = tk.Menu(self.mainwin, tearoff=False)
        self.popupMenu.add_command(
            label="Select all", accelerator="Ctrl+A", command=lambda: w.event_generate("<Control-a>"))
        self.popupMenu.add_separator()
        self.popupMenu.add_command(
            label="Cut", accelerator="Ctrl+X", command=lambda: w.event_generate("<Control-x>"))
        self.popupMenu.add_command(
            label="Copy", accelerator="Ctrl+C", command=lambda: w.event_generate("<Control-c>"))
        self.popupMenu.add_command(
            label="Paste", accelerator="Ctrl+V", command=lambda: w.event_generate("<Control-v>"))
        self.popupMenu.tk.call("tk_popup", self.popupMenu,
                               event.x_root, event.y_root)

    def onClose(self, event=None):
        self.toplevel.quit()
        self.toplevel.destroy()

    def onArrangeModeChanged(self):
        self.builder.get_object('arrangeGroupPrec')['state'] = 'normal' if (
            self.arrangeMode.get() == 'instruments') else 'disabled'

    def onImgInsertPosChanged(self):
        state = 'normal' if (self.imgInsertPosVar.get()
                             == 'custom') else 'disabled'
        self.builder.get_object('imgInsertCustomLabel1')['state'] = state
        self.builder.get_object('imgInsertCustomLabel2')['state'] = state
        self.builder.get_object('imgInsertPosTickSpin')['state'] = state
        self.builder.get_object('imgInsertPosLayerSpin')['state'] = state

    def applyTool(self):
        get_object = self.builder.get_object
        get_object('applyBtn')['state'] = 'disabled'
        fileTable = self.fileTable
        changedSongData = {}
        selectedIndexes = [fileTable.index(item)
                           for item in fileTable.selection()]
        selectionLen = len(selectedIndexes)
        outputVersion = -1

        if (formatComboIndex := get_object('formatCombo').current()) > 0:
            outputVersion = (NBS_VERSION + 1) - formatComboIndex

        async def work(dialog: ProgressDialog):
            try:
                notebook: ttk.Notebook = get_object('headerNotebook')
                headerModifiable = notebook.index(notebook.select()) == 1
                insertImageNotes: list[Note] = []
                if (imgPath := self.pixelArtImagePathVar.get()) and imgPath.strip() != '':
                    zoomPercent = self.imgInsertSizePercentVar.get()
                    insertWidth = NBW_WIDTH_DIVISOR // zoomPercent
                    insertHeight = NBW_HEIGHT_DIVISOR // zoomPercent
                    insertImageNotes = self.imageToNotes(imgPath, insertWidth, insertHeight)
                i = 0
                for i, index in enumerate(selectedIndexes):
                    dialog.totalProgress.set(i)
                    fileName = os.path.split(self.filePaths[i])[1]
                    dialog.currentText.set(f"Current file: {fileName}")
                    dialog.totalText.set(
                        f"Processing {i+1} / {selectionLen} files")
                    dialog.currentProgress.set(0)
                    songData: NbsSong = deepcopy(self.songsData[index])
                    dialog.setCurrentPercentage(randint(20, 25))
                    await sleep(0.001)
                    length = songData.header.length
                    maxLayer = songData.maxLayer

                    if headerModifiable:
                        self.modifyHeaders(songData.header)

                    if outputVersion > -1:
                        songData.header.file_version = outputVersion
                        if outputVersion == 0:
                            songData.downgradeToClassic()

                    if self.flipHorizontallyCheckVar.get() or self.flipVerticallyCheckVar.get():
                        for note in songData.notes:
                            if self.flipHorizontallyCheckVar.get():
                                note.tick = length - note.tick
                            if self.flipVerticallyCheckVar.get():
                                note.layer = maxLayer - note.layer
                    songData.sortNotes()
                    dialog.setCurrentPercentage(45)
                    await sleep(0.001)

                    if self.arrangeMode.get() == 'collapse':
                        self.collapseNotes(songData.notes)
                    elif self.arrangeMode.get() == 'instruments':
                        compactNotes(songData, self.groupPerc.get())
                    songData.sortNotes()
                    dialog.setCurrentPercentage(60)
                    await sleep(0.001)

                    if self.applyLayerVolCheckVar.get() or self.applyLayerPanCheckVar.get():
                        applyVol: bool = self.applyLayerVolCheckVar.get()
                        applyPan: bool = self.applyLayerPanCheckVar.get()

                        default_layer = Layer("")
                        if (songData.maxLayer >= songData.header.height):
                            songData.layers.extend(
                                repeat(default_layer, songData.maxLayer+1 - songData.header.height))

                        for note in songData.notes:
                            layer = songData.layers[note.layer]
                            if applyVol:
                                note.vel = (note.vel * layer.volume) // 100
                            if applyPan and (layer.pan != 0):
                                note.pan = (note.pan + layer.pan) // 2

                        for layer in songData.layers:
                            if applyVol:
                                layer.volume = 100
                            if applyPan:
                                layer.pan = 0

                    if insertImageNotes:
                        insertPos = self.imgInsertPosVar.get()
                        insertTick: int = -1
                        insertLayer: int = -1
                        if insertPos == 'lastLayer':
                            insertTick = 0
                            insertLayer = songData.maxLayer
                        elif insertPos == 'lastTick':
                            insertTick = len(songData)
                            insertLayer = 0
                        elif insertPos == 'custom':
                            insertTick = self.imgInsertPosTickVar.get()
                            insertLayer = self.imgInsertPosLayerVar.get()

                        self.shiftNotes(insertImageNotes, insertTick, insertLayer)
                        songData.notes.extend(insertImageNotes)     

                    dialog.setCurrentPercentage(randint(75, 85))
                    await sleep(0.001)
                    songData.sortNotes()
                    changedSongData[index] = songData
                    await sleep(0.001)

                for k, v in changedSongData.items():
                    self.songsData[k] = v
                dialog.totalProgress.set(i+1)

                showinfo("Applying tools",
                         "All selected files have been processed.")
            except CancelledError:
                raise
            except Exception as e:
                showerror("Applying tools error",
                          f'An error occurred while applying tools to files.\n{e.__class__.__name__}: {e}')
                logger.exception(e)
                dialogue.onCancel()
            finally:
                get_object('applyBtn')['state'] = 'normal'

        dialogue = ProgressDialog(self.toplevel, self)
        dialogue.d.set_title(f"Applying tools to {selectionLen} files")
        dialogue.totalMax = selectionLen
        dialogue.run(work)

    def collapseNotes(self, notes) -> None:
        layer = 0
        prevNote = Note()
        for note in notes:
            if note.tick == prevNote.tick:
                layer += 1
                note.layer = layer
            else:
                layer = 0
                note.layer = layer
                prevNote = note

    def imageToNotes(self, imgPath: str, width: int, height: int) -> list[Note]:
        img = Image.open(imgPath)
        img.thumbnail((width, height), Image.Resampling.NEAREST)
        width, height = img.size
        img = img.convert('RGBA')
        notes = []

        for i in range(width):
            for j in range(height):
                color = img.getpixel((i, j))
                assert isinstance(color, tuple)
                r, g, b, a = color
                if a <= 25:
                    continue
                nearestColor = Color(
                    'srgb', (r / 255, g / 255, b / 255)).closest(NBS_INST_NOTE_COLORS)
                inst = NBS_NOTE_COLORS_TO_INST[nearestColor.to_string(
                    hex=True)]
                notes.append(Note(i, j, inst, 0, 0))
        
        return notes
    
    def shiftNotes(self, notes: list[Note], x: int, y: int) -> None:
        for note in notes:
            note.tick += x
            note.layer += y

    def modifyHeaders(self, header):
        def setAttrFromStrVar(key: str, value: str):
            if value != '' and value.isdigit():
                try:
                    setattr(header, key, int(value))
                except ValueError:
                    print(f'Non-integer value: {value}')
        get_object = self.builder.get_object
        if not 'alternate' in get_object('headerAutosaveCheck').state():
            autoSave = self.headerAutosave.get()
            header.auto_save = autoSave
            if autoSave:
                setAttrFromStrVar('auto_save_time',
                                  self.headerAutosaveInterval.get())

        setAttrFromStrVar('minutes_spent', self.headerMinuteSpent.get())
        setAttrFromStrVar('left_clicks', self.headerLeftClicks.get())
        setAttrFromStrVar('right_clicks', self.headerRightClicks.get())
        setAttrFromStrVar('block_added', self.headerBlockAdded.get())
        setAttrFromStrVar('block_removed', self.headerBlockRemoved.get())

        if not 'alternate' in get_object('headerLoopCheck').state():
            loop = self.headerLoop.get()
            header.loop = loop
            if loop:
                setAttrFromStrVar('loop_max', self.headerLoopCount.get())
                setAttrFromStrVar('loop_start', self.headerLoopStart.get())


class DatapackExportDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/datapackexportdialog.ui'))

        self.d: Dialog = builder.get_object('dialog', master)

        button = builder.get_object('exportBtn')
        button.configure(command=self.export)
        if len(parent.fileTable.selection()) == 0:
            button["state"] = "disabled"

        def wnbsIDVaildate(P):
            isVaild = bool(re.match(r"^(\d|\w|[-_.])+$", P))
            button["state"] = "normal" if isVaild and (
                60 >= len(P) > 0) else "disabled"
            return isVaild

        self.entry = entry = builder.get_object('IDEntry')
        vcmd = (master.register(wnbsIDVaildate), '%P')
        entry.configure(validatecommand=vcmd)

        self.lyricsFilePath: tk.StringVar

        builder.connect_callbacks(self)
        builder.import_variables(self)

    def run(self):
        self.d.run()

    def export(self, _=None):
        self.d.close()
        fileTable = self.parent.fileTable
        index = fileTable.index(fileTable.selection()[0])

        path = askdirectory(title="Select folder to save")
        if path == '':
            return

        lyrics: Optional[str] = None

        try:
            with open(self.lyricsFilePath.get(), 'r', encoding='utf-8') as f:
                lyrics = f.read()
        except:
            pass

        exportDatapack(self.parent.songsData[index], os.path.join(
            path, self.entry.get()), self.entry.get(), 'wnbs', lyrics)


class ProgressDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        self.work: Callable

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/progressdialog.ui'))

        self.d: Dialog = builder.get_object('dialog1', master)
        self.d.toplevel.protocol(                   # type: ignore
            'WM_DELETE_WINDOW', self.onCancel)

        self.currentText: StringVar
        self.totalText: StringVar
        self.currentProgress: IntVar
        self.totalProgress: IntVar

        builder.connect_callbacks(self)
        builder.import_variables(self)

    @property
    def currentMax(self) -> int:
        return self.builder.get_object('currentProgressBar')['maximum']

    @currentMax.setter
    def currentMax(self, value: int) -> None:
        self.builder.get_object('currentProgressBar')['maximum'] = value

    @property
    def totalMax(self) -> int:
        try:
            return self.builder.get_object('totalProgressBar')['maximum']
        except Exception:
            return -1

    @totalMax.setter
    def totalMax(self, value: int) -> None:
        self.builder.get_object('totalProgressBar')['maximum'] = value

    def run(self, func=None):
        self.builder.get_object('dialog1', self.master).run()
        if func and asyncio.iscoroutinefunction(func):
            self.work = func
            self.d.toplevel.after(0, self.startWork)  # type: ignore

    def startWork(self) -> None:
        if self.totalProgress.get() >= self.totalMax:
            self.d.destroy()
            return
        asyncio.run(self.updateProgress())
        self.d.toplevel.after(0, self.startWork)  # type: ignore

    async def updateProgress(self) -> None:
        self.task = asyncio.create_task(self.work(dialog=self))
        while True:  # wait the async task finish
            done, _ = await asyncio.wait({self.task}, timeout=0)
            self.d.toplevel.update()  # type: ignore
            if self.task in done:
                await self.task
                break

    def setCurrentPercentage(self, value: int) -> None:
        self.currentProgress.set(round(self.currentMax * value / 100))

    def onCancel(self) -> None:
        try:
            allTasks = asyncio.all_tasks()
            for task in allTasks:
                task.cancel()
        except RuntimeError:  # if you have cancel the task it will raise RuntimeError
            pass
        self.d.destroy()


ExportDialogFunc = Callable[[NbsSong, str, ProgressDialog], Coroutine]


class ExportDialog:
    def __init__(self, master, parent, fileExt: str, title: Optional[str], progressTitle: str,
                 func: ExportDialogFunc, ui_file='ui/exportdialog.ui'):
        self.master = master
        self.parent = parent
        self.progressTitle = progressTitle
        self.fileExt = fileExt
        self.func = func

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path(ui_file))

        self.d: Dialog = builder.get_object('dialog', master)
        if title:
            self.d.set_title(title)
        builder.get_object('pathChooser').bind(
            '<<PathChooserPathChanged>>', self.pathChanged)

        self.exportMode: StringVar
        self.exportPath: StringVar

        builder.connect_callbacks(self)
        builder.import_variables(self)

        self.exportModeChanged()

        self.shouldCompactNotes = True

    def run(self):
        self.d.run()

    def exportModeChanged(self):
        self.isFolderMode = self.exportMode.get() == 'folder'
        self.builder.get_object('pathChooser').configure(
            state='normal' if self.isFolderMode else 'disabled')
        self.pathChanged()

    def pathChanged(self, _=None):
        self.builder.get_object('exportBtn')['state'] = 'normal' if (
            not self.isFolderMode) or (self.exportPath.get() != '') else 'disabled'

    def export(self, _=None):
        path = os.path
        fileTable: ttk.Treeview = self.parent.fileTable
        indexes = [fileTable.index(i) for i in fileTable.selection()]
        func = self.func

        if self.isFolderMode:
            self.pathChanged()
            if self.exportPath.get() != '':
                Path(self.exportPath.get()).mkdir(parents=True, exist_ok=True)
            else:
                return

        async def work(dialog: ProgressDialog):
            songsData = self.parent.songsData
            filePaths = self.parent.filePaths
            for i in indexes:
                dialog.totalProgress.set(i)
                dialog.totalText.set(f"Exporting {i+1} / {len(indexes)} files")
                dialog.currentProgress.set(0)
                origPath = filePaths[i]
                if not origPath:
                    origPath = asksaveasfilename(
                        filetypes=((self.fileExt+' files', self.fileExt),),
                        initialfile=path.basename(
                            songsData[i].header.import_name).rsplit('.', 1)[0],
                        defaultextension=self.fileExt)
                if not origPath:
                    if self.d.toplevel:
                        self.d.toplevel.after(
                            1, self.d.destroy)  # type: ignore
                    return
                baseName = path.basename(origPath)
                if baseName.endswith('.nbs'):
                    baseName = baseName[:-4]
                if not baseName.endswith(self.fileExt):
                    baseName += self.fileExt

                filePath = ''
                if not self.isFolderMode:
                    filePath = path.join(path.dirname(origPath), baseName)
                else:
                    filePath = path.join(self.exportPath.get(), baseName)
                try:
                    dialog.currentText.set(f"Current file: {filePath}")
                    # Prevent data from unintended changes
                    songData: NbsSong = deepcopy(songsData[i])
                    if self.shouldCompactNotes:
                        compactNotes(songData, True)
                    songData.correctData()
                    dialog.currentProgress.set(10)  # 10%
                    await func(songData, filePath, dialog)
                except CancelledError:
                    raise
                except Exception as e:
                    showerror("Exporting files error",
                              f'Cannot export file "{filePath}"\n{e.__class__.__name__}: {e}')
                    logger.exception(e)
            dialog.totalProgress.set(dialog.currentMax)

            self.d.toplevel.after(1, self.d.destroy)  # type: ignore

        dialogue = ProgressDialog(self.d.toplevel, self)
        dialogue.d.bind('<<DialogClose>>', lambda _: self.d.destroy())
        dialogue.d.set_title(self.progressTitle.format(len(indexes)))
        dialogue.totalMax = len(indexes)
        dialogue.run(work)


class MidiExportDialog(ExportDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent, '.mid', "MIDI exporting",
                         "Exporting {} files to MIDI...", nbs2midi)


class JsonExportDialog(ExportDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent, '.json', "JSON exporting",
                         "Exporting {} files to JSON...", self.nbs2json)

    async def nbs2json(self, data: NbsSong, filepath: str, dialog: ProgressDialog):
        if not filepath.endswith('.json'):
            filepath += '.json'

        dialog.currentProgress.set(25)  # 25%
        await sleep(0.001)

        notes = [note.__dict__ for note in data.notes]
        layers = [layer.__dict__ for layer in data.layers]
        insts = [inst.__dict__ for inst in data.customInsts]

        exportData = {'header': data.header.__dict__, 'notes': notes,
                      'layers': layers, 'custom_instruments': insts}

        dialog.currentProgress.set(60)  # 60%
        await sleep(0.001)

        with open(filepath, 'w', encoding='ascii') as f:
            json.dump(exportData, f, ensure_ascii=True, indent=4)

        dialog.currentProgress.set(90)  # 90%
        await sleep(0.001)


def checkFFmpeg(ps: str = '') -> bool:
    if not (which('ffmpeg') and which('ffprobe')):
        instructionMsg = ''
        if os.name == 'nt':
            instructionMsg = """
Make sure there are ffmpeg.exe and ffprobe.exe inside the ffmpeg/bin folder.
If not, you can download ffmpeg then put these two files in ffmpeg/bin folder."""
        elif os.name == 'posix':
            instructionMsg = """
Make sure the ffmpeg package is installed in the system.
Use "sudo apt install ffmpeg" command to install ffmpeg."""
        instructionMsg = "NBSTool can't find ffmpeg, which is required to render audio." + instructionMsg
        if ps:
            instructionMsg += '\n' + ps
        showwarning("ffmpeg not found", instructionMsg)
        return False
    else:
        return True


class AudioExportDialog(ExportDialog):
    def __init__(self, master, parent):
        self.formatVar: tk.StringVar
        self.sampleRateVar: tk.IntVar
        self.stereo: tk.BooleanVar
        self.includeLocked: tk.BooleanVar
        self.ignoreMissingSounds: tk.BooleanVar

        super().__init__(master, parent, '.wav', None,
                         "Exporting {} files to audio...", self.audioExport, 'ui/audioexportdialog.ui')

        formatCombo = self.builder.get_object('formatCombo')
        formatCombo.current('wav')
        self.formatVar.trace_add('write', self.formatChanged)

        samplingRateCombo = self.builder.get_object('samplingRateCombo')
        samplingRateCombo.set(44100)

        self.stereo.set(True)  # type: ignore
        self.includeLocked.set(True)  # type: ignore

        checkFFmpeg()

    def formatChanged(self, *args):
        self.fileExt = '.' + self.builder.get_object('formatCombo').current()

    async def audioExport(self, data: NbsSong, filepath: str, dialog: ProgressDialog):
        fmt = self.builder.get_object('formatCombo').current()
        samplingRate = self.builder.get_object('samplingRateCombo').current()

        channels = int(self.stereo.get()) + 1  # type: ignore
        includeLocked = self.includeLocked.get()  # type: ignore
        ignoreMissingSounds = self.ignoreMissingSounds.get()  # type: ignore

        await nbs2audio(data, filepath, dialog, fmt, samplingRate,
                        channels, exclude_locked_layers=not includeLocked,
                        ignore_missing_instruments=ignoreMissingSounds)


class ImpulseExportDialog(ExportDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent, '.it', "Impulse Tracker exporting",
                         "Exporting {} files to Impulse Tracker format (.it)...", nbs2it)
        self.shouldCompactNotes = False

        if not checkFFmpeg():
            self.d.close()
            self.d.toplevel.after(1, self.d.destroy)  # type: ignore


def parseFilePaths(string: str) -> tuple:
    strLen = len(string)
    ret: list[str] = []
    filePath = ''
    isQuoted = False
    for i, char in enumerate(string):
        i: int
        char: str
        if char == '(':
            isQuoted = True
        elif char == ')':
            isQuoted = False
        elif i+1 == strLen and filePath != '':
            ret.append(filePath)
        elif char.isspace():
            if isQuoted:
                filePath += char
            elif filePath != '':
                ret.append(filePath)
                filePath = ''
        else:
            filePath += char
    return tuple(ret)


ImportDialogFunc = Callable[[str, ProgressDialog],
                            Coroutine[Any, Any, NbsSong]]


class ImportDialog:
    def __init__(self, master, parent, fileExts: tuple, title: Optional[str], progressTitle: str,
                 func: ImportDialogFunc, ui_file='ui/importdialog.ui'):
        self.master = master
        self.parent = parent
        self.fileExts = fileExts
        self.title = title
        self.progressTitle = progressTitle
        self.func = func

        self.filePaths: StringVar

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path(ui_file))

        self.d: Dialog = builder.get_object('dialog', master)
        if title:
            self.d.set_title(title)

        builder.connect_callbacks(self)
        builder.import_variables(self)

        self.filePaths.trace_add("write", self.pathChanged)

    def run(self):
        self.d.run()

    def browse(self):
        paths = askopenfilenames(filetypes=self.fileExts)

        self.filePaths.set(str(paths))

    def pathChanged(self, *args):
        self.builder.get_object('importBtn')['state'] = 'normal' if (
            self.filePaths.get() != '') else 'disabled'

    def onImport(self, _=None):
        self.pathChanged()
        if self.filePaths.get() == '':
            self.pathChanged()
            return

        paths = literal_eval(self.filePaths.get())
        if isinstance(paths, str):
            paths = parseFilePaths(paths)
        fileCount = len(paths)

        async def work(dialog: ProgressDialog):
            songsData: list = self.parent.songsData
            filePaths: list = self.parent.filePaths
            for i, filePath in enumerate(paths):
                try:
                    dialog.totalProgress.set(i)
                    dialog.totalText.set(
                        f"Importing {i+1} / {fileCount} files")
                    dialog.currentProgress.set(0)
                    dialog.currentText.set(
                        f"Current file: {filePath}")
                    task = asyncio.create_task(self.func(filePath, dialog))
                    while True:
                        done, _ = await asyncio.wait({task}, timeout=0)
                        if task in done:
                            songData = task.result()
                            await task
                            break
                    if songData is None:
                        raise ImportError(
                            f"The file {filePath} is empty or cannot be imported.")
                    dialog.currentProgress.set(80)
                    await sleep(0.001)
                    songsData.append(songData)
                    filePaths.append('')
                    self.parent.addFileInfo('', songData)
                    await sleep(0.001)
                except CancelledError:
                    raise
                except Exception as e:
                    showerror("Importing file error",
                              f'Cannot import file "{filePath}"\n{e.__class__.__name__}: {e}')
                    logger.exception(e)
                    continue
                dialog.totalProgress.set(dialog.currentMax)
            # self.d.toplevel.after(1, self.d.destroy)

        dialogue = ProgressDialog(self.d.toplevel, self)
        # dialogue.d.bind('<<DialogClose>>', lambda _: self.d.destroy())
        dialogue.d.set_title(self.progressTitle.format(fileCount))
        dialogue.totalMax = fileCount
        dialogue.run(work)


class JsonImportDialog(ImportDialog):
    def __init__(self, master, parent):
        fileExts = (("JSON files", '*.json'), ('All files', '*'),)
        super().__init__(master, parent, fileExts, "Import from JSON files",
                         "Importing {} JSON files", self.convert)

    async def convert(self, filepath: str, dialog: ProgressDialog) -> NbsSong:
        j = {}
        with open(filepath, 'r', encoding='ascii') as f:
            j = json.load(f)
        validate(j, NBS_JSON_SCHEMA)

        if dialog:
            dialog.currentProgress.set(50)
            await sleep(0.001)

        nbs = NbsSong()
        header, notes, layers, customInsts = nbs.header, nbs.notes, nbs.layers, nbs.customInsts
        header.__dict__ = j['header']
        header.import_name = os.path.basename(filepath)
        for note in j['notes']:
            notes.append(Note(**note))
        for layer in j['layers']:
            layers.append(Layer(**layer))
        for inst in j['custom_instruments']:
            customInsts.append(Instrument(**inst))

        nbs.correctData()
        return nbs


class MuseScoreImportDialog(ImportDialog):
    def __init__(self, master, parent):
        self.autoExpand: BooleanVar
        self.expandMult: IntVar

        fileExts = (("MuseScore files", ('*.mscz', '*.mscx')),
                    ('All files', '*'),)
        super().__init__(master, parent, fileExts, None,
                         "Importing {} MIDI files", self.convert, "ui/musescoreimportdialog.ui")

        self.autoExpand.set(True)

    async def convert(self, filepath: str, dialog: ProgressDialog):
        return await musescore2nbs(
            filepath, self.expandMult.get(), self.autoExpand.get(), dialog)

    def autoExpandChanged(self):
        self.builder.get_object('expandScale')[
            'state'] = 'disabled' if self.autoExpand.get() else 'normal'


class MidiImportDialog(ImportDialog):
    def __init__(self, master, parent):
        self.autoExpand: BooleanVar
        self.expandMult: IntVar
        self.importDuration: BooleanVar
        self.durationSpacing: IntVar
        self.trailingVelocity: IntVar
        self.trailingVelAsPercent: BooleanVar
        self.importVelocity: BooleanVar
        self.importPitch: BooleanVar
        self.importPanning: BooleanVar
        self.trailingNoteVelMode: StringVar
        self.applyStereo: BooleanVar

        fileExts = (("Musical Instrument Digital Interface (MIDI) files",
                    ('*.mid', '*.midi')), ('All files', '*'),)
        super().__init__(master, parent, fileExts, None,
                         "Importing {} MIDI files", self.convert, "ui/midiimportdialog.ui")

        self.autoExpand.set(True)
        self.importPitch.set(True)
        self.importPanning.set(True)
        self.importVelocity.set(True)
        self.applyStereo.set(True)
        self.trailingNoteVelMode.set('fadeOut')
        self.trailingVelAsPercent.set(True)

    async def convert(self, filepath: str, dialog: ProgressDialog) -> NbsSong:
        expandMult = int(self.expandMult.get()
                         ) if not self.autoExpand.get() else 0
        fadeOut = self.trailingNoteVelMode.get() == 'fadeOut'
        return await midi2nbs(filepath, expandMult, self.importDuration.get(),
                              self.durationSpacing.get(), self.trailingVelocity.get(), self.trailingVelAsPercent.get(
        ), fadeOut, self.applyStereo.get(), self.importVelocity.get(),
            self.importPanning.get(), self.importPitch.get(),
            dialog)

    def autoExpandChanged(self):
        self.builder.get_object('expandScale')[
            'state'] = 'disabled' if self.autoExpand.get() else 'normal'

    def trailingNoteVelModeChanged(self):
        fixedVelocity = self.trailingNoteVelMode.get() == 'fixed'
        self.builder.get_object('trailingVelocitySpin')[
            'state'] = 'normal' if fixedVelocity else 'disabled'
        self.builder.get_object('trailingVelPercentCheck')[
            'state'] = 'normal' if fixedVelocity else 'disabled'

    def importDurationChanged(self):
        self.builder.get_object('durationSpacingLabel')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        self.builder.get_object('durationSpacingSpin')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        self.builder.get_object('trailingVelocityLabel')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        self.builder.get_object('fixedTrailingVelRadio')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        self.builder.get_object('fadeOutTrailingVelRadio')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        self.builder.get_object('applyStereoCheck')[
            'state'] = 'normal' if self.importDuration.get() else 'disabled'
        if self.importDuration.get():
            self.trailingNoteVelModeChanged()
        else:
            self.builder.get_object('trailingVelocitySpin')[
                'state'] = 'disabled'
            self.builder.get_object('trailingVelPercentCheck')[
                'state'] = 'disabled'

    def applyStereoChanged(self):
        pass


class AboutDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/aboutdialog.ui'))

        self.d: Dialog = builder.get_object('dialog', master)
        builder.connect_callbacks(self)
        self.d.run()

    def github(self):
        webbrowser.open_new_tab("https://github.com/IoeCmcomc/NBSTool")


class FlexCheckbutton(tk.Checkbutton):
    def __init__(self, *args, **kwargs):
        self.multiline: bool
        self.anchor: Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw']
        self.justify: Literal['left', 'center', 'right']

        okwargs = dict(kwargs)
        if 'multiline' in kwargs:
            self.multiline = kwargs['multiline']
            del okwargs['multiline']
        else:
            self.multiline = True

        tk.Checkbutton.__init__(self, *args, **okwargs)

        self.text = kwargs['text']
        if 'anchor' in kwargs:
            self.anchor = kwargs['anchor']
        else:
            self.anchor = 'w'
        self['anchor'] = self.anchor

        if 'justify' in kwargs:
            self.justify = kwargs['justify']
        else:
            self.justify = 'left'
        self['justify'] = self.justify

        if self.multiline:
            self.bind("<Configure>", lambda event: self.configure(width=event.width-10,
                                                                  justify=self.justify, anchor=self.anchor, wraplength=event.width-20, text=self.text+' '*999))


def centerToplevel(obj, width=None, height=None, mwidth=None, mheight=None):
    # Credit: https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python/56913005#56913005
    def get_curr_screen_size():
        """
        Workaround to get the size of the current screen in a multi-screen setup.

        Returns:
            Size(Tuple): (width, height)
        """
        root = tk.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        size = (root.winfo_width(), root.winfo_height(),)
        root.destroy()
        return size

    screenWidth, screenHeight = get_curr_screen_size()

    windowWidth = width or obj.winfo_width()
    windowHeight = height or obj.winfo_height()

    winPosX = int(screenWidth / 2 - windowWidth / 2)
    winPosY = int(screenHeight / 2.3 - windowHeight / 2)

    obj.minsize(mwidth or obj.winfo_width(), mheight or obj.winfo_height())
    obj.geometry(f"{windowHeight}x{windowHeight}+{winPosX}+{winPosY}")
    # obj.update()
    obj.update_idletasks()


def compactNotes(data: NbsSong, groupPerc: Union[int, BooleanVar] = 1) -> None:
    groupPerc = bool(groupPerc)
    prevNote = Note()
    outerLayer = 0
    insts = data.usedInsts[0]
    if not groupPerc:
        insts += data.usedInsts[1]
    for inst in insts:  # Arrange notes by instruments first
        innerLayer = localLayer = c = 0
        for note in data.notes:
            if note.inst == inst:
                c += 1
                if note.tick == prevNote.tick:
                    localLayer += 1
                    innerLayer = max(innerLayer, localLayer)
                    note.layer = localLayer + outerLayer
                else:
                    localLayer = 0
                    note.layer = localLayer + outerLayer
                    prevNote = note
        outerLayer += innerLayer + 1

    if groupPerc:  # Treat percussions as one instrument
        innerLayer = localLayer = c = 0
        for note in data.notes:
            if note.inst in data.usedInsts[1]:
                c += 1
                if note.tick == prevNote.tick:
                    localLayer += 1
                    innerLayer = max(innerLayer, localLayer)
                    note.layer = localLayer + outerLayer
                else:
                    localLayer = 0
                    note.layer = localLayer + outerLayer
                    prevNote = note
        outerLayer += innerLayer + 1
    data.maxLayer = outerLayer - 1


# Source: https://stackoverflow.com/a/37095855
def to_signed_32(n: int) -> int:
    n &= 0xffffffff
    return (n ^ 0x80000000) - 0x80000000


def exportDatapack(data: NbsSong, path: str, _bname: str, mode=None, lyrics=None):
    def writejson(path, jsout):
        with open(path, 'w') as f:
            json.dump(jsout, f, ensure_ascii=True)

    def writemcfunction(path, text):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    def makeFolderTree(inp):
        _makeFolderTree(inp, [])

    def _makeFolderTree(inp, a: list):
        if isinstance(inp, (tuple, set)):
            for el in inp:
                _makeFolderTree(el, copy(a))
        elif isinstance(inp, dict):
            for k, v in inp.items():
                _makeFolderTree(v, a + [k])
        elif isinstance(inp, str):
            p = os.path.join(*a, inp)
            print(p)
            os.makedirs(p, exist_ok=True)
        else:
            return

    path = os.path.join(*os.path.normpath(path).split())
    bname: str = ''
    if _bname:
        bname = _bname
    else:
        bname = os.path.basename(path)

    data.correctData()

    lyrics_inst = 0
    if lyrics:
        lyrics_layer = next((i for i, x in enumerate(
            data.layers) if 'lyric' in x.name.lower()), -1)
        lyrics_inst = next((x.inst for i, x in enumerate(
            data.notes) if x.layer == lyrics_layer), -1)

    compactNotes(data, groupPerc=False)
    data.correctData()

    instruments = VANILLA_INSTS + data.customInsts
    layers = data.layers

    instLayers = {}
    for note in data.notes:
        if note.inst not in instLayers:
            instLayers[note.inst] = [note.layer]
        elif note.layer not in instLayers[note.inst]:
            instLayers[note.inst].append(note.layer)

    scoreObj = bname[:50]
    speed = int(min(data.header.tempo * 4, 120))
    length = data.header.length

    makeFolderTree(
        {path: {
            'data': {
                bname: {
                    'functions': {
                        'notes',
                        'tree',
                    },
                },
                'minecraft': {
                    'tags': 'functions',
                },
            },
        },
        }
    )

    captions: Optional[Deque] = None
    lyrics_uuid = None
    uuid_arr_str = ''
    lyrics_layer: int = -1
    if lyrics:
        captions = lyric2captions(lyrics)
        lyrics_uuid = uuid.uuid4()
        uuid_int = lyrics_uuid.int
        # Source: https://stackoverflow.com/a/32053256/12682038
        uuid_array = ((uuid_int >> x) &
                      0xFFFFFFFF for x in reversed(range(0, 128, 32)))
        uuid_arr_str = ', '.join(str(to_signed_32(num)) for num in uuid_array)
        lyrics_layer = next((i for i, x in enumerate(
            layers) if 'lyric' in x.name.lower()), -1)

    writejson(os.path.join(path, 'pack.mcmeta'), {"pack": {
        "description": "Note block song datapack made with NBSTool.", "pack_format": 8}})
    writejson(os.path.join(path, 'data', 'minecraft', 'tags', 'functions',
                           'load.json'), jsout={"values": ["{}:load".format(bname)]})
    writejson(os.path.join(path, 'data', 'minecraft', 'tags', 'functions',
                           'tick.json'), jsout={"values": ["{}:tick".format(bname)]})

    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'load.mcfunction'),
                    """scoreboard objectives add {0} dummy
scoreboard objectives add {0}_t dummy
scoreboard players set speed {0} {1}""".format(scoreObj, speed))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'tick.mcfunction'),
                    """execute as @a[tag={0}] run scoreboard players operation @s {0} += speed {0}
execute as @a[tag={0}] run function {1}:tree/0_{2}
execute as @e[type=armor_stand, tag={3}_WNBS_Marker] at @s unless block ~ ~-1 ~ minecraft:note_block run kill @s""".format(scoreObj, bname, 2**(floor(log2(length))+1)-1, scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'play.mcfunction'),
                    """tag @s add {0}
scoreboard players set @s {0}_t -1
""".format(scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'pause.mcfunction'),
                    "tag @s remove {}".format(scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'stop.mcfunction'),
                    """tag @s remove {0}
scoreboard players reset @s {0}
scoreboard players reset @s {0}_t
data modify entity {1} CustomName set value ''""".format(scoreObj, lyrics_uuid))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'uninstall.mcfunction'),
                    """scoreboard objectives remove {0}
scoreboard objectives remove {0}_t""".format(scoreObj))

    text = ''
    for k, v in instLayers.items():
        for i in range(len(v)):
            text += 'execute run give @s minecraft:armor_stand{{display: {{Name: "{{\\"text\\":\\"{}\\"}}" }}, EntityTag: {{Marker: 1b, NoGravity:1b, Invisible: 1b, Tags: ["{}_WNBS_Marker"], CustomName: "{{\\"text\\":\\"{}\\"}}" }} }}\n'.format(
                    "{}-{}".format(instruments[k].sound_id,
                                   i), scoreObj, "{}-{}".format(k, i)
            )
    if lyrics:
        assert not uuid_arr_str is None
        text += f'execute run give @s minecraft:armor_stand{{display: {{Name: "{{\\"text\\":\\"lyrics\\"}}" }}, EntityTag: {{Marker: 1b, NoGravity:1b, Invisible: 1b, Tags: ["{scoreObj}_WNBS_Marker"], UUID: [I;{uuid_arr_str}], CustomName: "{{\\"text\\":\\"\\"}}", CustomNameVisible: 1b }} }}\n'
    writemcfunction(os.path.join(path, 'data', bname,
                                 'functions', 'give.mcfunction'), text)

    tick = -1
    colNotes = {tick: []}
    for note in data.notes:
        while note.tick != tick:
            tick += 1
            colNotes[tick] = []
        colNotes[tick].append(note)

    for tick in range(length):
        text = ""
        if tick in colNotes:
            currNotes = colNotes[tick]
            for note in currNotes:
                if note.inst != lyrics_inst:
                    text += \
                        """execute as @e[type=armor_stand, tag={obj}_WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run setblock ~ ~ ~ minecraft:note_block[instrument={instname},note={key}] replace
execute as @e[type=armor_stand, tag={obj}_WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:redstone_block replace minecraft:air
execute as @e[type=armor_stand, tag={obj}_WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:air replace minecraft:redstone_block
""".format(obj=scoreObj, tick=tick, inst=note.inst, order=instLayers[note.inst].index(note.layer), instname=instruments[note.inst].sound_id, key=max(33, min(57, note.key)) - 33)
                else:
                    if captions:
                        caption = captions.popleft()
                        component = [
                            "",
                            {
                                "text": caption[0],
                                "color": "yellow",
                                "bold": True,
                            },
                            {
                                "text": caption[1],
                            }
                        ]
                        raw_text = json.dumps(component, ensure_ascii=False)
                        text += f"data modify entity {lyrics_uuid} CustomName set value '{raw_text}'\n"

        if tick < length-1:
            text += "scoreboard players set @s {}_t {}".format(
                scoreObj, tick)
        else:
            text += "execute run function {}:stop".format(bname)
        if text != "":
            writemcfunction(os.path.join(
                path, 'data', bname, 'functions', 'notes', str(tick)+'.mcfunction'), text)

    steps = floor(log2(length)) + 1
    pow = 2**steps
    for step in range(steps):
        searchrange = floor(pow / (2**step))
        segments = floor(pow / searchrange)
        for segment in range(segments):
            text = ""
            half = floor(searchrange / 2)
            lower = searchrange * segment

            min1 = lower
            max1 = lower + half - 1
            min2 = lower + half
            max2 = lower + searchrange - 1

            if min1 <= length:
                if step == steps-1:  # Last step, play the tick
                    try:
                        if len(colNotes[min1]) > 0:
                            text += "execute as @s[scores={{{0}={1}..{2}, {0}_t=..{3}}}] run function {4}:notes/{5}\n".format(
                                scoreObj, min1*80, (max1+1)*80+160, min1-1, bname, min1)
                    except KeyError:
                        pass
                    if min2 <= length:
                        try:
                            if len(colNotes[min2]) > 0:
                                text += "execute as @s[scores={{{0}={1}..{2}, {0}_t=..{3}}}] run function {4}:notes/{5}".format(
                                    scoreObj, min2*80, (max2+1)*80+160, min2-1, bname, min2)
                        except KeyError:
                            pass
                else:  # Don't play yet, refine the search
                    for i in range(min1, min(max1, length)+1):
                        try:
                            if len(colNotes[i]) > 0:
                                text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}\n".format(
                                    scoreObj, min1*80, (max1+1)*80+160, bname, min1, max1)
                                break
                        except KeyError:
                            break
                    for i in range(min2, min(max2, length)+1):
                        try:
                            if len(colNotes[i]) > 0:
                                text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}".format(
                                    scoreObj, min2*80, (max2+2)*80+160, bname, min2, max2)
                                break
                        except KeyError:
                            break
                if text != "":
                    writemcfunction(os.path.join(
                        path, 'data', bname, 'functions', 'tree', '{}_{}.mcfunction'.format(min1, max2)), text)
            else:
                break


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: Union[str, int]
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage())


logger.add(resource_path("logs", "latest.log"),
           retention=10, compression='bz2')
logging.basicConfig(handlers=[InterceptHandler()],
                    level=logging.INFO, force=True)

showwarning_ = warnings.showwarning


def _showwarning(message, *args, **kwargs):
    logger.warning(message)
    showwarning_(message, *args, **kwargs)


warnings.showwarning = _showwarning


@logger.catch
def main() -> None:
    logger.info("NBSTool v{}", __version__)
    logger.info("Platform: {}", platform.platform())
    logger.info("Python: {}", sys.version)
    logger.info("Architecture: {}", "64-bit" if sys.maxsize >
                2**32 else "32-bit")
    if '__compiled__' in globals():
        logger.info("Running in Nuitka-compiled mode")
        logger.info("Nuitka version: {}", version('nuitka'))
    logger.info("Resource path: {}", resource_path())
    if _ffmpeg_path := which('ffmpeg'):
        logger.info("ffmpeg path: {}", _ffmpeg_path)
    else:
        logger.warning("ffmpeg not found; audio and .it export will not work")
    if _ffprobe_path := which('ffprobe'):
        logger.info("ffprobe path: {}", _ffprobe_path)
    else:
        logger.warning("ffprobe not found; audio and .it export will not work")

    app = MainWindow()

    if len(sys.argv) == 2:
        app.addFiles(paths=[sys.argv[1], ])

    app.mainwin.mainloop()


if __name__ == "__main__":
    main()
