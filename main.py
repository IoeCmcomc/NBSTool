import sys, os, operator, webbrowser, traceback

import tkinter as tk
import tkinter.ttk as ttk

import tkinter.messagebox as tkmsgbox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.scrolledtext import ScrolledText

from time import sleep
from random import randrange
from pprint import pprint

from attr import Attr
from nbsio import opennbs, writenbs

#sys.stdout = open('main_log.txt', 'w')

class MainWindow(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.properties()
		self.elements()
		self.WindowBind()
		self.UpdateVar(True)
		self.update()
		self.pack(fill='both', expand=True)
		self.update()
		WindowGeo(self.parent, self.parent, 800, 500, 600, 500)
	
	def properties(self):
		self.filePath = None
		self.inputFileData = None
		self.last = Attr()
		self.last.inputFileData = None
		self.var = Attr()
	
	def elements(self):
		self.parent.title("NBS Tool")
		self.style = ttk.Style()
		self.style.theme_use("default")
		
		#Menu bar
		self.menuBar = tk.Menu(self)
		self.parent.config(menu=self.menuBar)
		self.menus()
		
		#Tabs
		self.NbTabs = ttk.Notebook(self)
		self.tabs()
		self.NbTabs.pack(fill='both', expand=True)
		
		#Footer
		tk.Frame(self, height=5).pack()

		self.footer = tk.Frame(self, relief='groove', borderwidth=1, height=25)
		self.footer.pack_propagate(False)
		self.footer.pack(fill='x')
		self.footerElements()
	
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
		
		#"Tools" tab
		self.ToolsTab = tk.Frame(self.NbTabs)

		self.ToolsTab.rowconfigure(0, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(1, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(2)
		
		self.ToolsTab.columnconfigure(0, weight=1, uniform='b')
		self.ToolsTab.columnconfigure(1, weight=1, uniform='b')

		self.ToolsTabElements()
		self.NbTabs.add(self.ToolsTab, text="Tools")
		
	def GeneralTabElements(self):
		padx, pady = 5, 5

		#"Open file" frame
		self.OpenFileFrame = tk.Frame(self.GeneralTab, relief='ridge', borderwidth=1)
		self.OpenFileFrame.grid(row=0, columnspan=2, sticky='ew')
		
		self.OpenFileLabel = tk.Label(self.OpenFileFrame, text="Open file:", anchor='w', width=8)
		self.OpenFileLabel.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileEntry = tk.Entry(self.OpenFileFrame)
		self.OpenFileEntry.pack(side='left', fill='x', padx=padx, expand=True)
		
		self.BrowseFileButton = ttk.Button(self.OpenFileFrame, text="Browse", command = lambda: self.OnBrowseFile() )
		self.BrowseFileButton.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileButton = ttk.Button(self.OpenFileFrame, text="Open", command = lambda: self.OnOpenFile('', True) )
		self.OpenFileButton.pack(side='left', padx=padx, pady=pady)
		
		lfp = 10
		
		#File metadata frame
		self.FileMetaFrame = tk.LabelFrame(self.GeneralTab, text="Metadata")
		self.FileMetaFrame.grid(row=1, column=0, padx=lfp, pady=lfp, sticky='nsew')
		
		self.FileMetaMess = tk.Message(self.FileMetaFrame, text="No flie was found.")
		self.FileMetaMess.pack(fill='both', expand=True, padx=padx, pady=padx)
		
		#More infomation frame
		self.FileInfoFrame = tk.LabelFrame(self.GeneralTab, text="Infomations")
		self.FileInfoFrame.grid(row=1, column=1, padx=lfp, pady=lfp, sticky='nsew')
		
		self.FileInfoMess = tk.Message(self.FileInfoFrame, text="No flie was found.")
		self.FileInfoMess.pack(fill='both', expand=True, padx=padx, pady=pady)
	
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
		
		self.var.tool.inst = ["Harp (piano)" ,"Double Bass" ,"Bass Drum" ,"Snare Drum" ,"Click" ,"Guitar" ,"Flute" ,"Bell" ,"Chime" ,"Xylophone"]
		self.var.tool.inst.opt = ["(not applied)"] + self.var.tool.inst + ["Random"]
		self.InstToolCombox = ttk.Combobox(self.InstToolFrame, state='readonly', values=self.var.tool.inst.opt._)
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
		self.CompactToolChkOpt1 = FlexCheckbutton(self.CompactToolFrame, text="Automatic separate notes by instruments (remain some spaces)", variable=self.var.tool.compact.opt1, state='disabled', anchor='w')
		self.CompactToolChkOpt1.select()
		self.CompactToolChkOpt1.pack(padx=padx*5, pady=pady)
		
		#'Apply' botton
		self.ToolsTabButton = ttk.Button(self.ToolsTab, text="Apply", state='disabled', command = self.OnApplyTool )
		self.ToolsTabButton.grid(row=2, column=1, sticky='se', padx=fpadx, pady=fpady)
	
	def footerElements(self):
		self.footerLabel = tk.Label(self.footer, text="Footer")
		self.footerLabel.pack(side='left', fill='x')
		self.var.footerLabel = 0
		
		self.sizegrip = ttk.Sizegrip(self.footer)
		self.sizegrip.pack(side='right')

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
		self.bind_class("TButton", "<Return>", lambda e: e.widget.invoke())
		self.bind_class("Checkbutton", "<Return>", lambda e: e.widget.toggle())
		self.bind_class("Checkbutton", "<Return>", lambda e: e.widget.invoke())
		self.bind_class("TCombobox", "<Return>", lambda e: e.widget.event_generate('<Down>'))
		self.bind_class("Entry" ,"<Button-3>", self.popupmenus)
		
	def popupmenus(self, event):
		w = event.widget
		self.popupMenu = tk.Menu(self, tearoff=False)
		self.popupMenu.add_command(label="Select all", accelerator="Ctrl+A", command=lambda: w.event_generate("<Control-a>"))
		self.popupMenu.add_separator()
		self.popupMenu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: w.event_generate("<Control-x>"))
		self.popupMenu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: w.event_generate("<Control-c>"))
		self.popupMenu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: w.event_generate("<Control-v>"))
		self.popupMenu.tk.call("tk_popup", self.popupMenu, event.x_root, event.y_root)

	def onClose(self, event):
		self.parent.quit()
		self.parent.destroy()

	def OnBrowseFile(self, doOpen=False):
		types = [('Note Block Studio file', '*.nbs'), ('All files', '*')]
		filename = askopenfilename(filetypes = types)
		self.OpenFileEntry.delete(0,'end')
		self.OpenFileEntry.insert(0, filename)
		if doOpen:
			self.OnOpenFile(filename, None)

	def OnOpenFile(self, fileName, fromEntry=False):
		if fromEntry: fileName = self.OpenFileEntry.get()
		self.UpdateProgBar(20)
		if fileName != '':
			try:
				data = opennbs(fileName)
			except Exception as ex:
				self.RaiseFooter(type(ex).__name__, 'darkred')
				self.UpdateProgBar(-1)
				print('='*40+"\n ERROR!"+"\n"+'='*40)
				print(traceback.format_exc())
				return
			if data is not None:
				self.UpdateProgBar(40)
				self.inputFileData = data
				self.filePath = fileName
		
			self.UpdateVar()
			self.RaiseFooter('Opened')
			self.UpdateProgBar(100)
		self.UpdateProgBar(-1)
			#print(self.inputFileData)
	
	def OnSaveFile(self, saveAsNewFile=False):
		if self.inputFileData is not None:
			if saveAsNewFile is True:
				types = [('Note Block Studio file', '*.nbs'), ('All files', '*')]
				filename = asksaveasfilename(filetypes = types)
			else: filename = self.filePath
			self.UpdateProgBar(50)
			writenbs(filename, self.inputFileData)
			self.UpdateProgBar(100)
			self.RaiseFooter('Saved')
			self.UpdateProgBar(-1)
	
	def toggleCompactToolOpt(self, id=1):
		if id >= 1:
			self.CompactToolChkOpt1["state"] = "disable" if self.var.tool.compact.get() == 0 else "normal"

	def OnApplyTool(self):
		self.ToolsTabButton['state'] = 'disabled'
		self.UpdateProgBar(0)
		data = self.inputFileData
		ticklen = data['headers']['length']
		layerlen = data['maxLayer']
		instOpti = self.InstToolCombox.current()
		self.UpdateProgBar(30)
		for i, note in enumerate(data['notes']):
			#Flip
			if bool(self.var.tool.flip.horizontal.get()): note['tick'] = ticklen - note['tick']
			if bool(self.var.tool.flip.vertical.get()): note['layer'] = layerlen - note['layer']

			#Instrument change
			if instOpti > 0:
				note['inst'] = randrange(len(self.var.tool.inst)) if instOpti > len(self.var.tool.inst) else instOpti-1
		self.UpdateProgBar(50)
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

		self.UpdateProgBar(70)
		#Compact
		if bool(self.var.tool.compact.get()): data = compactNotes(data, self.var.tool.compact.opt1.get(), groupPerc=0)
		self.UpdateProgBar(80)
		#Sort notes
		data['notes'] = sorted(data['notes'], key = operator.itemgetter('tick', 'layer') )
		self.UpdateProgBar(90)
		self.inputFileData = data
		self.UpdateProgBar(100)
		self.RaiseFooter('Applied')
		self.UpdateProgBar(-1)
		self.ToolsTabButton['state'] = 'normal'
	
	def UpdateVar(self, repeat=False):
		#print("Started updating….")
		#Update general tab
		data = self.inputFileData
		if data is not None:
			self.ToolsTabButton['state'] = 'normal'
			if data != self.last.inputFileData:
				self.UpdateProgBar(40)
				headers = data['headers']
				
				self.UpdateProgBar(60)
				text = "File version: {}\nFirst custom inst index: {}\nSong length: {}\nSong height: {}\nSong name: {}\nSong author: {}\nComposer: {}\nSong description: {}\nTempo: {}\nAuto-saving: {}\nTime signature: {}\nMinutes spent: {}\n'left' clicks: {}\nRight clicks: {}\nBlocks added: {}\nBlocks removed: {}\nMIDI/Schematic file name: {}".format \
				( headers['file_version'], headers['vani_inst'], headers['length'], headers['height'], headers['name'], headers['orig_author'], headers['author'], headers['description'], headers['tempo'], "Enabled (save every {} minutes(s)".format(headers['auto-saving_time']) if headers['auto-saving'] else "Disabled", headers['time_sign'], headers['minutes_spent'], headers['left_clicks'], headers['right_clicks'], headers['block_added'], headers['block_removed'], headers['import_name'] )
				self.FileMetaMess.configure(text=text)
				
				self.UpdateProgBar(80)
				text = "File format: {}\nHas percussion: {}\nMax layer with at least 1 note block: {}\nCustom instrument(s): {}".format \
				( "Old" if data['IsOldVersion'] else "New", data['hasPerc'], data['maxLayer'], headers['inst_count'] )
				self.FileInfoMess.configure(text=text)
				
				self.UpdateProgBar(100)
				self.last.inputFileData = data
				#print("Updated class properties…", data == self.last.inputFileData)
			
			self.UpdateProgBar(-1)
		else:
			self.ToolsTabButton['state'] = 'disabled'

		self.update_idletasks()
		if repeat: self.after(1000, lambda: self.UpdateVar(True))
	
	def UpdateProgBar(self, value, time=0.05):
		if value == -1:
			self.progressbar.pack_forget()
		else:
			self.progressbar["value"] = value
			self.progressbar.pack(side='right')
			self.progressbar.update()
			sleep(time)
	
	def RaiseFooter(self, text='', color='green', hid=False):
		if hid == False:
			#self.RaiseFooter(hid=True)
			text.replace("\s", " ")
			self.footerLabel.configure(text=text, foreground=color)
			self.footerLabel.pack(side='left', fill='x')
			self.footerLabel.update()
			self.after(999, lambda: self.RaiseFooter(text=text, color=color, hid=True))
		else:
			self.footerLabel.pack_forget()
			self.footerLabel.update()

class AboutWindow(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self)
		self.parent = parent
		self.alarmTime = 0
		self.title("About this application...")

		logo = tk.Label(self, text="NBSTool", font=("Arial", 44))
		logo.pack(padx=30, pady=10)

		description = tk.Message(self, text="A tool to work with .nbs (Note Block Studio) files.\nAuthor: IoeCmcomc\nVersion: 0,26", justify='center')
		description.pack(fill='both', expand=False, padx=10, pady=10)

		githubLink = ttk.Button(self, text='GitHub', command= lambda: webbrowser.open("https://github.com/IoeCmcomc/NBSTool",new=True))
		githubLink.pack(padx=10, pady=10)

		self.lift()
		self.focus_force()
		self.grab_set()
		self.grab_release()

		self.resizable(False, False)
		self.transient(self.parent)

		self.bind("<FocusOut>", self.Alarm)
		self.bind('<Escape>', lambda _: self.destroy())

		WindowGeo(self, parent, 400, 250)

	def Alarm(self, event):
		print(dir(event))
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

def WindowGeo(obj, parent, width, height, mwidth=None, mheight=None):
	ScreenWidth = root.winfo_screenwidth()
	ScreenHeight = root.winfo_screenheight()
	
	WindowWidth = width or obj.winfo_reqwidth()
	WindowHeight = height or obj.winfo_reqheight()
	
	WinPosX = int(ScreenWidth / 2 - WindowWidth / 2)
	WinPosY = int(ScreenHeight / 2.3 - WindowHeight / 2)

	obj.geometry("{}x{}+{}+{}".format(WindowWidth, WindowHeight, WinPosX, WinPosY))
	obj.update()
	obj.minsize(mwidth or obj.winfo_width(), mheight or obj.winfo_height())

def flipNotes(data, vertically=0, horizontally=0):
	vertically, horizontally = bool(vertically), bool(horizontally)
	ticklen = data['headers']['length']
	layerlen = data['maxLayer']
	if vertically or horizontally:
		for note in data['notes']:
			if horizontally: note['tick'] = ticklen - note['tick']
			if vertically: note['layer'] = layerlen - note['layer']
	return data

def compactNotes(data, sepInst=1, groupPerc=0):
	sepInst, groupPerc = bool(sepInst), bool(groupPerc)
	r = data
	if sepInst:
		print(r['usedInsts'])
		print(r['usedInsts'][0]+r['usedInsts'][1])
		OuterLayer = 0
		for inst in r['usedInsts'][0]+r['usedInsts'][1]:
			#print('Instrument: {}'.format(inst))
			InnerLayer = LocalLayer = c = 0
			#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
			PrevNote = {'layer':-1, 'tick':-1}
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
	else:
		PrevNote = {'layer':-1, 'tick':-1}
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

#Credit: https://stackoverflow.com/questions/42474560/pyinstaller-single-exe-file-ico-image-in-title-of-tkinter-main-window
def resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)


root = tk.Tk()
app = MainWindow(root)
root.iconbitmap(resource_path('icon.ico'))
root.mainloop()
print("The app was closed.")