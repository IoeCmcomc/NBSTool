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


import sys
import os
import operator
import webbrowser
import copy
import traceback
import re
import json
import asyncio

from pathlib import Path
from ast import literal_eval

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory, askopenfilenames

import pygubu
from pygubu import Builder
from pygubu.widgets.dialog import Dialog
# Explict import for PyInstaller
from pygubu.builder import ttkstdwidgets, tkstdwidgets
from pygubu.builder.widgets import tkscrollbarhelper, dialog, pathchooserinput
import customwidgets

from time import time
from pprint import pprint
from random import randrange, randint
from math import floor, log2
from datetime import timedelta
from copy import deepcopy

from PIL import Image, ImageTk

from nbsio import NBS_VERSION, NbsSong
from ncfio import writencf
from nbs2midi import nbs2midi
from musescore2nbs import musescore2nbs

vaniNoteSounds = [
    {'filename': 'harp.ogg', 'name': 'harp'},
    {'filename': 'dbass.ogg', 'name': 'bass'},
    {'filename': 'bdrum.ogg', 'name': 'basedrum'},
    {'filename': 'sdrum.ogg', 'name': 'snare'},
    {'filename': 'click.ogg', 'name': 'hat'},
    {'filename': 'guitar.ogg', 'name': 'guitar'},
    {'filename': 'flute.ogg', 'name': 'flute'},
    {'filename': 'bell.ogg', 'name': 'bell'},
    {'filename': 'icechime.ogg', 'name': 'chime'},
    {'filename': 'xylobone.ogg', 'name': 'xylophone'},
    {'filename': 'iron_xylophone.ogg', 'name': 'iron_xylophone'},
    {'filename': 'cow_bell.ogg', 'name': 'cow_bell'},
    {'filename': 'didgeridoo.ogg', 'name': 'didgeridoo'},
    {'filename': 'bit.ogg', 'name': 'bit'},
    {'filename': 'banjo.ogg', 'name': 'banjo'},
    {'filename': 'pling.ogg', 'name': 'pling'}
]

globalIncVar = 0

def resource_path(*args):
    if getattr(sys, 'frozen', False):
        r = os.path.join(sys._MEIPASS, *args)
    else:
        r = os.path.join(os.path.abspath('.'), *args)
    return r


class MainWindow():
    def __init__(self):
        builder: Builder = pygubu.Builder()
        self.builder: Builder = builder
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/toplevel.ui'))
        self.toplevel: tk.Toplevel = builder.get_object('toplevel')
        self.mainwin: tk.Frame = builder.get_object('mainFrame')
        style = ttk.Style(self.toplevel)
        style.layout('Barless.TNotebook.Tab', []) # turn off tabs
        style.configure('Barless.TNotebook', borderwidth=0, highlightthickness=0)

        self.fileTable: ttk.Treeview = builder.get_object('fileTable')
        applyBtn = builder.get_object('applyBtn')

        self.toplevel.title("NBS Tool")
        centerToplevel(self.toplevel)

        self.initMenuBar()

        builder.import_variables(self)
        builder.connect_callbacks(self)

        self.initFormatTab()
        self.initHeaderTab()
        self.initFlipTab()
        self.initArrangeTab()
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
                self.updateHeaderNotebook([fileTable.index(item) for item in selection])
                applyBtn["state"] = "normal"
            else:
                builder.get_object('fileMenu').entryconfig(1, state="disabled")
                builder.get_object('saveFilesBtn')["state"] = "disabled"
                builder.get_object('removeEntriesBtn')["state"] = "disabled"
                builder.get_object('headerNotebook').select(0)
                self.selectedFilesVerStr.set("No file are selected.")
                applyBtn["state"] = "disabled"
            exportMenu: tk.Menu = builder.get_object('exportMenu')
            exportMenu.entryconfig(0, state="normal" if selectionLen == 1 else "disable")
            exportMenu.entryconfig(1, state="normal" if selectionNotEmpty else "disable")

        self.fileTable.bind("<<TreeviewSelect>>", on_fileTable_select)

        self.mainwin.lift()
        self.mainwin.focus_force()
        self.mainwin.grab_set()
        self.mainwin.grab_release()

        self.VERSION = '1.0.0'
        self.filePaths = []
        self.songsData = []
        self.selectedFilesVersion = -1

    def isInteger(self, value) -> bool:
        print("isInteger", value, value == '' or value.isdigit())
        return value == '' or value.isdigit()

    def getSelectedFilesVersion(self, selection: tuple) -> int:
        fileVersion = -1
        for i in selection:
            header = self.songsData[i].header
            ver: int = header.file_version
            if (ver != fileVersion) and (fileVersion != -1):
                return -1
            else:
                fileVersion = ver
        return fileVersion

    def updateHeaderNotebook(self, selection: tuple) -> None:
        def updateCheckbutton(i: int, var: tk.StringVar, widget: ttk.Checkbutton, value: bool) -> bool:
            ret = (i > 0) and (var.get() != value)
            if ret:
                widget.state(['alternate'])
            else:
                var.set(value)
            return not ret

        def updateSpinbox(i: int, var: tk.StringVar, value: int) -> None:
            var.set('' if ((i > 0) and (var.get() != str(value))) else value)

        get_object = self.builder.get_object
        notebook: ttk.Notebook = self.builder.get_object('headerNotebook')
        fileVersion = self.getSelectedFilesVersion(selection)
        if fileVersion == -1:
            notebook.select(0)
            self.selectedFilesVerStr.set("Selected file(s) don't have the same version number.")
            self.selectedFilesVersion = -1
            return
        self.selectedFilesVersion = fileVersion
        self.selectedFilesVerStr.set("Selected file(s) format version: {: >8}".format(fileVersion if fileVersion > 0 else 'Classic'))
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
                # Credit: https://stackoverflow.com/questions/24942760/is-there-a-way-to-gray-out-disable-a-tkinter-frame
                for child in get_object('headerLoopFrame').winfo_children():
                    child.configure(state='disable')

            autoSave = header.auto_save
            if updateCheckbutton(i, self.headerAutosave, get_object('headerAutosaveCheck'), autoSave):
                updateSpinbox(i, self.headerAutosaveInterval, header.auto_save_time)
            self.onAutosaveCheckBtn()

            updateSpinbox(i, self.headerMinuteSpent, header.minutes_spent)
            updateSpinbox(i, self.headerLeftClicks, header.left_clicks)
            updateSpinbox(i, self.headerRightClicks, header.right_clicks)
            updateSpinbox(i, self.headerBlockAdded, header.block_added)
            updateSpinbox(i, self.headerBlockRemoved, header.block_removed)

    def onAutosaveCheckBtn(self):
        label = self.builder.get_object('headerAutosaveLabel')
        spinbox = self.builder.get_object('headerAutosaveSpin')
        state = 'normal' if ((not 'alternate' in self.builder.get_object('headerAutosaveCheck').state()) and self.headerAutosave.get()) else 'disabled'
        label['state'] = state
        spinbox['state'] = state

    def onLoopCheckBtn(self):
        checkBox: ttk.Checkbutton = self.builder.get_object('headerLoopCheck')
        loop = self.headerLoop.get()
        state = 'normal' if ((not 'alternate' in self.builder.get_object('headerLoopCheck').state()) and self.headerLoop.get()) else 'disabled'
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
        global globalIncVar
        if filePath == '':
            globalIncVar += 1
            filePath = "[Not saved] ({})".format(globalIncVar)
        header = songData.header
        length = timedelta(seconds=floor(
            header['length'] / header['tempo'])) if header['length'] != None else "Not calculated"
        self.fileTable.insert("", 'end', text=filePath, values=(
            length, header.name, header.author, header.orig_author))

    def addFiles(self, _=None, paths=()):
        types = [("Note Block Studio files", '*.nbs'), ('All files', '*')]
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
                songData = NbsSong(filePath)
                self.songsData.append(songData)
            except Exception as e:
                showerror("Opening file error", 'Cannot open file "{}"\n{}: {}'.format(filePath, e.__class__.__name__, e))
                print(traceback.format_exc())
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
            else:
                path = askdirectory(title="Select folder to save")
            if path == '':
                return
            Path(path).mkdir(parents=True, exist_ok=True)
            self.disabledFileTable()
            for item in selection:
                try:
                    i = fileTable.index(item)
                    filePath = self.filePaths[i]
                    if filePath == '':
                        filePath = self.songsData[i].header.import_name.rsplit('.', 1)[0] + '.nbs'
                        savedPath = os.path.join(path, filePath)
                        fileTable.item(item, text=savedPath)
                        self.filePaths[i] = savedPath
                    self.songsData[i].write(os.path.join(path, os.path.basename(filePath)))
                except Exception as e:
                    showerror("Saving file error", 'Cannot save file "{}"\n{}: {}'.format(os.path.join(path, os.path.basename(filePath)), e.__class__.__name__, e))
                    print(traceback.format_exc())
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
                    filePath = self.songsData[i].header.import_name.rsplit('.', 1)[0] + '.nbs'
                    savedPath = os.path.join(path, filePath)
                    self.fileTable.item(items[i], text=savedPath)
                    self.filePaths[i] = savedPath
                self.songsData[i].write(os.path.join(path, os.path.basename(filePath)))
            except Exception as e:
                showerror("Saving file error", 'Cannot save file "{}"\n{}: {}'.format(os.path.join(path, os.path.basename(filePath)), e.__class__.__name__, e))
                print(traceback.format_exc())
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

    def callMuseScoreImportDialog(self):
        dialog = MuseScoreImportDialog(self.toplevel, self)
        dialog.run()
        del dialog

    def callDatapackExportDialog(self):
        dialog = DatapackExportDialog(self.toplevel, self)
        dialog.run()
        del dialog

    def callMidiExportDialog(self):
        dialog = MidiExportDialog(self.toplevel, self)
        dialog.run()
        del dialog

    def callAboutDialog(self):
        dialog = AboutDialog(self.toplevel, self)
        del dialog

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
                           self._on_treeview_left_click, add='+')

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
        self.builder.get_object('arrangeGroupPrec')['state'] = 'normal' if (self.arrangeMode.get() == 'instruments') else 'disabled'

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

        async def work(dialog: ProgressDialog = None):
            print("async work() start")
            try:
                notebook : ttk.Notebook = get_object('headerNotebook')
                headerModifiable = notebook.index(notebook.select()) == 1
                for i, index in enumerate(selectedIndexes):
                    dialog.totalProgress.set(i)
                    fileName = os.path.split(self.filePaths[i])[1]
                    dialog.currentText.set("Current file: {}".format(fileName))
                    dialog.totalText.set("Processing {} / {} files".format(i+1, selectionLen))
                    dialog.currentProgress.set(0)
                    songData: NbsSong = deepcopy(self.songsData[index])
                    dialog.setCurrentPercentage(randint(20, 25))
                    await asyncio.sleep(0.001)
                    dialog.currentMax = len(songData.notes)*2
                    length = songData.header['length']
                    maxLayer = songData.maxLayer

                    if headerModifiable:
                        self.modifyHeaders(songData.header)

                    if outputVersion > -1:
                        songData.header['file_version'] = outputVersion

                    if self.flipHorizontallyCheckVar.get() or self.flipVerticallyCheckVar.get():
                        for note in songData.notes:
                            if self.flipHorizontallyCheckVar.get():
                                note['tick'] = length - note['tick']
                            if self.flipVerticallyCheckVar.get():
                                note['layer'] = maxLayer - note['layer']
                            dialog.currentProgress.set(dialog.currentProgress.get()+1)
                    songData.sortNotes()

                    if self.arrangeMode.get() == 'collapse':
                        self.collapseNotes(songData.notes)
                    elif self.arrangeMode.get() == 'instruments':
                        compactNotes(songData, self.groupPerc)

                    dialog.setCurrentPercentage(randint(75, 85))
                    await asyncio.sleep(0.001)
                    songData.sortNotes()
                    changedSongData[index] = songData
                    await asyncio.sleep(0.001)

                for k, v in changedSongData.items():
                    self.songsData[k] = v
                dialog.totalProgress.set(i+1)
            except asyncio.CancelledError:
                raise
            finally:
                get_object('applyBtn')['state'] = 'normal'

        dialog = ProgressDialog(self.toplevel, self)
        dialog.d.set_title("Applying tools to {} files".format(selectionLen))
        dialog.totalMax = selectionLen
        dialog.run(work)

    def collapseNotes(self, notes) -> None:
        layer = 0
        prevNote = {'layer': -1, 'tick': -1}
        for note in notes:
            if note['tick'] == prevNote['tick']:
                layer += 1
                note['layer'] = layer
            else:
                layer = 0
                note['layer'] = layer
                prevNote = note

    def modifyHeaders(self, header):
        def setAttrFromStrVar(key: str, value: str):
            if value != '' and value.isdigit():
                try:
                    setattr(header, key, int(value))
                except:
                    print(f'Non-integer value: {value}')
        get_object = self.builder.get_object
        if not 'alternate' in get_object('headerAutosaveCheck').state():
            autoSave = self.headerAutosave.get()
            header.auto_save = autoSave
            if autoSave:
                setAttrFromStrVar('auto_save_time', self.headerAutosaveInterval.get())

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
            isVaild = bool(re.match("^(\d|\w|[-_.])+$", P))
            button["state"] = "normal" if isVaild and (
                14 >= len(P) > 0) else "disabled"
            return isVaild

        self.entry = entry = builder.get_object('IDEntry')
        vcmd = (master.register(wnbsIDVaildate), '%P')
        entry.configure(validatecommand=vcmd)

        builder.connect_callbacks(self)

    def run(self):
        self.d.run()

    def export(self, _=None):
        self.d.close()
        fileTable = self.parent.fileTable
        index = fileTable.index(fileTable.selection()[0])

        path = askdirectory(title="Select folder to save")
        if path == '':
            return
        exportDatapack(self.parent.songsData[index], os.path.join(
            path, self.entry.get()), self.entry.get(), 'wnbs')


class MidiExportDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/midiexportdialog.ui'))

        self.d: Dialog = builder.get_object('dialog', master)
        builder.get_object('pathChooser').bind('<<PathChooserPathChanged>>', self.pathChanged)

        builder.connect_callbacks(self)
        builder.import_variables(self)

        self.exportModeChanged()

    def run(self):
        self.d.run()

    def exportModeChanged(self):
        self.isFolderMode = self.exportMode.get() == 'folder'
        self.builder.get_object('pathChooser')['state'] = 'normal' if self.isFolderMode else 'disabled'
        self.pathChanged()

    def pathChanged(self, _=None):
        self.builder.get_object('exportBtn')['state'] = 'normal' if (not self.isFolderMode) or (self.exportPath.get() != '') else 'disabled'

    def export(self, _=None):
        path = os.path
        fileTable = self.parent.fileTable
        indexes = [fileTable.index(i) for i in fileTable.selection()]

        if self.isFolderMode:
            self.pathChanged()
            if self.exportPath.get() != '':
                Path(self.exportPath.get()).mkdir(parents=True, exist_ok=True)
            else:
                return

        async def work(dialog: ProgressDialog = None):
            try:
                songsData = self.parent.songsData
                filePaths = self.parent.filePaths
                for i in indexes:
                    dialog.totalProgress.set(i)
                    dialog.totalText.set("Exporting {} / {} files".format(i+1, len(indexes)))
                    dialog.currentProgress.set(0)
                    origPath = filePaths[i]
                    baseName = path.basename(origPath)
                    if baseName.endswith('.nbs'):
                        baseName = baseName[:-4]
                    baseName += '.mid'

                    filePath = ''
                    if not self.isFolderMode:
                        filePath = path.join(path.dirname(origPath), baseName)
                    else:
                        filePath = path.join(self.exportPath.get(), baseName)
                    try:
                        dialog.currentText.set("Current file: {}".format(filePath))
                        songData = deepcopy(songsData[i])
                        compactNotes(songData, True)
                        dialog.currentProgress.set(10) # 10%
                        await nbs2midi(songData, filePath, dialog)
                    except Exception as e:
                        showerror("Exporting file error", 'Cannot export file "{}"\n{}: {}'.format(filePath, e.__class__.__name__, e))
                        print(traceback.format_exc())
                dialog.totalProgress.set(dialog.currentMax)
            except asyncio.CancelledError:
                raise
            self.d.toplevel.after(1, self.d.destroy)

        dialog = ProgressDialog(self.d.toplevel, self)
        dialog.d.bind('<<DialogClose>>', lambda _: self.d.destroy())
        dialog.d.set_title("Exporting {} files to MIDI".format(len(indexes)))
        dialog.totalMax = len(indexes)
        dialog.run(work)


class ProgressDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        self.work = None

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/progressdialog.ui'))

        self.d: Dialog = builder.get_object('dialog1', master)
        self.d.toplevel.protocol('WM_DELETE_WINDOW', self.onCancel)

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
        return self.builder.get_object('totalProgressBar')['maximum']

    @totalMax.setter
    def totalMax(self, value: int) -> None:
        self.builder.get_object('totalProgressBar')['maximum'] = value

    def run(self, func=None):
        self.builder.get_object('dialog1', self.master).run()
        if asyncio.iscoroutinefunction(func):
            self.work = func
            self.d.toplevel.after(0, self.startWork)

    def startWork(self) -> None:
        if self.totalProgress.get() >= self.totalMax:
            self.d.destroy()
            return
        asyncio.run(self.updateProgress())
        print("startWork() about to after")
        self.d.toplevel.after(0, self.startWork)

    async def updateProgress(self) -> None:
        print("async updateProgressDialog() start")
        self.task = asyncio.create_task(self.work(dialog=self))
        while True: # wait the async task finish
            done, pending = await asyncio.wait({self.task}, timeout=0)
            self.d.toplevel.update()
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


def parseFilePaths(string: str) -> list:
    strLen = len(string)
    ret = []
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


class MuseScoreImportDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('ui/musescoreimportdialog.ui'))

        self.d: Dialog = builder.get_object('dialog', master)

        builder.connect_callbacks(self)
        builder.import_variables(self)

        self.autoExpand.set(True)
        self.filePaths.trace_add("write", self.pathChanged)

    def run(self):
        self.d.run()

    def browse(self):
        types = (("MuseScore files", ('*.mscz', '*.mscx')), ('All files', '*'),)
        paths = askopenfilenames(filetypes=types)

        self.filePaths.set(paths)

    def autoExpandChanged(self):
        self.builder.get_object('expandScale')['state'] = 'disabled' if self.autoExpand.get() else 'normal'

    def pathChanged(self, *args):
        self.builder.get_object('importBtn')['state'] = 'normal' if (self.filePaths.get() != '') or (self.exportPath.get() != '') else 'disabled'

    def onImport(self, _=None):
        fileTable = self.parent.fileTable

        if not self.autoExpand.get():
            self.pathChanged()
            if self.filePaths.get() == '':
                self.pathChanged()
                return

        paths = literal_eval(self.filePaths.get())
        if isinstance(paths, str):
            paths = parseFilePaths(paths)
        fileCount = len(paths)

        async def work(dialog: ProgressDialog = None):
            try:
                songsData: list = self.parent.songsData
                filePaths: list = self.parent.filePaths
                for i, filePath in enumerate(paths):
                    try:
                        dialog.totalProgress.set(i)
                        dialog.totalText.set("Importing {} / {} files".format(i+1, fileCount))
                        dialog.currentProgress.set(0)
                        dialog.currentText.set("Current file: {}".format(filePath))
                        task = asyncio.create_task(musescore2nbs(filePath, self.expandMult.get(), self.autoExpand.get(), dialog))
                        while True:
                            done, pending = await asyncio.wait({task}, timeout=0)
                            if task in done:
                                songData = task.result()
                                await task
                                break
                        if not songData:
                            raise Exception("The file {} cannot be read as a vaild XML file.".format(filePath))
                        dialog.currentProgress.set(80)
                        await asyncio.sleep(0.001)
                        songsData.append(songData)
                        filePaths.append('')
                        self.parent.addFileInfo('', songData)
                        await asyncio.sleep(0.001)
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        showerror("Importing file error", 'Cannot import file "{}"\n{}: {}'.format(filePath, e.__class__.__name__, e))
                        print(traceback.format_exc())
                        continue
                dialog.totalProgress.set(dialog.currentMax)
            except asyncio.CancelledError:
                raise
            # self.d.toplevel.after(1, self.d.destroy)

        dialog = ProgressDialog(self.d.toplevel, self)
        # dialog.d.bind('<<DialogClose>>', lambda _: self.d.destroy())
        dialog.d.set_title("Importing {} MuseScore files".format(fileCount))
        dialog.totalMax = fileCount
        dialog.run(work)


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

    ScreenWidth, ScreenHeight = get_curr_screen_size()

    WindowWidth = width or obj.winfo_width()
    WindowHeight = height or obj.winfo_height()

    WinPosX = int(ScreenWidth / 2 - WindowWidth / 2)
    WinPosY = int(ScreenHeight / 2.3 - WindowHeight / 2)

    obj.minsize(mwidth or obj.winfo_width(), mheight or obj.winfo_height())
    obj.geometry("{}x{}+{}+{}".format(WindowWidth,
                                      WindowHeight, WinPosX, WinPosY))
    # obj.update()
    obj.update_idletasks()


def compactNotes(data, groupPerc=1) -> None:
    groupPerc = bool(groupPerc)
    prevNote = {'layer': -1, 'tick': -1}
    outerLayer = 0
    it = data['usedInsts'][0]
    if not groupPerc:
        it += data['usedInsts'][1]
    for inst in it:
        #print('Instrument: {}'.format(inst))
        innerLayer = localLayer = c = 0
        #print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
        for note in data['notes']:
            if note['inst'] == inst:
                c += 1
                if note['tick'] == prevNote['tick']:
                    localLayer += 1
                    innerLayer = max(innerLayer, localLayer)
                    note['layer'] = localLayer + outerLayer
                else:
                    localLayer = 0
                    note['layer'] = localLayer + outerLayer
                    prevNote = note
                #print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
        outerLayer += innerLayer + 1
        #print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
    if groupPerc:
        innerLayer = localLayer = c = 0
        for note in data['notes']:
            if note['inst'] in data['usedInsts'][1]:
                c += 1
                if note['tick'] == prevNote['tick']:
                    localLayer += 1
                    innerLayer = max(innerLayer, localLayer)
                    note['layer'] = localLayer + outerLayer
                else:
                    localLayer = 0
                    note['layer'] = localLayer + outerLayer
                    prevNote = note
        outerLayer += innerLayer + 1
    data['maxLayer'] = outerLayer - 1

def exportDatapack(data, path, bname, mode=None, master=None):
    def writejson(path, jsout):
        with open(path, 'w') as f:
            json.dump(jsout, f, ensure_ascii=False)

    def writemcfunction(path, text):
        with open(path, 'w') as f:
            f.write(text)

    def makeFolderTree(inp, a=[]):
        if isinstance(inp, (tuple, set)):
            for el in inp:
                makeFolderTree(el, copy.copy(a))
        elif isinstance(inp, dict):
            for k, v in inp.items():
                makeFolderTree(v, a + [k])
        elif isinstance(inp, str):
            p = os.path.join(*a, inp)
            os.makedirs(p, exist_ok=True)
        else:
            return

    path = os.path.join(*os.path.normpath(path).split())
    bname = os.path.basename(path)

    data.correctData()
    compactNotes(data, groupPerc=False)

    noteSounds = vaniNoteSounds + data['customInsts']

    instLayers = {}
    for note in data['notes']:
        if note['inst'] not in instLayers:
            instLayers[note['inst']] = [note['layer']]
        elif note['layer'] not in instLayers[note['inst']]:
            instLayers[note['inst']].append(note['layer'])

    scoreObj = bname[:13]
    speed = int(min(data['header']['tempo'] * 4, 120))
    length = data['header']['length']

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

    writejson(os.path.join(path, 'pack.mcmeta'), {"pack": {
                "description": "Note block song datapack made with NBSTool.", "pack_format": 6}})
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
execute as @e[type=armor_stand, tag=WNBS_Marker] at @s unless block ~ ~-1 ~ minecraft:note_block run kill @s""".format(scoreObj, bname, 2**(floor(log2(length))+1)-1))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'play.mcfunction'),
                    """tag @s add {0}
scoreboard players set @s {0}_t -1
""".format(scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'pause.mcfunction'),
                    "tag @s remove {}".format(scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'stop.mcfunction'),
                    """tag @s remove {0}
scoreboard players reset @s {0}
scoreboard players reset @s {0}_t""".format(scoreObj))
    writemcfunction(os.path.join(path, 'data', bname, 'functions', 'uninstall.mcfunction'),
                    """scoreboard objectives remove {0}
scoreboard objectives remove {0}_t""".format(scoreObj))

    text = ''
    for k, v in instLayers.items():
        for i in range(len(v)):
            text += 'execute run give @s minecraft:armor_stand{{display: {{Name: "{{\\"text\\":\\"{}\\"}}" }}, EntityTag: {{Marker: 1b, NoGravity:1b, Invisible: 1b, Tags: ["WNBS_Marker"], CustomName: "{{\\"text\\":\\"{}\\"}}" }} }}\n'.format(
                    "{}-{}".format(noteSounds[k]['name'],
                                    i), "{}-{}".format(k, i)
            )
    writemcfunction(os.path.join(path, 'data', bname,
                                    'functions', 'give.mcfunction'), text)

    tick = 0
    colNotes = {tick: []}
    for note in data['notes']:
        colNotes[tick].append(note)
        while note['tick'] != tick:
            tick += 1
            colNotes[tick] = []

    for tick in range(length):
        text = ""
        if tick in colNotes:
            currNotes = colNotes[tick]
            for note in currNotes:
                text += \
                    """execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run setblock ~ ~ ~ minecraft:note_block[instrument={instname},note={key}] replace
execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:redstone_block replace minecraft:air
execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:air replace minecraft:redstone_block
""".format(obj=scoreObj, tick=tick, inst=note['inst'], order=instLayers[note['inst']].index(note['layer']), instname=noteSounds[note['inst']]['name'], key=max(33, min(57, note['key'])) - 33)
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
                                scoreObj, min1*80, (max1+1)*80+40, min1-1, bname, min1)
                    except KeyError:
                        break
                    if min2 <= length:
                        try:
                            if len(colNotes[min2]) > 0:
                                text += "execute as @s[scores={{{0}={1}..{2}, {0}_t=..{3}}}] run function {4}:notes/{5}".format(
                                    scoreObj, min2*80, (max2+1)*80+40, min2-1, bname, min2)
                        except KeyError:
                            break
                else:  # Don't play yet, refine the search
                    for i in range(min1, min(max1, length)+1):
                        try:
                            if len(colNotes[i]) > 0:
                                text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}\n".format(
                                    scoreObj, min1*80, (max1+1)*80+40, bname, min1, max1)
                                break
                        except KeyError:
                            break
                    for i in range(min2, min(max2, length)+1):
                        try:
                            if len(colNotes[i]) > 0:
                                text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}".format(
                                    scoreObj, min2*80, (max2+2)*80+40, bname, min2, max2)
                                break
                        except KeyError:
                            break
                if text != "":
                    writemcfunction(os.path.join(
                        path, 'data', bname, 'functions', 'tree', '{}_{}.mcfunction'.format(min1, max2)), text)
            else:
                break


if __name__ == "__main__":
    app = MainWindow()

    print(sys.argv)

    if len(sys.argv) == 2:
        app.addFiles(paths=[sys.argv[1], ])

    print('Ready')
    app.mainwin.mainloop()

    print("The app was closed.")
