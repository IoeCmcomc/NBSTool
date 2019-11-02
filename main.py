# This file is a part of:
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█       
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███       
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███       
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███       
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███       
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███       
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄ 
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██ 
#__________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Version: 0.7.0
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


import sys, os, operator, webbrowser, copy, traceback, re, json, music21

import tkinter as tk
import tkinter.ttk as ttk

#import tkinter.messagebox as tkmsgbox
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.scrolledtext import ScrolledText

from time import sleep, time
from pprint import pprint
from random import randrange
from math import floor, log2
from datetime import date

from PIL import Image, ImageTk
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import music21 as m21
import music21.stream as m21s
import music21.instrument as m21i

from attr import Attr
from nbsio import opennbs, writenbs, DataPostprocess
from ncfio import writencf
'''
import logging

l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())'''

#sys.stdout = open('main_log.txt', 'w')

#Credit: https://stackoverflow.com/questions/42474560/pyinstaller-single-exe-file-ico-image-in-title-of-tkinter-main-window
def resource_path(*args):
	if len(args) > 1:
		relative_path = os.path.join(*args)
	else: relative_path = args[0]
	try:
		r = os.path.join(sys._MEIPASS, relative_path)
	except Exception:
		r = os.path.join(os.path.abspath("."), relative_path)
	#print(r)
	return r

class MainWindow(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.properties()
		self.elements()
		self.WindowBind()
		#self.update()
		self.pack(fill='both', expand=True)
		self.update()
		WindowGeo(self.parent, self.parent, 800, 500, 600, 500)

	def properties(self):
		self.filePath = None
		self.inputFileData = None
		self.noteSounds = None
		self.last = Attr()
		self.last.inputFileData = None
		self.var = Attr()
		self.PlayingState = 'stop'
		self.PlayingTick = -1
		self.SongPlayerAfter = None
		self.exportFilePath = tk.StringVar()

	def elements(self):
		self.parent.title("NBS Tool")
		self.style = ttk.Style()
		#self.style.theme_use("default")
		self.style.theme_use("vista")
		
		#Menu bar
		self.menuBar = tk.Menu(self)
		self.parent.configure(menu=self.menuBar)
		self.menus()
		
		#Tabs
		self.NbTabs = ttk.Notebook(self)
		self.tabs()
		self.NbTabs.enable_traversal()
		self.NbTabs.pack(fill='both', expand=True)
		
		#Footer
		tk.Frame(self, height=5).pack()

		self.footer = tk.Frame(self, relief='groove', borderwidth=1, height=25, width=self.winfo_width())
		self.footer.pack_propagate(False)
		self.footerElements()
		self.footer.pack(side='top', fill='x')
	
	def menus(self):
		# 'File' menu
		self.fileMenu = tk.Menu(self.menuBar, tearoff=False)
		self.menuBar.add_cascade(label="File", menu=self.fileMenu)
		
		self.fileMenu.add_command(label="Open", accelerator="Ctrl+O", command = lambda: self.OnBrowseFile(True))
		self.fileMenu.add_command(label="Save", accelerator="Ctrl+S", command=self.OnSaveFile)
		self.fileMenu.add_command(label="Save as new file", accelerator="Ctrl+Shift+S", command = lambda: self.OnSaveFile(True))
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label="Quit", accelerator="Esc", command=self.onClose)

		self.helpMenu = tk.Menu(self.menuBar, tearoff=False)
		self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

		self.helpMenu.add_command(label="About", command=lambda: AboutWindow(self))

	def tabs(self):
		#"General" tab
		self.GeneralTab = tk.Frame(self.NbTabs)
		
		self.GeneralTab.rowconfigure(0)
		self.GeneralTab.rowconfigure(1, weight=1)
		
		self.GeneralTab.columnconfigure(0, weight=1, uniform='a')
		self.GeneralTab.columnconfigure(1, weight=1, uniform='a')
		
		self.GeneralTabElements()
		self.NbTabs.add(self.GeneralTab, text="General")
		
		#"Play" tab
		self.PlayTab = tk.Frame(self.NbTabs)

		self.PlayTabElements()
		self.NbTabs.add(self.PlayTab, text="Play")

		#"Tools" tab
		self.ToolsTab = tk.Frame(self.NbTabs)

		self.ToolsTab.rowconfigure(0, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(1, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(2)
		
		self.ToolsTab.columnconfigure(0, weight=1, uniform='b')
		self.ToolsTab.columnconfigure(1, weight=1, uniform='b')

		self.ToolsTabElements()
		self.NbTabs.add(self.ToolsTab, text="Tools")

		#"Export" tab
		self.ExportTab = tk.Frame(self.NbTabs)

		self.ExportTabElements()
		self.NbTabs.add(self.ExportTab, text="Export")
		
	def GeneralTabElements(self):
		fpadx, fpady = 10, 10
		padx, pady = 5, 5

		#"Open file" frame
		self.OpenFileFrame = tk.Frame(self.GeneralTab, relief='ridge', borderwidth=1)
		self.OpenFileFrame.grid(row=0, columnspan=2, sticky='nsew')
		
		self.OpenFileLabel = tk.Label(self.OpenFileFrame, text="Open file:", anchor='w', width=8)
		self.OpenFileLabel.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileEntry = tk.Entry(self.OpenFileFrame)
		self.OpenFileEntry.pack(side='left', fill='x', padx=padx, expand=True)
		
		self.BrowseFileButton = ttk.Button(self.OpenFileFrame, text="Browse", command = lambda: self.OnBrowseFile() )
		self.BrowseFileButton.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileButton = ttk.Button(self.OpenFileFrame, text="Open", command = lambda: self.OnOpenFile('', True) )
		self.OpenFileButton.pack(side='left', padx=padx, pady=pady)
		
		#File metadata frame
		self.FileMetaFrame = tk.LabelFrame(self.GeneralTab, text="Metadata")
		self.FileMetaFrame.grid(row=1, column=0, padx=fpadx, pady=fpady, sticky='nsew')
		
		self.FileMetaMess = tk.Message(self.FileMetaFrame, text="No flie was found.")
		self.FileMetaMess.pack(fill='both', expand=True, padx=padx, pady=padx)
		
		#More infomation frame
		self.FileInfoFrame = tk.LabelFrame(self.GeneralTab, text="Infomations")
		self.FileInfoFrame.grid(row=1, column=1, padx=fpadx, pady=fpady, sticky='nsew')
		
		self.FileInfoMess = tk.Message(self.FileInfoFrame, text="No flie was found.")
		self.FileInfoMess.pack(fill='both', expand=True, padx=padx, pady=pady)
	
	def PlayTabElements(self):
		fpadx, fpady = 10, 10
		padx, pady = 5, 5

		self.PlayCanvasFrame = tk.Frame(self.PlayTab, relief='groove', borderwidth=1)
		self.PlayCanvasFrame.pack(fill='both', expand=True, padx=fpadx, pady=fpady)

		tk.Message(self.PlayCanvasFrame, text='Experimental feature', font=("Arial", 44)).pack(fill='both', expand=True)

		self.PlayCtrlFrame = tk.Frame(self.PlayTab, relief='groove', borderwidth=1)
		self.PlayCtrlFrame.pack(fill='both', padx=fpadx, pady=fpady)

		self.PlayCtrlScale = tk.Scale(self.PlayCtrlFrame, from_=0, to=self.inputFileData['headers']['length'] if self.inputFileData is not None else 0, orient='horizontal', sliderlength=25)
		self.PlayCtrlScale.pack(side='top', fill='x', expand=True)
		self.PlayCtrlScale.bind("<ButtonPress-1>", lambda _: self.CtrlSongPlayer(state='pause'))
		#self.PlayCtrlScale.bind("<ButtonRelease-1>", lambda e: setattr(self, 'PlayingTick', e.widget.get()))
		self.PlayCtrlScale.bind("<ButtonRelease-1>", lambda _: self.CtrlSongPlayer(state='play'))

		self.CtrlBtnSW = StackingWidget(self.PlayCtrlFrame, relief='groove', borderwidth=1)
		self.CtrlBtnSW.pack(side='left', anchor='sw', padx=padx, pady=pady)

		#self.PlaySongBtn = SquareButton(self.PlayCtrlFrame, text ='▶', size=20, command=lambda: self.CtrlSongPlayer(state='play'))
		self.CtrlBtnSW.append(tk.Button(self.CtrlBtnSW, text ='Play', command=lambda: self.CtrlSongPlayer(state='play')), 'play')
		self.CtrlBtnSW.pack('play')

		self.CtrlBtnSW.append(tk.Button(self.CtrlBtnSW, text ='Pause', command=lambda: self.CtrlSongPlayer(state='pause')), 'pause')
		self.CtrlBtnSW.pack('pause')

		#self.StopSongBtn = SquareButton(self.PlayCtrlFrame, text ='⏹', size=20, command=lambda: self.CtrlSongPlayer(state='stop'))
		self.StopSongBtn = tk.Button(self.PlayCtrlFrame, text ='Stop', command=lambda: self.CtrlSongPlayer(state='stop'))
		self.StopSongBtn.pack(side='left', anchor='sw', padx=padx, pady=pady)

	def ToolsTabElements(self):
		fpadx, fpady = 10, 10
		padx, pady = 5, 0

		#Flip tool
		self.FlipToolFrame = tk.LabelFrame(self.ToolsTab, text="Flipping")
		self.FlipToolFrame.grid(row=0, column=0, sticky='nsew', padx=fpadx, pady=fpady)
		
		self.FlipToolMess = tk.Message(self.FlipToolFrame, anchor='w', text="Flip the note sequence horizontally (by tick), vertically (by layer) or both: ")
		self.FlipToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)
		
		self.var.tool.flip.vertical = tk.IntVar()
		self.FilpToolCheckV = tk.Checkbutton(self.FlipToolFrame, text="Vertically", variable=self.var.tool.flip.vertical)
		self.FilpToolCheckV.pack(side='left', padx=padx, pady=pady)
		
		self.var.tool.flip.horizontal = tk.IntVar()
		self.FilpToolCheckH = tk.Checkbutton(self.FlipToolFrame, text="Horizontally", variable=self.var.tool.flip.horizontal)
		self.FilpToolCheckH.pack(side='left', padx=padx, pady=pady)

		#Instrument tool
		self.InstToolFrame = tk.LabelFrame(self.ToolsTab, text="Note's instrument")
		self.InstToolFrame.grid(row=0, column=1, sticky='nsew', padx=fpadx, pady=fpady)
		
		self.InstToolMess = tk.Message(self.InstToolFrame, anchor='w', text="Change all note's instrument to:")
		self.InstToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)
		
		self.var.tool.opts = opts = ["(not applied)"] + [x['name'] for x in vaniNoteSounds] + ["Random"]
		self.InstToolCombox = ttk.Combobox(self.InstToolFrame, state='readonly', values=opts)
		self.InstToolCombox.current(0)
		self.InstToolCombox.pack(side='left', fill='both' ,expand=True, padx=padx, pady=pady)

		#Reduce tool
		self.ReduceToolFrame = tk.LabelFrame(self.ToolsTab, text="Reducing")
		self.ReduceToolFrame.grid(row=1, column=0, sticky='nsew', padx=fpadx, pady=fpady)

		self.ReduceToolMess = tk.Message(self.ReduceToolFrame, anchor='w', text="Delete as many note as possible to reduce file size.")
		self.ReduceToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)

		self.var.tool.reduce.opt1 = tk.IntVar()
		self.CompactToolChkOpt1 = FlexCheckbutton(self.ReduceToolFrame, text="Delete duplicate notes", variable=self.var.tool.reduce.opt1, anchor='w')
		self.CompactToolChkOpt1.pack(padx=padx, pady=pady)

		self.var.tool.reduce.opt2 = tk.IntVar()
		self.CompactToolChkOpt2 = FlexCheckbutton(self.ReduceToolFrame, text=" In every tick, delete all notes except the first note", variable=self.var.tool.reduce.opt2, anchor='w')
		self.CompactToolChkOpt2.pack(padx=padx, pady=pady)

		self.var.tool.reduce.opt3 = tk.IntVar()
		self.CompactToolChkOpt3 = FlexCheckbutton(self.ReduceToolFrame, text=" In every tick, delete all notes except the last note", variable=self.var.tool.reduce.opt3, anchor='w')
		self.CompactToolChkOpt3.pack(padx=padx, pady=(pady, 10))

		#Compact tool
		self.CompactToolFrame = tk.LabelFrame(self.ToolsTab, text="Compacting")
		self.CompactToolFrame.grid(row=1, column=1, sticky='nsew', padx=fpadx, pady=fpady)

		self.CompactToolMess = tk.Message(self.CompactToolFrame, anchor='w', text="Remove spaces between notes vertically (by layer) and group them by instruments.")
		self.CompactToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)

		self.var.tool.compact = tk.IntVar()
		self.CompactToolCheck = FlexCheckbutton(self.CompactToolFrame, text="Compact notes", variable=self.var.tool.compact, command=self.toggleCompactToolOpt, anchor='w')
		self.CompactToolCheck.pack(padx=padx, pady=pady)

		self.var.tool.compact.opt1 = tk.IntVar()
		self.CompactToolChkOpt1 = FlexCheckbutton(self.CompactToolFrame, text="Automatic separate notes by instruments (remain some spaces)", variable=self.var.tool.compact.opt1, state='disabled', command=lambda: self.toggleCompactToolOpt(2), anchor='w')
		self.CompactToolChkOpt1.select()
		self.CompactToolChkOpt1.pack(padx=padx*5, pady=pady)

		self.var.tool.compact.opt1_1 = tk.IntVar()
		self.CompactToolChkOpt1_1 = FlexCheckbutton(self.CompactToolFrame, text="Group percussions into one layer", variable=self.var.tool.compact.opt1_1, state='disabled', anchor='w')
		self.CompactToolChkOpt1_1.select()
		self.CompactToolChkOpt1_1.pack(padx=padx*5*2, pady=pady)
		
		#'Apply' botton
		self.ToolsTabButton = ttk.Button(self.ToolsTab, text="Apply", state='disabled', command = self.OnApplyTool )
		self.ToolsTabButton.grid(row=2, column=1, sticky='se', padx=fpadx, pady=fpady)
	
	def ExportTabElements(self):
		fpadx, fpady = 10, 10
		padx, pady = 5, 5
		
		#Upper frame
		self.ExpConfigFrame = tk.LabelFrame(self.ExportTab, text="Option")
		self.ExpConfigFrame.pack(fill='both', expand=True, padx=fpadx, pady=fpady)
		
		#"Select mode" frame
		self.ExpConfigGrp1 = tk.Frame(self.ExpConfigFrame, relief='groove', borderwidth=1)
		self.ExpConfigGrp1.pack(fill='both', padx=fpadx)

		self.ExpConfigLabel = tk.Label(self.ExpConfigGrp1, text="Export the song as a:", anchor='w')
		self.ExpConfigLabel.pack(side='left', fill='x', padx=padx, pady=pady)

		self.var.export.mode = tk.IntVar()
		self.ExpConfigMode1 = tk.Radiobutton(self.ExpConfigGrp1, text="File", variable=self.var.export.mode, value=1)
		self.ExpConfigMode1.pack(side='left', padx=padx, pady=pady)
		self.ExpConfigMode1.select()
		self.ExpConfigMode2 = tk.Radiobutton(self.ExpConfigGrp1, text="Datapack", variable=self.var.export.mode, value=0)
		self.ExpConfigMode2.pack(side='left', padx=padx, pady=pady)

		self.var.export.type.file = \
		[('Musical Instrument Digital Interface files', '*.mid'),
		('Nokia Composer Format', '*.txt'),
		('MPEG-1 Layer 3', '*.mp3'),
		('Waveform Audio File Format', '*.wav'),
		('Ogg Vorbis files', '*.ogg'),
		('Free Lossless Audio Codec files', '*.flac')]
		self.var.export.type.dtp = ['Wireless note block song', 'other']
		self.ExpConfigCombox = ttk.Combobox(self.ExpConfigGrp1, state='readonly', values=["{} ({})".format(tup[0], tup[1]) for tup in self.var.export.type.file])
		self.ExpConfigCombox.current(0)
		self.ExpConfigCombox.bind("<<ComboboxSelected>>", self.toggleExpOptiGrp)
		self.ExpConfigCombox.pack(side='left', fill='x', padx=padx, pady=pady)

		self.var.export.mode.trace('w', self.toggleExpOptiGrp)

		ttk.Separator(self.ExpConfigFrame, orient="horizontal").pack(fill='x', expand=False, padx=padx*3, pady=pady)
		
		self.ExpOptiSW = StackingWidget(self.ExpConfigFrame, relief='groove', borderwidth=1)
		self.ExpOptiSW.pack(fill='both', expand=True, padx=fpadx)

		#Midi export options frame
		self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Midi')
		self.ExpOptiSW.pack('Midi', side='top', fill='both', expand=True)

		self.var.export.midi.opt1 = tk.IntVar()
		self.ExpMidi1Rad1 = tk.Radiobutton(self.ExpOptiSW['Midi'], text="Sort notes to MIDI tracks by note's layer", variable=self.var.export.midi.opt1, value=1)
		self.ExpMidi1Rad1.pack(anchor='nw', padx=padx, pady=(pady, 0))
		self.ExpMidi1Rad2 = tk.Radiobutton(self.ExpOptiSW['Midi'], text="Sort notes to MIDI tracks by note's instrument", variable=self.var.export.midi.opt1, value=0)
		self.ExpMidi1Rad2.pack(anchor='nw', padx=padx, pady=(0, pady))
		
		#Nokia export options frame
		self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'NCF')
		self.ExpOptiSW.pack('NCF', side='top', fill='both', expand=True)

		self.NCFOutput = ScrolledText(self.ExpOptiSW['NCF'], state="disabled", height=10)
		self.NCFOutput.pack(fill='both', expand=True)

		#'Wireless song datapack' export options frame
		self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Wnbs')
		self.ExpOptiSW.pack('Wnbs', side='top', fill='both', expand=True)

		self.WnbsIDLabel = tk.Label(self.ExpOptiSW['Wnbs'], text="Unique name:")
		self.WnbsIDLabel.pack(anchor='nw', padx=padx, pady=pady)

		#vcmd = (self.register(self.onValidate), '%P')
		self.WnbsIDEntry = tk.Entry(self.ExpOptiSW['Wnbs'], validate="key",
		validatecommand=(self.register(lambda P: bool(re.match("^(\d|\w|[-_])*$", P))), '%P'))
		self.WnbsIDEntry.pack(anchor='nw', padx=padx, pady=pady)

		#Other export options frame
		self.ExpOptiSW.append(tk.Frame(self.ExpOptiSW), 'Other')
		self.ExpOptiSW.pack('Other', side='top', fill='both', expand=True)
		
		self.ExpMusicLabel = tk.Label(self.ExpOptiSW['Other'], text="There is no option available.")
		self.ExpMusicLabel.pack(anchor='nw', padx=padx, pady=pady)
		
		#Output frame
		self.ExpOutputFrame = tk.LabelFrame(self.ExportTab, text="Output")
		self.ExpOutputFrame.pack(fill='both', padx=fpadx, pady=(0, fpady))

		self.ExpOutputLabel = tk.Label(self.ExpOutputFrame, text="File path:", anchor='w', width=8)
		self.ExpOutputLabel.pack(side='left', fill='x', padx=padx, pady=pady)
		
		self.ExpOutputEntry = tk.Entry(self.ExpOutputFrame, textvariable=self.exportFilePath)
		self.ExpOutputEntry.pack(side='left', fill='x', padx=padx, expand=True)
		
		self.ExpBrowseButton = ttk.Button(self.ExpOutputFrame, text="Browse", command = self.OnBrowseExp )
		self.ExpBrowseButton.pack(side='left', padx=padx, pady=pady)

		self.ExpSaveButton = ttk.Button(self.ExpOutputFrame, text="Export", command = self.OnExport )
		self.ExpSaveButton.pack(side='left', padx=padx, pady=pady)

	def footerElements(self):
		self.footerLabel = tk.Label(self.footer, text="Ready")
		self.footerLabel.pack(side='left', fill='x')
		self.var.footerLabel = 0
		
		self.sizegrip = ttk.Sizegrip(self.footer)
		self.sizegrip.pack(side='right', anchor='se')

		self.progressbar = ttk.Progressbar(self.footer, orient="horizontal", length=300 ,mode="determinate")
		self.progressbar["value"] = 0
		self.progressbar["maximum"] = 100
		#self.progressbar.start()
		#self.progressbar.stop()
	
	def WindowBind(self):
		#Keys
		self.parent.bind('<Escape>', self.onClose)
		self.parent.bind('<Control-o>', lambda _: self.OnBrowseFile(True))
		self.parent.bind('<Control-s>', self.OnSaveFile)
		self.parent.bind('<Control-Shift-s>', lambda _: self.OnSaveFile(True))
		self.parent.bind('<Control-Shift-S>', lambda _: self.OnSaveFile(True))

		#Bind class
		self.bind_class("Message" ,"<Configure>", lambda e: e.widget.configure(width=e.width-10))
		
		for tkclass in ('TButton', 'Checkbutton', 'Radiobutton'):
			self.bind_class(tkclass, '<Return>', lambda e: e.widget.event_generate('<space>', when='tail'))

		self.bind_class("TCombobox", "<Return>", lambda e: e.widget.event_generate('<Down>'))

		for tkclass in ("Entry", "Text", "ScrolledText"):
			self.bind_class(tkclass ,"<Button-3>", self.popupmenus)
		
		self.bind_class("TNotebook", "<<NotebookTabChanged>>", self._on_tab_changed)
	
	
	#Credit: http://code.activestate.com/recipes/580726-tkinter-notebook-that-fits-to-the-height-of-every-/
	def _on_tab_changed(self,event):
		event.widget.update_idletasks()

		tab = event.widget.nametowidget(event.widget.select())
		event.widget.configure(height=tab.winfo_reqheight())
	
	def popupmenus(self, event):
		w = event.widget
		self.popupMenu = tk.Menu(self, tearoff=False)
		self.popupMenu.add_command(label="Select all", accelerator="Ctrl+A", command=lambda: w.event_generate("<Control-a>"))
		self.popupMenu.add_separator()
		self.popupMenu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: w.event_generate("<Control-x>"))
		self.popupMenu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: w.event_generate("<Control-c>"))
		self.popupMenu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: w.event_generate("<Control-v>"))
		self.popupMenu.tk.call("tk_popup", self.popupMenu, event.x_root, event.y_root)

	def onClose(self, event=None):
		self.parent.quit()
		self.parent.destroy()

	def OnBrowseFile(self, doOpen=False):
		types = [('Note Block Studio files', '*.nbs'), ('All files', '*')]
		filename = askopenfilename(filetypes = types)
		if self.filePath is None or bool(filename):
			self.filePath = filename
			self.OpenFileEntry.delete(0,'end')
			self.OpenFileEntry.insert(0, filename)
			if doOpen:
				self.OnOpenFile(filename, None)

	def OnOpenFile(self, fileName, fromEntry=False):
		if fromEntry: fileName = self.OpenFileEntry.get()
		self.UpdateProgBar(20)
		if fileName != '':
			data = opennbs(fileName)
			if data is not None:
				self.UpdateProgBar(80)
				self.inputFileData = data
				self.ExpOutputEntry.delete(0, 'end')
				self.exportFilePath.set('')
		
			self.UpdateVar()
			self.RaiseFooter('Opened')
			self.UpdateProgBar(100)
		self.UpdateProgBar(-1)
	
	def OnSaveFile(self, saveAsNewFile=False):
		if self.inputFileData is not None:
			if saveAsNewFile is True:
				types = [('Note Block Studio files', '*.nbs'), ('All files', '*')]
				self.filePath = asksaveasfilename(filetypes = types)
			self.UpdateProgBar(50)

			writenbs(self.filePath, self.inputFileData)

			if saveAsNewFile is True:
				self.OpenFileEntry.delete(0,'end')
				self.OpenFileEntry.insert(0, self.filePath)

			self.UpdateProgBar(100)
			self.RaiseFooter('Saved')
			self.UpdateProgBar(-1)
	
	def toggleCompactToolOpt(self, id=1):
		if id <= 2:
			a = ((self.var.tool.compact.opt1.get() == 0) or (self.var.tool.compact.get() == 0))
			self.CompactToolChkOpt1_1["state"] = "disable" if a is True else "normal"
			if id <= 1:
				self.CompactToolChkOpt1["state"] = "disable" if self.var.tool.compact.get() == 0 else "normal"

	def CtrlSongPlayer(self, event=None, state=None, repeat=False):
		if self.inputFileData is None: return
		hds = self.inputFileData['headers']
		notes = self.inputFileData['notes']
		layers = self.inputFileData['layers']
		tickIndexes = self.inputFileData['indexByTick']
		noteSounds = self.noteSounds

		if state == 'play' and self.PlayingState != 'play' or repeat and self.SongPlayerAfter is not None:
			if self.PlayingTick < hds['length'] - 1:
				self.PlayingState = 'play'
				self.CtrlBtnSW.switch('pause')
				self.PlayingTick = int(self.PlayCtrlScale.get())
				self.PlayCtrlScale.set(self.PlayingTick + 1)

				toUnsigned = lambda x: 256 + x if x < 0 else x
				tickSoundLength = max(len(x['obj']) for x in noteSounds)
				currNotes = tickIndexes[self.PlayingTick][1]
				SoundToPlay = None

				for n, i in enumerate(currNotes ):
					note = notes[i]
					currLayer = layers[note['layer']]
					inst = note['inst']
					
					currNoteSound = noteSounds[inst]
					noteSoundObj = currNoteSound['obj']
					
					ANoteSound = noteSoundObj._spawn(noteSoundObj.raw_data, overrides={'frame_rate': int(noteSoundObj.frame_rate * (2.0 ** ((note['key'] - currNoteSound['pitch']) / 12))) }).set_frame_rate(44100)
					if currLayer['volume'] != 100: ANoteSound = ANoteSound.apply_gain(noteSoundObj.dBFS - noteSoundObj.dBFS * (currLayer['volume'] / 100)) + 3
					if currLayer['stereo'] != 100: ANoteSound = ANoteSound.pan((toUnsigned(currLayer['stereo']) - 100) / 100)
					
					if len(currNotes) == 1: SoundToPlay = ANoteSound
					elif n == 0: SoundToPlay = ANoteSound + AudioSegment.silent(duration=tickSoundLength - len(ANoteSound))
					else: SoundToPlay = SoundToPlay.overlay(ANoteSound)
				
				if len(currNotes) > 0: _play_with_simpleaudio(SoundToPlay.set_frame_rate(44100))

				#self.SongPlayerAfter = self.after(40, lambda: self.CtrlSongPlayer(state='play', repeat=True) )
				self.SongPlayerAfter = self.after(int(1000 / hds['tempo'] * 0.9), lambda: self.CtrlSongPlayer(state='play', repeat=True) )
			else:
				state = 'stop'
		
		if state == 'pause' and self.PlayingState != 'pause':
			if self.PlayingState == 'stop': return
			self.PlayingState = 'pause'
			self.CtrlBtnSW.switch('play')
			self.after_cancel(self.SongPlayerAfter)
			self.SongPlayerAfter = None
		
		if state == 'stop' and self.PlayingState != 'stop' and self.SongPlayerAfter:
			self.PlayingState = 'stop'
			self.PlayingTick = -1
			self.CtrlBtnSW.switch('play')
			self.after_cancel(self.SongPlayerAfter)
			self.SongPlayerAfter = None
			self.PlayCtrlScale.set(0)
		

	def OnApplyTool(self):
		self.ToolsTabButton['state'] = 'disabled'
		self.UpdateProgBar(0)
		data = self.inputFileData
		ticklen = data['headers']['length']
		layerlen = data['maxLayer']
		instOpti = self.InstToolCombox.current()
		self.UpdateProgBar(20)
		for note in data['notes']:
			#Flip
			if bool(self.var.tool.flip.horizontal.get()): note['tick'] = ticklen - note['tick']
			if bool(self.var.tool.flip.vertical.get()): note['layer'] = layerlen - note['layer']

			#Instrument change
			if instOpti > 0:
				note['inst'] = randrange(len(self.var.tool.opts)-2) if instOpti > len(self.noteSounds) else instOpti-1
		self.UpdateProgBar(30)
		#Reduce
		if bool(self.var.tool.reduce.opt2.get()) and bool(self.var.tool.reduce.opt3.get()):
			data['notes'] = [note for i, note in enumerate(data['notes']) if note == data['notes'][-1] or note['tick'] != data['notes'][i-1]['tick'] or note['tick'] != data['notes'][i+1]['tick']]
		elif bool(self.var.tool.reduce.opt2.get()):
			data['notes'] = [note for i, note in enumerate(data['notes']) if note['tick'] != data['notes'][i-1]['tick']]
		elif bool(self.var.tool.reduce.opt3.get()):
			data['notes'] = [data['notes'][i-1] for i, note in enumerate(data['notes']) if note['tick'] != data['notes'][i-1]['tick']]
			self.UpdateProgBar(60)
		if bool(self.var.tool.reduce.opt1.get()):
			data['notes'] = sorted(data['notes'], key = operator.itemgetter('tick', 'inst', 'key', 'layer') )
			data['notes'] = [note for i, note in enumerate(data['notes']) if note['tick'] != data['notes'][i-1]['tick'] or note['inst'] != data['notes'][i-1]['inst'] or note['key'] != data['notes'][i-1]['key']]
			data['notes'] = sorted(data['notes'], key = operator.itemgetter('tick', 'layer') )

		self.UpdateProgBar(50)
		#Compact
		if bool(self.var.tool.compact.get()): data = compactNotes(data, self.var.tool.compact.opt1.get(), self.var.tool.compact.opt1_1.get())
		self.UpdateProgBar(60)
		#Sort notes
		data['notes'] = sorted(data['notes'], key = operator.itemgetter('tick', 'layer') )
		
		self.UpdateProgBar(60)
		data = DataPostprocess(data)
				
		self.UpdateProgBar(90)
		self.UpdateVar()
		#self.UpdateProgBar(100)
		self.RaiseFooter('Applied')
		self.UpdateProgBar(-1)
		self.ToolsTabButton['state'] = 'normal'
	
	def toggleExpOptiGrp(self ,n=None, m=None, y=None):
		print(n, m, y)
		asFile = bool(self.var.export.mode.get())
		key = max(0, self.ExpConfigCombox.current())
		print(asFile, key)
		if asFile:
			if key == 0: self.ExpOptiSW.switch('Midi')
			elif key == 1: self.ExpOptiSW.switch('NCF')
			else: self.ExpOptiSW.switch('Other')
			self.ExpConfigCombox.configure(values=["{} ({})".format(tup[0], tup[1]) for tup in self.var.export.type.file])
		else:
			if key == 0: self.ExpOptiSW.switch('Wnbs')
			else: self.ExpOptiSW.switch('Other')
			self.ExpConfigCombox.configure(values=["{} ({})".format(tup[0], tup[1]) if isinstance(tup, tuple) else tup for tup in self.var.export.type.dtp])
		key = min(key, len(self.ExpConfigCombox['values'])-1)
		self.ExpConfigCombox.current(key)
		self.ExpConfigCombox.configure(width=len(self.ExpConfigCombox.get()) + 2)
		
		if self.exportFilePath.get():
			print(self.exportFilePath.get())
			fext = (self.var.export.type.file[self.ExpConfigCombox.current()],)[0][1][1:]
			print(fext)
			print(self.WnbsIDEntry.get())
			if asFile:
				if not self.exportFilePath.get().lower().endswith(self.WnbsIDEntry.get()): self.exportFilePath.set( "{}/{}".format(self.exportFilePath.get(), self.WnbsIDEntry.get()) )
				self.WnbsIDEntry.delete(0, 'end')
				if not self.exportFilePath.get().lower().endswith(fext): self.exportFilePath.set( self.exportFilePath.get().split('.')[0] + fext )
			else:
				if '.' in self.exportFilePath.get():
					self.WnbsIDEntry.delete(0, 'end')
					self.WnbsIDEntry.insert(0, self.exportFilePath.get().split('/')[-1].split('.')[0])
					self.exportFilePath.set( '/'.join(self.exportFilePath.get().split('/')[0:-1]) )

	def UpdateVar(self):
		#print("Started updating….")
		data = self.inputFileData
		self.UpdateProgBar(20)
		if data is not None:
			self.ToolsTabButton['state'] = 'normal'
			if data != self.last.inputFileData:
				self.UpdateProgBar(20)
				headers = data['headers']
				self.UpdateProgBar(30)
				text = "File version: {}\nFirst custom inst index: {}\nSong length: {}\nSong height: {}\nSong name: {}\nSong author: {}\nComposer: {}\nSong description: {}\nTempo: {} TPS\nAuto-saving: {}\nTime signature: {}/4\nMinutes spent: {}\nLeft clicks: {}\nRight clicks: {}\nBlocks added: {}\nBlocks removed: {}\nMIDI/Schematic file name: {}".format \
				( headers['file_version'], headers['vani_inst'], headers['length'], headers['height'], headers['name'], headers['orig_author'], headers['author'], headers['description'], headers['tempo'], "Enabled (save every {} minutes(s)".format(headers['auto-saving_time']) if headers['auto-saving'] else "Disabled", headers['time_sign'], headers['minutes_spent'], headers['left_clicks'], headers['right_clicks'], headers['block_added'], headers['block_removed'], headers['import_name'] )
				self.FileMetaMess.configure(text=text)
				self.UpdateProgBar(40)
				text = "File format: {}\nHas percussion: {}\nMax layer with at least 1 note block: {}\nCustom instrument(s): {}".format \
				( "Old" if data['IsOldVersion'] else "New", data['hasPerc'], data['maxLayer'], headers['inst_count'] )
				self.FileInfoMess.configure(text=text)
				self.UpdateProgBar(50)
				self.PlayCtrlScale['to'] = self.inputFileData['headers']['length']
				self.UpdateProgBar(60)
				customInsts =  [ {'name': item['name'], 'filepath': resource_path('sounds', item['filename']), 'obj': AudioSegment.from_ogg(resource_path('sounds', item['filename'])), 'pitch': item['pitch']} for item in data['customInsts']]
				self.noteSounds = vaniNoteSounds + customInsts
				self.UpdateProgBar(70)
				self.var.tool.opts = opts = ["(not applied)"] + [x['name'] for x in self.noteSounds] + ["Random"]
				self.InstToolCombox.configure(values=opts)
				self.UpdateProgBar(80)
				if data['maxLayer'] == 0:
					text = writencf(data)
				else:
					text = "The song must have only 1 layer in order to export as Nokia Composer Format."
				self.NCFOutput.configure(state='normal')
				self.NCFOutput.delete('1.0', 'end')
				self.NCFOutput.insert('end', text)
				self.NCFOutput.configure(state='disabled')
				self.UpdateProgBar(100)
				self.last.inputFileData = copy.deepcopy(data)
				self.RaiseFooter('Updated')
				#print("Updated class properties…", data == self.last.inputFileData)
			
			self.UpdateProgBar(-1)
		else:
			self.ToolsTabButton['state'] = 'disabled'

		self.update_idletasks()
	
	def OnBrowseExp(self):
		if self.filePath and self.inputFileData:
			asFile = bool(self.var.export.mode.get())
			if asFile:
				curr = (self.var.export.type.file[self.ExpConfigCombox.current()],)
				#print(curr)
				fext = curr[0][1][1:]
				self.exportFilePath.set( asksaveasfilename(title="Export file", initialfile=os.path.splitext(os.path.basename(self.filePath))[0]+fext, filetypes=curr) )
			else:
				print("Ask directory")
				curr = [(self.var.export.type.dtp[self.ExpConfigCombox.current()], '*.'),]
				fext =''
				self.exportFilePath.set( askdirectory(title="Export datapack (choose the directory to put the datapack)", initialdir=os.path.dirname(self.filePath), mustexist=False) )
			if self.exportFilePath.get():
				print(self.exportFilePath.get())
				if asFile:
					if not self.exportFilePath.get().lower().endswith(fext): self.exportFilePath.set( self.exportFilePath.get().split('.')[0] + fext )
				else:
					if '.' in self.exportFilePath.get().split('/')[-1]:
						self.exportFilePath.set( '/'.join(self.exportFilePath.get().split('/')[0:-1]) )
		
	def OnExport(self):
		if self.exportFilePath.get() is not None:
			self.ExpBrowseButton['state'] = self.ExpSaveButton['state'] = 'disabled'
			self.UpdateProgBar(10)
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
						fext = self.var.export.type.file[self.ExpConfigCombox.current()][1][2:]
						exportMusic(self, path, fext)
			else:
				if type == 0:
					exportDatapack(self, os.path.join(path, self.WnbsIDEntry.get()), 'wnbs')

			#self.UpdateProgBar(100)
			self.RaiseFooter('Exported')
			self.UpdateProgBar(-1)

			self.ExpBrowseButton['state'] = self.ExpSaveButton['state'] = 'normal'
	
	def UpdateProgBar(self, value, time=0.001):
		if value == -1 or time <= 0:
			self.progressbar.pack_forget()
			self.configure(cursor='arrow')
		else:
			self.configure(cursor='wait')
			self.progressbar["value"] = value
			self.progressbar.pack(side='right')
			self.progressbar.update()
			sleep(time)
	
	def RaiseFooter(self, text='', color='green', hid=False):
		if hid == False:
			#self.RaiseFooter(hid=True)
			text.replace('\s', ' ')
			self.footerLabel.configure(text=text, foreground=color)
			self.footerLabel.pack(side='left', fill='x')
			self.after(999, lambda: self.RaiseFooter(text=text, color=color, hid=True))
		else:
			self.footerLabel.pack_forget()
		self.footerLabel.update()


class AboutWindow(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self)
		self.parent = parent
		self.title("About this application...")

		self.logo = ImageTk.PhotoImage(Image.open(resource_path('icon.ico')).resize((128 ,128), Image.ANTIALIAS))

		logolabel = tk.Label(self, text="NBSTool", font=("Arial", 44), image=self.logo, compound='left')
		logolabel.pack(padx=30, pady=(10*2, 10))

		description = tk.Message(self, text="A tool to work with .nbs (Note Block Studio) files.\nAuthor: IoeCmcomc\nVersion: 0.7.0", justify='center')
		description.pack(fill='both', expand=False, padx=10, pady=10)

		githubLink = ttk.Button(self, text='GitHub', command= lambda: webbrowser.open("https://github.com/IoeCmcomc/NBSTool",new=True))
		githubLink.pack(padx=10, pady=10)

		self.lift()
		self.focus_force()
		self.grab_set()
		#self.grab_release()

		self.resizable(False, False)
		self.transient(self.parent)

		self.bind("<FocusOut>", self.Alarm)
		self.bind('<Escape>', lambda _: self.destroy())

		self.iconbitmap(resource_path("icon.ico"))

		WindowGeo(self, parent, 500, 300)

	def Alarm(self, event):
		self.focus_force()
		self.bell()

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
		else: self.justify = 'left'
		self['justify'] = self.justify

		if self.multiline:
			self.bind("<Configure>", lambda event: self.configure(width=event.width-10, justify=self.justify, anchor=self.anchor, wraplength=event.width-20, text=self.text+' '*999) )
#Currently unused
class SquareButton(tk.Button):
	def __init__(self, *args, **kwargs):
		self.blankImg = tk.PhotoImage()

		if "size" in kwargs:
			#print(kwargs['size'])
			self.size = kwargs['size']
			del kwargs['size']
		else:
			self.size = 30

		pprint(kwargs)

		tk.Button.__init__(self, *args, **kwargs)

		self.configure(image=self.blankImg, font=("Arial", self.size-3), width=self.size, height=self.size, compound=tk.CENTER)

class StackingWidget(tk.Frame):
	def __init__(self, parent, **kwargs):
		super().__init__(parent, **kwargs)
		self._frames = {}
		self._i = 0
		#self._shown = None
	def __getitem__(self, key):
		if key in self._frames: return self._frames[key][0]
		super().__getitem__(key)
	def append(self, frame, key=None):
		if isinstance(frame, (tk.Widget, ttk.Widget)):
			if not key:
				key = self._i
				self._i += 1
			self._frames[key] = [frame, None]
			#self._shown = key
			#return self._frames[name]
	def switch(self, key):
		for k, (w, o) in self._frames.items():
			if k == key:
				if o: w.pack(**o)
				else: w.pack()
			else: w.pack_forget()
	def pack(self, key=None, **opts):
		if key:
			self._frames[key][1] = opts
			#self._frames[key][0].pack(**opts)
		else: super().pack(**opts)
		if len(self._frames) == 1:
				self.switch(key)


def WindowGeo(obj, parent, width, height, mwidth=None, mheight=None):
	ScreenWidth = root.winfo_screenwidth()
	ScreenHeight = root.winfo_screenheight()
	
	WindowWidth = width or obj.winfo_reqwidth()
	WindowHeight = height or obj.winfo_reqheight()
	
	WinPosX = int(ScreenWidth / 2 - WindowWidth / 2)
	WinPosY = int(ScreenHeight / 2.3 - WindowHeight / 2)

	obj.minsize(mwidth or obj.winfo_width(), mheight or obj.winfo_height())
	obj.geometry("{}x{}+{}+{}".format(WindowWidth, WindowHeight, WinPosX, WinPosY))
	#obj.update()
	obj.update_idletasks()


def compactNotes(data, sepInst=1, groupPerc=1):
	sepInst, groupPerc = bool(sepInst), bool(groupPerc)
	r = data
	PrevNote = {'layer':-1, 'tick':-1}
	if sepInst:
		OuterLayer = 0
		iter = r['usedInsts'][0]
		if not groupPerc: iter += r['usedInsts'][1]
		for inst in iter:
			#print('Instrument: {}'.format(inst))
			InnerLayer = LocalLayer = c = 0
			#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
			for note in r['notes']:
				if note['inst'] == inst:
					c += 1
					if note['tick'] == PrevNote['tick']:
						LocalLayer += 1
						InnerLayer = max(InnerLayer, LocalLayer)
						note['layer'] = LocalLayer + OuterLayer
					else:
						LocalLayer = 0
						note['layer'] = LocalLayer + OuterLayer
						PrevNote = note
					#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
			OuterLayer += InnerLayer + 1
			#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
		if groupPerc:
			InnerLayer = LocalLayer = c = 0
			for note in r['notes']:
				if note['inst'] in r['usedInsts'][1]:
					c += 1
					if note['tick'] == PrevNote['tick']:
						LocalLayer += 1
						InnerLayer = max(InnerLayer, LocalLayer)
						note['layer'] = LocalLayer + OuterLayer
					else:
						LocalLayer = 0
						note['layer'] = LocalLayer + OuterLayer
						PrevNote = note
			OuterLayer += InnerLayer + 1
		r['maxLayer'] = OuterLayer - 1
	else:
		layer = 0
		for note in r['notes']:
			if note['tick'] == PrevNote['tick']:
				layer += 1
				note['layer'] = layer
			else:
				layer = 0
				note['layer'] = layer
				PrevNote = note
	return r

def exportMIDI(cls, path, byLayer=False):
	data = copy.deepcopy(cls.inputFileData)
	byLayer = bool(byLayer)

	if not byLayer:
		data = DataPostprocess(data)
		data = compactNotes(data)

	UniqInstEachLayer = {}
	for note in data['notes']:
		if note['layer'] not in UniqInstEachLayer:
			if note['isPerc']: UniqInstEachLayer[note['layer']] = -1
			else: UniqInstEachLayer[note['layer']] = note['inst']
		else:
			if not note['isPerc']: note['inst'] = UniqInstEachLayer[note['layer']]

	lenTrack = data['maxLayer'] + 1
	for i in range(lenTrack):
		if i not in UniqInstEachLayer: UniqInstEachLayer[i] = 0
	
	main_score = m21s.Score()

	percussions = (
	#(percussion_key, instrument, key)
	(35, 2, 64),
	(36, 2, 60),
	(37, 4, 60),
	(38, 3, 62),
	#(39, 4, 60),
	(40, 3, 58),
	#(41, 2, 60),
	(42, 3, 76),
	(43, 2, 67),
	#(44, 3, 76),
	(45, 2, 69),
	(46, 2, 72),
	(47, 2, 74),
	(48, 2, 77),
	(49, 2, 71),
	(50, 3, 77),
	(51, 3, 78),
	(52, 3, 62),
	(53, 3, 67),
	(54, 3, 72),
	(55, 3, 73),
	(56, 4, 55),
	#(57, 3, 67),
	(58, 4, 56),
	#(59, 3, 67),
	(60, 4, 63),
	(61, 4, 57),
	(62, 4, 62),
	(63, 2, 76),
	(64, 3, 69),
	#(65, 3, 67),
	#(66, 3, 62),
	#(67, 4, 62),
	(68, 4, 58),
	(69, 4, 74),
	(70, 4, 77),
	(73, 3, 71),
	(74, 4, 65),
	(75, 4, 72),
	(76, 4, 64),
	(77, 4, 59),
	(80, 4, 71),
	(81, 4, 76),
	(82, 3, 78)
	)

	instrument_codes = {-1:m21i.Percussion, 
						0: m21i.Harp,
						1: m21i.AcousticBass,
						5: m21i.Guitar,
						6: m21i.Flute,
						7: m21i.Handbells,
						8: m21i.ChurchBells,
						9: m21i.Xylophone,
						10: m21i.Xylophone,
						11: m21i.Piano,
						12: m21i.Piano,
						13: m21i.Piano,
						14: m21i.Banjo,
						15: m21i.Piano,
						}

	timeSign = data['headers']['time_sign']
	time = 0
	tempo = data['headers']['tempo'] * 60 / timeSign
	volume = 127
	
	c = 0
	for i in range(lenTrack):
		staff = m21s.Part()
		staff.append(m21.tempo.MetronomeMark(number=tempo)) #Tempo
		staff.timeSignature = m21.meter.TimeSignature('{}/4'.format(timeSign)) #Time signature
		staff.clef = m21.clef.TrebleClef() #Clef
		try:
			staff.append(instrument_codes[UniqInstEachLayer[i]]())
		except KeyError:
			staff.append(m21i.Piano())
		main_score.append(staff)

	for i, note in enumerate(data['notes']):
		time = note['tick'] / timeSign
		pitch = note['key'] + 21
		duration = 2 if note['duration'] == 0 else note['duration'] / timeSign
		track = note['layer']

		if note['isPerc']:
			for a, b, c in percussions:
				if c == pitch and b == note['inst']: pitch = a

		if byLayer:
			volume = int(data['layers'][note['layer']]['volume'] / 100 * 127)
		
		#print("track: {}, channel: {}, pitch: {}, time: {}, duration: {}, volume: {}".format(track, channel, pitch, time, duration, volume))

		a_note = m21.note.Note()
		a_note.pitch.midi = pitch #Pitch
		a_note.duration.quarterLength = 1 / 4 #Duration
		a_note.volume = volume
		main_score[track].append(a_note)
		a_note.offset = time

		cls.UpdateProgBar(10 + int( note['tick'] / (data['headers']['length']+1) * 80))

	mt = m21.metadata.Metadata()
	mt.title = mt.popularTitle = 'Title'
	mt.composer = 'Composer'
	main_score.insert(0, mt)
	
	#fn = main_score.write("midi", path)

	mid = m21.midi.translate.streamToMidiFile(main_score)

	if data['hasPerc']:
		for i in range(lenTrack):
			if UniqInstEachLayer[i] == -1:
				for el in mid.tracks[i].events:
					el.channel = 10

	cls.UpdateProgBar(95)

	mid.open(path, 'wb')
	mid.write()
	mid.close()

def exportMusic(cls, path, ext):
	start = time()
	noteSounds = cls.noteSounds
	notes = cls.inputFileData['notes']
	headers = cls.inputFileData['headers']
	tempo = headers['tempo']
	length = headers['length']+1
	layers = cls.inputFileData['layers']
	tickIndexes = cls.inputFileData['indexByTick']
	toUnsigned = lambda x: 256 + x if x < 0 else x
	tickSoundLength = max(len(x['obj']) for x in noteSounds)
	music = AudioSegment.silent(duration=int(length / tempo * 1000 + 500))
	lastInst = -1
	
	for currtick in range(length):
		currNotes = tickIndexes[currtick][1]

		for n, i in enumerate(currNotes):
			lstart = time()
			note = notes[i]
			currLayer = layers[note['layer']]
			inst = note['inst']
			
			if inst != lastInst:
				currNoteSound = noteSounds[inst]
				noteSoundObj = currNoteSound['obj']			
				
			ANoteSound = noteSoundObj._spawn(noteSoundObj.raw_data, overrides={'frame_rate': int(noteSoundObj.frame_rate * (2.0 ** ((note['key'] - currNoteSound['pitch']) / 12))) }).set_frame_rate(44100)
			
			if currLayer['volume'] != 100: ANoteSound = ANoteSound.apply_gain(noteSoundObj.dBFS - noteSoundObj.dBFS * (currLayer['volume'] / 100)) + 3
			
			if currLayer['stereo'] != 100: ANoteSound = ANoteSound.pan((toUnsigned(currLayer['stereo']) - 100) / 100)
			
			if len(currNotes) == 1: tickSound = ANoteSound
			elif n == 0: tickSound = ANoteSound + AudioSegment.silent(duration=tickSoundLength - len(ANoteSound))
			else: tickSound = tickSound.overlay(ANoteSound)
			
			lastInst = note['inst']

		if len(currNotes) > 0: music = music.overlay(tickSound.set_frame_rate(44100), position=int(note['tick'] / tempo * 1000))
		
		print('Processing {}/{} tick. Time: {:3f}. Done in {:3f} seconds.'.format(note['tick'], length, time() - start, time() - lstart))
			
	print("Processed in {:3f} seconds.".format(time() - start))
	
	'''
	meta = {'album': '',
		'artist': headers['author'],
		'comment': headers['description'],
		'date': date.today().year,
		'genre': 'Minecraft note block',
		'title': headers['name'],
		'track': ''}'''
		
	meta = {'genre': 'Minecraft note block'}
	
	music.set_frame_rate(44100).export(path, format=ext, tags=meta)
	print("Exported in {:3f} seconds.".format(time() - start))


def exportDatapack(cls, path, mode='none'):
	def writejson(path, jsout):
		with open(path, 'w') as f:
			json.dump(jsout, f, ensure_ascii=False)
	def writemcfunction(path, text):
			with open(path, 'w') as f:
				f.write(text)

	def wnbs():
		scoreObj = "wnbs_" + bname[:7]
		speed = int(min(data['headers']['tempo'] * 4, 120))
		length = data['headers']['length']
		
		os.makedirs(path, exist_ok=True)
		writejson(os.path.join(path, 'pack.mcmeta'), {"pack":{"description":"Note block song made with NBSTool.", "pack_format":1}} )
		os.makedirs(os.path.join(path, 'data', 'minecraft', 'tags', 'functions'), exist_ok=True)
		writejson(os.path.join(path, 'data', 'minecraft', 'tags', 'functions', 'load.json'), jsout = {"values":["{}:load".format(bname)]} )
		writejson(os.path.join(path, 'data', 'minecraft', 'tags', 'functions', 'tick.json'), jsout = {"values":["{}:tick".format(bname)]} )
		os.makedirs(os.path.join(path, 'data', bname, 'functions'), exist_ok=True)

		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'load.mcfunction'),
"""scoreboard objectives add {0} dummy
scoreboard objectives add {0}_t dummy
scoreboard players set speed {0} {1}""".format(scoreObj, speed) )
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'tick.mcfunction'),
"""execute as @a[tag={0}] run scoreboard players operation @s {0} += speed {0}
execute as @a[tag={0}] run function {1}:tree/0_{2}
execute as @e[type=armor_stand, tag=WNBS_Marker] at @s unless block ~ ~-1 ~ minecraft:note_block run kill @s""".format(scoreObj, bname, 2**(floor(log2(length))+1)-1) )
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'play.mcfunction'),
"""tag @s add {0}
scoreboard players set @s {0}_t -1
""".format(scoreObj) )
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'pause.mcfunction'),
			"tag @s remove {}".format(scoreObj) )
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'stop.mcfunction'),
"""tag @s remove {0}
scoreboard players reset @s {0}
scoreboard players reset @s {0}_t""".format(scoreObj) )
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'remove.mcfunction'),
"""scoreboard objectives remove {0}
scoreboard objectives remove {0}_t""".format(scoreObj) )

		text = ''
		for k, v in instLayers.items():
			for i in range(len(v)):
				text += 'execute run give @s minecraft:armor_stand{{display: {{Name: "{{\\"text\\":\\"{}\\"}}" }}, EntityTag: {{Marker: 1b, NoGravity:1b, Invisible: 1b, Tags: ["WNBS_Marker"], CustomName: "{{\\"text\\":\\"{}\\"}}" }} }}\n'.format(
					"{}-{}".format(noteSounds[k]['name'], i), "{}-{}".format(k, i)
				)
		writemcfunction(os.path.join(path, 'data', bname, 'functions', 'give.mcfunction'), text)

		colNotes = { tick: [x for x in data['notes'] if x['tick'] == tick] for tick in range(length) }
		#pprint(colNotes)
		print(len(colNotes))

		os.makedirs(os.path.join(path, 'data', bname, 'functions', 'notes'), exist_ok=True)
		for tick in range(length):
			currNotes = colNotes[tick]
			text = ""
			#text = "say Calling function {}:notes/{}\n".format(bname, tick)
			for note in currNotes:
				text += \
"""execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run setblock ~ ~ ~ minecraft:note_block[instrument={instname},note={key}] replace
execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:redstone_block replace minecraft:air
execute as @e[type=armor_stand, tag=WNBS_Marker, name=\"{inst}-{order}\"] at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:note_block[instrument={instname}] run fill ^ ^ ^-1 ^ ^ ^-1 minecraft:air replace minecraft:redstone_block
""".format(
						obj=scoreObj, tick=tick, inst=note['inst'], order=instLayers[note['inst']].index(note['layer']), instname=noteSounds[note['inst']]['name'], key=max(33, min(57, note['key'])) - 33
					)
			if tick == length-1: text += "execute run function {}:stop".format(bname)
			else: text += "scoreboard players set @s {}_t {}".format(scoreObj, tick)
			if text != "": writemcfunction(os.path.join(path, 'data', bname, 'functions', 'notes', str(tick)+'.mcfunction'), text)

		os.makedirs(os.path.join(path, 'data', bname, 'functions', 'tree'), exist_ok=True)
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
				
				#print(str(step) + " " + str(segments) + "    " + str(min1) + " " + str(max1) + " " + str(min2) + " " + string(max2))
				
				if min1 <= length:
					if step == steps-1: # Last step, play the tick
						try:
							if len(colNotes[min1]) > 0: text += "execute as @s[scores={{{0}={1}..{2}, {0}_t=..{3}}}] run function {4}:notes/{5}\n".format(scoreObj, min1*80, (max1+1)*80+40, min1-1, bname, min1)
						except KeyError: break
						if min2 <= length:
							try:
								if len(colNotes[min2]) > 0: text += "execute as @s[scores={{{0}={1}..{2}, {0}_t=..{3}}}] run function {4}:notes/{5}".format(scoreObj, min2*80, (max2+1)*80+40, min2-1, bname, min2)
							except KeyError: break
					else: # Don't play yet, refine the search
						for i in range(min1, min(max1, length)+1):
							try:
								if len(colNotes[i]) > 0:
									text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}\n".format(scoreObj, min1*80, (max1+1)*80+40, bname, min1, max1)
									break
							except KeyError: break
						for i in range(min2, min(max2, length)+1):
							try:
								if len(colNotes[i]) > 0:
									text += "execute as @s[scores={{{}={}..{}}}] run function {}:tree/{}_{}".format(scoreObj, min2*80, (max2+2)*80+40, bname, min2, max2)
									break
							except KeyError: break
					if text != "":
						#text = "say Calling function {}:tree/{}_{}\n".format(bname, min1, max2) + text
						writemcfunction(os.path.join(path, 'data', bname, 'functions', 'tree', '{}_{}.mcfunction'.format(min1, max2)), text)
				else: break

	path = os.path.join(*os.path.normpath(path).split())
	bname = os.path.basename(path)
	
	data = DataPostprocess(cls.inputFileData)
	data = compactNotes(data, groupPerc=False)
	
	noteSounds = cls.noteSounds

	instLayers = {}
	for note in data['notes']:
		if note['inst'] not in instLayers:
			instLayers[note['inst']] = [note['layer']]
		elif note['layer'] not in instLayers[note['inst']]:
			instLayers[note['inst']].append(note['layer'])
	#pprint(instLayers)
	
	locals()[mode]()
	print("Done!")

if __name__ == "__main__":
	
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

	print('Importing sounds...')
	vaniNoteSounds = [ {'name': item['name'], 'filepath': resource_path('sounds', item['filename']), 'obj': AudioSegment.from_ogg(resource_path('sounds', item['filename'])), 'pitch': 45} for item in vaniNoteSounds]

	print('Imported sounds.')
	print('Creating root...')

	root = tk.Tk()
	app = MainWindow(root)
	print('Creating app...')

	if len(sys.argv) == 2: app.OnOpenFile(sys.argv[1])

	root.iconbitmap(resource_path("icon.ico"))
	print('Ready')
	root.mainloop()
	
	print("The app was closed.")