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
# Version: 0.7.0
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

from pathlib import Path

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory, askopenfilenames

import pygubu
from pygubu import Builder

from time import time
from pprint import pprint
from random import randrange
from math import floor, log2
from datetime import timedelta

from PIL import Image, ImageTk

from nbsio import NBS_VERSION, NbsSong
from ncfio import writencf

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

# Credit: https://stackoverflow.com/questions/42474560/pyinstaller-single-exe-file-ico-image-in-title-of-tkinter-main-window
def resource_path(*args):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
        r = os.path.join(datadir, *args)
    else:
        try:
            r = os.path.join(sys._MEIPASS, *args)
        except Exception:
            r = os.path.join(os.path.abspath("."), *args)
    # print(r)
    return r


class MainWindow():
    def __init__(self):
        builder: Builder = pygubu.Builder()
        self.builder: Builder = builder
        builder.add_from_file(resource_path('toplevel.ui'))
        print("The following exception is not an error:")
        print('='*20)
        self.toplevel: tk.Toplevel = builder.get_object('toplevel')
        print('='*20)
        self.mainwin: tk.Frame = builder.get_object('mainFrame')

        self.fileTable: ttk.Treeview = builder.get_object('fileTable')
        applyBtn = builder.get_object('applyBtn')

        self.toplevel.title("NBS Tool")
        centerToplevel(self.toplevel)
        self.style = ttk.Style()
        # self.style.theme_use("default")
        try:
            self.style.theme_use("vista")
        except Exception as e:
            print(repr(e), e.__class__.__name__)
            try:
                self.style.theme_use("winnative")
            except Exception:
                pass

        self.initMenuBar()

        builder.import_variables(self)
        builder.connect_callbacks(self)

        self.initFormatTab()
        self.initFlipTab()
        self.initArrangeTab()
        self.windowBind()

        def on_fileTable_select(event):
            selectionLen = len(event.widget.selection())
            selectionNotEmpty = len(event.widget.selection()) > 0
            if selectionNotEmpty:
                builder.get_object('fileMenu').entryconfig(1, state="normal")
                builder.get_object('saveFilesBtn')["state"] = "normal"
                builder.get_object('removeEntriesBtn')["state"] = "normal"
                applyBtn["state"] = "normal"
            else:
                builder.get_object('fileMenu').entryconfig(1, state="disabled")
                builder.get_object('saveFilesBtn')["state"] = "disabled"
                builder.get_object('removeEntriesBtn')["state"] = "disabled"
                applyBtn["state"] = "disabled"
            exportMenu: tk.Menu = builder.get_object('exportMenu')
            exportMenu.entryconfig(0, state="normal" if selectionLen == 1 else "disable")
            exportMenu.entryconfig(1, state="normal" if selectionLen > 0 else "disable")

        self.fileTable.bind("<<TreeviewSelect>>", on_fileTable_select)

        self.mainwin.lift()
        self.mainwin.focus_force()
        self.mainwin.grab_set()
        self.mainwin.grab_release()

        self.VERSION = '0.7.0'
        self.filePaths = []
        self.songsData = []

    def initMenuBar(self):
        self.menuBar = menuBar = self.builder.get_object('menubar')
        self.toplevel.configure(menu=menuBar)

    def openFiles(self, _=None):
        self.fileTable.delete(*self.fileTable.get_children())
        self.filePaths.clear()
        self.songsData.clear()
        self.addFiles()

    def addFiles(self, _=None, paths=()):
        types = [('Note Block Studio files', '*.nbs'), ('All files', '*')]
        addedPaths = []
        if len(paths) > 0:
            addedPaths = paths
        else:
            addedPaths = askopenfilenames(filetypes=types)
        if len(addedPaths) == 0:
            return
        for filePath in addedPaths:
            try:
                songData = NbsSong(filePath)
                self.songsData.append(songData)
            except Exception:
                showerror("Reading file error",
                          "Cannot read or parse file: "+filePath)
                print(traceback.format_exc())
                continue
            header = songData.header
            length = timedelta(seconds=floor(
                header['length'] / header['tempo'])) if header['length'] != None else "Not calculated"
            name = header['name']
            author = header['author']
            orig_author = header['orig_author']
            self.fileTable.insert("", 'end', text=filePath, values=(
                length, name, author, orig_author))
            self.mainwin.update()
        self.filePaths.extend(addedPaths)
        self.builder.get_object('fileMenu').entryconfig(2, state="normal" if len(
            self.filePaths) > 0 else "disabled")

    def saveFiles(self, _=None):
        if len(self.filePaths) == 0:
            return
        fileTable = self.fileTable
        if len(selection := fileTable.selection()) > 0:
            if len(selection) == 1:
                filePath = os.path.basename(
                    self.filePaths[fileTable.index(selection[0])])
                types = [('Note Block Studio files', '*.nbs'),
                         ('All files', '*')]
                path = asksaveasfilename(
                    filetypes=types, initialfile=filePath, defaultextension=".nbs")
                self.songsData[fileTable.index(selection[0])].write(path)
                return
            else:
                path = askdirectory(title="Select folder to save")
            if path == '':
                return
            Path(path).mkdir(parents=True, exist_ok=True)
            for item in selection:
                i = fileTable.index(item)
                filePath = self.filePaths[i]
                self.songsData[i].write(os.path.join(
                    path, os.path.basename(filePath)))

    def saveAll(self, _=None):
        if len(self.filePaths) == 0:
            return
        path = askdirectory(title="Select folder to save")
        if path == '':
            return
        Path(path).mkdir(parents=True, exist_ok=True)
        for i, filePath in enumerate(self.filePaths):
            self.songsData[i].write(os.path.join(
                path, os.path.basename(filePath)))

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
            values=("(not selected)", '5', '4', '3', '2', '1', "Classic"))
        combobox.current(0)

    def initFlipTab(self):
        self.builder.get_object('flipHorizontallyCheck').deselect()
        self.builder.get_object('flipVerticallyCheck').deselect()

    def initArrangeTab(self):
        self.builder.get_object('notArrangeRadio').select()
        self.builder.get_object('arrangeGroupPrec').deselect()

    def callDatapackExportDialog(self):
        dialog = DatapackExportDialog(self.toplevel, self)
        dialog.run()
        del dialog

    def ToolsTabElements(self):
        fpadx, fpady = 10, 10
        padx, pady = 5, 0

        # Flip tool
        self.FlipToolFrame = tk.LabelFrame(self.ToolsTab, text="Flipping")
        self.FlipToolFrame.grid(
            row=0, column=0, sticky='nsew', padx=fpadx, pady=fpady)

        self.FlipToolMess = tk.Message(
            self.FlipToolFrame, anchor='w', text="Flip the note sequence horizontally (by tick), vertically (by layer) or both: ")
        self.FlipToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)

        self.var.tool.flip.vertical = tk.IntVar()
        self.FilpToolCheckV = tk.Checkbutton(
            self.FlipToolFrame, text="Vertically", variable=self.var.tool.flip.vertical)
        self.FilpToolCheckV.pack(side='left', padx=padx, pady=pady)

        self.var.tool.flip.horizontal = tk.IntVar()
        self.FilpToolCheckH = tk.Checkbutton(
            self.FlipToolFrame, text="Horizontally", variable=self.var.tool.flip.horizontal)
        self.FilpToolCheckH.pack(side='left', padx=padx, pady=pady)

        # Instrument tool
        self.InstToolFrame = tk.LabelFrame(
            self.ToolsTab, text="Note's instrument")
        self.InstToolFrame.grid(
            row=0, column=1, sticky='nsew', padx=fpadx, pady=fpady)

        self.InstToolMess = tk.Message(
            self.InstToolFrame, anchor='w', text="Change all note's instrument to:")
        self.InstToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)

        self.var.tool.opts = opts = [
            "(not applied)"] + [x['name'] for x in vaniNoteSounds] + ["Random"]
        self.InstToolCombox = ttk.Combobox(
            self.InstToolFrame, state='readonly', values=opts)
        self.InstToolCombox.current(0)
        self.InstToolCombox.pack(
            side='left', fill='both', expand=True, padx=padx, pady=pady)

        # Reduce tool
        self.ReduceToolFrame = tk.LabelFrame(self.ToolsTab, text="Reducing")
        self.ReduceToolFrame.grid(
            row=1, column=0, sticky='nsew', padx=fpadx, pady=fpady)

        self.ReduceToolMess = tk.Message(
            self.ReduceToolFrame, anchor='w', text="Delete as many note as possible to reduce file size.")
        self.ReduceToolMess.pack(
            fill='both', expand=True, padx=padx, pady=pady)

        self.var.tool.reduce.opt1 = tk.IntVar()
        self.CompactToolChkOpt1 = FlexCheckbutton(
            self.ReduceToolFrame, text="Delete duplicate notes", variable=self.var.tool.reduce.opt1, anchor='w')
        self.CompactToolChkOpt1.pack(padx=padx, pady=pady)

        self.var.tool.reduce.opt2 = tk.IntVar()
        self.CompactToolChkOpt2 = FlexCheckbutton(
            self.ReduceToolFrame, text=" In every tick, delete all notes except the first note", variable=self.var.tool.reduce.opt2, anchor='w')
        self.CompactToolChkOpt2.pack(padx=padx, pady=pady)

        self.var.tool.reduce.opt3 = tk.IntVar()
        self.CompactToolChkOpt3 = FlexCheckbutton(
            self.ReduceToolFrame, text=" In every tick, delete all notes except the last note", variable=self.var.tool.reduce.opt3, anchor='w')
        self.CompactToolChkOpt3.pack(padx=padx, pady=(pady, 10))

        # Compact tool
        self.CompactToolFrame = tk.LabelFrame(self.ToolsTab, text="Compacting")
        self.CompactToolFrame.grid(
            row=1, column=1, sticky='nsew', padx=fpadx, pady=fpady)

        self.CompactToolMess = tk.Message(
            self.CompactToolFrame, anchor='w', text="Remove spaces between notes vertically (by layer) and group them by instruments.")
        self.CompactToolMess.pack(
            fill='both', expand=True, padx=padx, pady=pady)

        self.var.tool.compact = tk.IntVar()
        self.CompactToolCheck = FlexCheckbutton(
            self.CompactToolFrame, text="Compact notes", variable=self.var.tool.compact, command=self.toggleCompactToolOpt, anchor='w')
        self.CompactToolCheck.pack(padx=padx, pady=pady)

        self.var.tool.compact.opt1 = tk.IntVar()
        self.CompactToolChkOpt1 = FlexCheckbutton(self.CompactToolFrame, text="Automatic separate notes by instruments (remain some spaces)",
                                                  variable=self.var.tool.compact.opt1, state='disabled', command=lambda: self.toggleCompactToolOpt(2), anchor='w')
        self.CompactToolChkOpt1.select()
        self.CompactToolChkOpt1.pack(padx=padx*5, pady=pady)

        self.var.tool.compact.opt1_1 = tk.IntVar()
        self.CompactToolChkOpt1_1 = FlexCheckbutton(
            self.CompactToolFrame, text="Group percussions into one layer", variable=self.var.tool.compact.opt1_1, state='disabled', anchor='w')
        self.CompactToolChkOpt1_1.select()
        self.CompactToolChkOpt1_1.pack(padx=padx*5*2, pady=pady)

        # 'Apply' botton
        self.ToolsTabButton = ttk.Button(
            self.ToolsTab, text="Apply", state='disabled', command=self.OnApplyTool)
        self.ToolsTabButton.grid(
            row=2, column=1, sticky='se', padx=fpadx, pady=fpady)

    def ExportTabElements(self):
        fpadx, fpady = 10, 10
        padx, pady = 5, 5

        # Upper frame
        self.ExpConfigFrame = tk.LabelFrame(self.ExportTab, text="Option")
        self.ExpConfigFrame.pack(
            fill='both', expand=True, padx=fpadx, pady=fpady)

        # "Select mode" frame
        self.ExpConfigGrp1 = tk.Frame(
            self.ExpConfigFrame, relief='groove', borderwidth=1)
        self.ExpConfigGrp1.pack(fill='both', padx=fpadx)

        self.ExpConfigLabel = tk.Label(
            self.ExpConfigGrp1, text="Export the song as a:", anchor='w')
        self.ExpConfigLabel.pack(side='left', fill='x', padx=padx, pady=pady)

        self.var.export.mode = tk.IntVar()
        self.ExpConfigMode1 = tk.Radiobutton(
            self.ExpConfigGrp1, text="File", variable=self.var.export.mode, value=1)
        self.ExpConfigMode1.pack(side='left', padx=padx, pady=pady)
        self.ExpConfigMode1.select()
        self.ExpConfigMode2 = tk.Radiobutton(
            self.ExpConfigGrp1, text="Datapack", variable=self.var.export.mode, value=0)
        self.ExpConfigMode2.pack(side='left', padx=padx, pady=pady)

        self.var.export.type.file = \
            [('Musical Instrument Digital files', '*.mid'),
             ('Nokia Composer Format', '*.txt'), ]
        self.var.export.type.dtp = ['Wireless note block song', 'other']
        self.ExpConfigCombox = ttk.Combobox(self.ExpConfigGrp1, state='readonly', values=[
                                            "{} ({})".format(tup[0], tup[1]) for tup in self.var.export.type.file])
        self.ExpConfigCombox.current(0)
        self.ExpConfigCombox.bind(
            "<<ComboboxSelected>>", self.toggleExpOptiGrp)
        self.ExpConfigCombox.pack(side='left', fill='x', padx=padx, pady=pady)

        self.var.export.mode.trace('w', self.toggleExpOptiGrp)

        ttk.Separator(self.ExpConfigFrame, orient="horizontal").pack(
            fill='x', expand=False, padx=padx*3, pady=pady)

        self.ExpOptiSW = StackingWidget(
            self.ExpConfigFrame, relief='groove', borderwidth=1)
        self.ExpOptiSW.pack(fill='both', expand=True, padx=fpadx)

        # Midi export options frame
        self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Midi')
        self.ExpOptiSW.pack('Midi', side='top', fill='both', expand=True)

        self.var.export.midi.opt1 = tk.IntVar()
        self.ExpMidi1Rad1 = tk.Radiobutton(
            self.ExpOptiSW['Midi'], text="Sort notes to MIDI tracks by note's layer", variable=self.var.export.midi.opt1, value=1)
        self.ExpMidi1Rad1.pack(anchor='nw', padx=padx, pady=(pady, 0))
        self.ExpMidi1Rad2 = tk.Radiobutton(
            self.ExpOptiSW['Midi'], text="Sort notes to MIDI tracks by note's instrument", variable=self.var.export.midi.opt1, value=0)
        self.ExpMidi1Rad2.pack(anchor='nw', padx=padx, pady=(0, pady))

        # Nokia export options frame
        self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'NCF')
        self.ExpOptiSW.pack('NCF', side='top', fill='both', expand=True)

        self.NCFOutput = ScrolledText(
            self.ExpOptiSW['NCF'], state="disabled", height=10)
        self.NCFOutput.pack(fill='both', expand=True)

        # 'Wireless song datapack' export options frame
        self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Wnbs')
        self.ExpOptiSW.pack('Wnbs', side='top', fill='both', expand=True)

        self.WnbsIDLabel = tk.Label(
            self.ExpOptiSW['Wnbs'], text="Unique name:")
        self.WnbsIDLabel.pack(anchor='nw', padx=padx, pady=pady)

        #vcmd = (self.register(self.onValidate), '%P')
        self.WnbsIDEntry = tk.Entry(self.ExpOptiSW['Wnbs'], validate="key",
                                    validatecommand=(self.register(lambda P: bool(re.match("^(\d|\w|[-_])*$", P))), '%P'))
        self.WnbsIDEntry.pack(anchor='nw', padx=padx, pady=pady)

        # Other export options frame
        self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Other')
        self.ExpOptiSW.pack('Other', side='top', fill='both', expand=True)

        self.ExpMusicLabel = tk.Label(
            self.ExpOptiSW['Other'], text="There is no option available.")
        self.ExpMusicLabel.pack(anchor='nw', padx=padx, pady=pady)

        # Output frame
        self.ExpOutputFrame = tk.LabelFrame(self.ExportTab, text="Output")
        self.ExpOutputFrame.pack(fill='both', padx=fpadx, pady=(0, fpady))

        self.ExpOutputLabel = tk.Label(
            self.ExpOutputFrame, text="File path:", anchor='w', width=8)
        self.ExpOutputLabel.pack(side='left', fill='x', padx=padx, pady=pady)

        self.ExpOutputEntry = tk.Entry(
            self.ExpOutputFrame, textvariable=self.exportFilePath)
        self.ExpOutputEntry.pack(side='left', fill='x', padx=padx, expand=True)

        self.ExpBrowseButton = ttk.Button(
            self.ExpOutputFrame, text="Browse", command=self.OnBrowseExp)
        self.ExpBrowseButton.pack(side='left', padx=padx, pady=pady)

        self.ExpSaveButton = ttk.Button(
            self.ExpOutputFrame, text="Export", command=self.OnExport)
        self.ExpSaveButton.pack(side='left', padx=padx, pady=pady)

    def footerElements(self):
        self.footerLabel = tk.Label(self.footer, text="Ready")
        self.footerLabel.pack(side='left', fill='x')
        self.var.footerLabel = 0

        self.sizegrip = ttk.Sizegrip(self.footer)
        self.sizegrip.pack(side='right', anchor='se')

        self.progressbar = ttk.Progressbar(
            self.footer, orient="horizontal", length=300, mode="determinate")
        self.progressbar["value"] = 0
        self.progressbar["maximum"] = 100
        # self.progressbar.start()
        # self.progressbar.stop()

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

        mainwin.bind_class("TNotebook", "<<NotebookTabChanged>>",
                           self._on_tab_changed)

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
        tree = event.widget
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
        tree = event.widget
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

    def toggleCompactToolOpt(self, id=1):
        if id <= 2:
            a = ((self.var.tool.compact.opt1.get() == 0)
                 or (self.var.tool.compact.get() == 0))
            self.CompactToolChkOpt1_1["state"] = "disable" if a is True else "normal"
            if id <= 1:
                self.CompactToolChkOpt1["state"] = "disable" if self.var.tool.compact.get(
                ) == 0 else "normal"

    def onArrangeModeChanged(self):
        self.builder.get_object('arrangeGroupPrec')['state'] = 'normal' if (self.arrangeMode.get() == 'instruments') else 'disabled'


    def applyTool(self):
        builder = self.builder
        builder.get_object('applyBtn')['state'] = 'disabled'
        fileTable = self.fileTable
        songsData = self.songsData
        selectedIndexes = (fileTable.index(item)
                               for item in fileTable.selection())

        outputVersion = -1

        if (formatComboIndex := builder.get_object('formatCombo').current()) > 0:
            outputVersion = (NBS_VERSION + 1) - formatComboIndex
        for i in selectedIndexes:
            songData = songsData[i]
            length = songData.header['length']
            maxLayer = songData.maxLayer

            if outputVersion > -1:
                songData.header['file_version'] = outputVersion

            for note in songData.notes:
                if self.flipHorizontallyCheckVar.get():
                    note['tick'] = length - note['tick']
                if self.flipVerticallyCheckVar.get():
                    note['layer'] = maxLayer - note['layer']

            songData.sortNotes()

            print(self.arrangeMode.get())
            if self.arrangeMode.get() == 'collapse':
                self.collapseNotes(songData.notes)
            elif self.arrangeMode.get() == 'instruments':
                compactNotes(songData, self.groupPerc)

            songData.sortNotes()

        builder.get_object('applyBtn')['state'] = 'normal'

        print('Applied!')

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

    def OnApplyTool(self):
        self.ToolsTabButton['state'] = 'disabled'
        data = self.inputFileData
        ticklen = data['header']['length']
        layerlen = data['maxLayer']
        instOpti = self.InstToolCombox.current()
        for note in data['notes']:
            # Flip
            if bool(self.var.tool.flip.horizontal.get()):
                note['tick'] = ticklen - note['tick']
            if bool(self.var.tool.flip.vertical.get()):
                note['layer'] = layerlen - note['layer']

            # Instrument change
            if instOpti > 0:
                note['inst'] = randrange(
                    len(self.var.tool.opts)-2) if instOpti > len(self.noteSounds) else instOpti-1
        # Reduce
        if bool(self.var.tool.reduce.opt2.get()) and bool(self.var.tool.reduce.opt3.get()):
            data['notes'] = [note for i, note in enumerate(
                data['notes']) if note == data['notes'][-1] or note['tick'] != data['notes'][i-1]['tick'] or note['tick'] != data['notes'][i+1]['tick']]
        elif bool(self.var.tool.reduce.opt2.get()):
            data['notes'] = [note for i, note in enumerate(
                data['notes']) if note['tick'] != data['notes'][i-1]['tick']]
        elif bool(self.var.tool.reduce.opt3.get()):
            data['notes'] = [data['notes'][i-1]
                             for i, note in enumerate(data['notes']) if note['tick'] != data['notes'][i-1]['tick']]
        if bool(self.var.tool.reduce.opt1.get()):
            data['notes'] = sorted(data['notes'], key=operator.itemgetter(
                'tick', 'inst', 'key', 'layer'))
            data['notes'] = [note for i, note in enumerate(data['notes']) if note['tick'] != data['notes'][i-1]
                             ['tick'] or note['inst'] != data['notes'][i-1]['inst'] or note['key'] != data['notes'][i-1]['key']]
            data['notes'] = sorted(
                data['notes'], key=operator.itemgetter('tick', 'layer'))

        # Compact
        if bool(self.var.tool.compact.get()):
            data = compactNotes(
                data, self.var.tool.compact.opt1.get(), self.var.tool.compact.opt1_1.get())
        # Sort notes


        data.correctData()
        self.ToolsTabButton['state'] = 'normal'

    def toggleExpOptiGrp(self, n=None, m=None, y=None):
        asFile = bool(self.var.export.mode.get())
        key = max(0, self.ExpConfigCombox.current())
        if asFile:
            if key == 0:
                self.ExpOptiSW.switch('Midi')
            elif key == 1:
                self.ExpOptiSW.switch('NCF')
            else:
                self.ExpOptiSW.switch('Other')
            self.ExpConfigCombox.configure(values=["{} ({})".format(
                tup[0], tup[1]) for tup in self.var.export.type.file])
        else:
            if key == 0:
                self.ExpOptiSW.switch('Wnbs')
            else:
                self.ExpOptiSW.switch('Other')
            self.ExpConfigCombox.configure(values=["{} ({})".format(tup[0], tup[1]) if isinstance(
                tup, tuple) else tup for tup in self.var.export.type.dtp])
        key = min(key, len(self.ExpConfigCombox['values'])-1)
        self.ExpConfigCombox.current(key)
        self.ExpConfigCombox.configure(width=len(self.ExpConfigCombox.get()))

        if self.exportFilePath.get():
            print(self.exportFilePath.get())
            fext = (self.var.export.type.file[self.ExpConfigCombox.current()],)[
                0][1][1:]
            if asFile:
                if not self.exportFilePath.get().lower().endswith(self.WnbsIDEntry.get()):
                    self.exportFilePath.set(
                        "{}/{}".format(self.exportFilePath.get(), self.WnbsIDEntry.get()))
                self.WnbsIDEntry.delete(0, 'end')
                if not self.exportFilePath.get().lower().endswith(fext):
                    self.exportFilePath.set(
                        self.exportFilePath.get().split('.')[0] + fext)
            else:
                if '.' in self.exportFilePath.get():
                    self.WnbsIDEntry.delete(0, 'end')
                    self.WnbsIDEntry.insert(
                        0, self.exportFilePath.get().split('/')[-1].split('.')[0])
                    self.exportFilePath.set(
                        '/'.join(self.exportFilePath.get().split('/')[0:-1]))

    def OnBrowseExp(self):
        if self.filePath and self.inputFileData:
            asFile = bool(self.var.export.mode.get())
            if asFile:
                curr = (
                    self.var.export.type.file[self.ExpConfigCombox.current()],)
                fext = curr[0][1][1:]
                self.exportFilePath.set(asksaveasfilename(title="Export file", initialfile=os.path.splitext(
                    os.path.basename(self.filePath))[0]+fext, filetypes=curr))
            else:
                curr = [
                    (self.var.export.type.dtp[self.ExpConfigCombox.current()], '*.'), ]
                fext = ''
                self.exportFilePath.set(askdirectory(
                    title="Export datapack (choose the directory to put the datapack)", initialdir=os.path.dirname(self.filePath), mustexist=False))
            if self.exportFilePath.get():
                if asFile:
                    if not self.exportFilePath.get().lower().endswith(fext):
                        self.exportFilePath.set(
                            self.exportFilePath.get().split('.')[0] + fext)
                else:
                    if '.' in self.exportFilePath.get().split('/')[-1]:
                        self.exportFilePath.set(
                            '/'.join(self.exportFilePath.get().split('/')[0:-1]))

    def OnExport(self):
        if self.exportFilePath.get() is not None:
            data, path = self.inputFileData, self.exportFilePath.get()
            asFile = bool(self.var.export.mode.get())
            type = self.ExpConfigCombox.current()
            if asFile:
                if type == 0:
                    exportMIDI(self, path, self.var.export.midi.opt1.get())
                elif type == 1:
                    with open(path, "w") as f:
                        f.write(writencf(data))
                elif type in {2, 3, 4, 5}:
                    fext = self.var.export.type.file[self.ExpConfigCombox.current(
                    )][1][2:]
                    # exportMusic(self, path, fext)
            else:
                if type == 0:
                    exportDatapack(self, os.path.join(
                        path, self.WnbsIDEntry.get()), 'wnbs')

            self.ExpBrowseButton['state'] = self.ExpSaveButton['state'] = 'normal'


class DatapackExportDialog:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(resource_path())
        builder.add_from_file(resource_path('datapackexportdialog.ui'))

        self.dialog = builder.get_object('dialog', master)
        centerToplevel(self.dialog.toplevel)

        button = builder.get_object('exportBtn')
        button.configure(command=self.export)
        if len(parent.fileTable.selection()) == 0:
            button["state"] = "disabled"

        def wnbsIDVaildate(P):
            isVaild = bool(re.match("^(\d|\w|[-_])*$", P))
            button["state"] = "normal" if isVaild and (
                14 >= len(P) > 0) else "disabled"
            return isVaild

        self.entry = entry = builder.get_object('IDEntry')
        vcmd = (master.register(wnbsIDVaildate), '%P')
        entry.configure(validatecommand=vcmd)

        builder.connect_callbacks(self)

    def run(self):
        self.builder.get_object('dialog').run()

    def export(self, _=None):
        self.dialog.close()
        fileTable = self.parent.fileTable
        index = fileTable.index(fileTable.selection()[0])

        path = askdirectory(title="Select folder to save")
        if path == '':
            return
        exportDatapack(self.parent.songsData[index], os.path.join(
            path, self.entry.get()), self.entry.get(), 'wnbs')


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


class StackingWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._frames = {}
        self._i = 0
        #self._shown = None

    def __getitem__(self, key):
        if key in self._frames:
            return self._frames[key][0]
        super().__getitem__(key)

    def append(self, frame, key=None):
        if isinstance(frame, (tk.Widget, ttk.Widget)):
            if not key:
                key = self._i
                self._i += 1
            self._frames[key] = [frame, None]

    def switch(self, key):
        for k, (w, o) in self._frames.items():
            if k == key:
                if o:
                    w.pack(**o)
                else:
                    w.pack()
            else:
                w.pack_forget()

    def pack(self, key=None, **opts):
        if key:
            self._frames[key][1] = opts
        else:
            super().pack(**opts)
        if len(self._frames) == 1:
            self.switch(key)


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

def exportMIDI(cls, path, byLayer=False):
    pass


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
            # print(p)
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
                  "description": "Note block song made with NBSTool.", "pack_format": 1}})
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
    print('Creating app...')

    print(sys.argv)

    if len(sys.argv) == 2:
        app.addFiles(paths=[sys.argv[1], ])

    print('Ready')
    app.mainwin.mainloop()

    print("The app was closed.")
