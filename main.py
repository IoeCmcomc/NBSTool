import sys, operator, webbrowser

from time import sleep
from random import randrange

#from tkinter import *
from tkinter import Tk, Menu, Frame, LabelFrame,  Button, Label, Message, \
Checkbutton, Entry, Text, IntVar, StringVar, messagebox, END, Toplevel
from tkinter.ttk import Button, Style, Notebook, Progressbar, Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.scrolledtext import ScrolledText

from attr import Attr
from nbsio import opennbs, writenbs

#sys.stdout = open('main_log.txt', 'w')

class MainWindow(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.properties()
		self.elements()
		self.WindowBind()
		self.UpdateVar(True)
		self.pack(fill='both', expand=True)
		WindowGeo(self.parent, self.parent, width=800, height=500)
	
	def properties(self):
		self.filePath = None
		self.inputFileData = None
		self.last = Attr()
		self.last.inputFileData = None
		self.var = Attr()
	
	def elements(self):
		self.parent.title("NBS Tool")
		self.style = Style()
		self.style.theme_use("default")
		
		#Menu bar
		self.menuBar = Menu(self)
		self.parent.config(menu=self.menuBar)
		self.menus()
		
		#Tabs
		self.NbTabs = Notebook(self, padding=(0, 10, 0, 10))
		self.tabs()
		self.NbTabs.pack(expand=True, fill='both')
		
		#Footer
		self.footer = Frame(self, relief='groove', borderwidth=1, height=30)
		self.footer.pack(fill='x')
		
		self.footerElements()
	
	def menus(self):
		# 'File' menu
		self.fileMenu = Menu(self.menuBar, tearoff=False)
		self.menuBar.add_cascade(label="File", menu=self.fileMenu)
		
		self.fileMenu.add_command(label="Open", command = lambda: self.OnBrowseFile(True))
		self.fileMenu.add_command(label="Save", command=self.OnSaveFile)
		self.fileMenu.add_command(label="Save as new file", command = lambda: self.OnSaveFile(True))

		self.helpMenu = Menu(self.menuBar, tearoff=False)
		self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

		self.helpMenu.add_command(label="About", command=lambda: AboutWindow(self))

	def tabs(self):
		#"General" tab
		self.GeneralTab = Frame(self.NbTabs)
		
		self.GeneralTab.rowconfigure(0, pad=3)
		self.GeneralTab.rowconfigure(1, pad=3, weight=1)
		
		self.GeneralTab.columnconfigure(0, pad=3, weight=1, uniform='a')
		self.GeneralTab.columnconfigure(1, pad=3, weight=1, uniform='a')
		
		self.GeneralTabElements()
		self.NbTabs.add(self.GeneralTab, text="General")
		
		#"Tools" tab
		self.ToolsTab = Frame(self.NbTabs)

		self.ToolsTab.rowconfigure(0, pad=3, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(1, pad=3, weight=1, uniform='b')
		self.ToolsTab.rowconfigure(2, pad=3)
		
		self.ToolsTab.columnconfigure(0, pad=3, weight=1, uniform='b')
		self.ToolsTab.columnconfigure(1, pad=3, weight=1, uniform='b')

		self.ToolsTabElements()
		self.NbTabs.add(self.ToolsTab, text="Tools")
	
	def GeneralTabElements(self):
		padx, pady = 5, 5

		#"Open file" frame
		self.OpenFileFrame = Frame(self.GeneralTab, relief='ridge', borderwidth=1)
		self.OpenFileFrame.grid(row=0, columnspan=2, sticky='ew')
		
		self.OpenFileLabel = Label(self.OpenFileFrame, text="Open file:", anchor='w', width=8)
		self.OpenFileLabel.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileEntry = Entry(self.OpenFileFrame)
		self.OpenFileEntry.pack(side='left', fill='x', padx=padx, expand=True)
		
		self.BrowseFileButton = Button(self.OpenFileFrame, text="Browse", command = lambda: self.OnBrowseFile() )
		self.BrowseFileButton.pack(side='left', padx=padx, pady=pady)
		
		self.OpenFileButton = Button(self.OpenFileFrame, text="Open", command = lambda: self.OnOpenFile('', True) )
		self.OpenFileButton.pack(side='left', padx=padx, pady=pady)
		
		lfp = 10
		
		#File metadata frame
		self.FileMetaFrame = LabelFrame(self.GeneralTab, text="Metadata")
		self.FileMetaFrame.grid(row=1, column=0, padx=lfp, pady=lfp, sticky='nsew')
		
		self.FileMetaMess = Message(self.FileMetaFrame, text="No flie was found.")
		self.FileMetaMess.bind("<Configure>", lambda e: self.FileMetaMess.configure(width=e.width-10))
		self.FileMetaMess.pack(fill='both', expand=True, padx=padx, pady=padx)
		
		#More infomation frame
		self.FileInfoFrame = LabelFrame(self.GeneralTab, text="Infomations")
		self.FileInfoFrame.grid(row=1, column=1, padx=lfp, pady=lfp, sticky='nsew')
		
		self.FileInfoMess = Message(self.FileInfoFrame, text="No flie was found.")
		self.FileInfoMess.bind("<Configure>", lambda e: self.FileInfoMess.configure(width=e.width-10))
		self.FileInfoMess.pack(fill='both', expand=True, padx=padx, pady=pady)
	
	def ToolsTabElements(self):
		fpadx, fpady = 10, 10
		padx, pady = 5, 0

		#Flip tool
		self.FlipToolFrame = LabelFrame(self.ToolsTab, text="Flipping")
		self.FlipToolFrame.grid(row=0, column=0, sticky='nsew', padx=fpadx, pady=fpady)
		
		self.FlipToolMess = Message(self.FlipToolFrame, anchor='w', text="Flip the note sequence horizontally (by tick), vertically (by layer) or both: ")
		self.FlipToolMess.bind("<Configure>", lambda e: self.FlipToolMess.configure(width=e.width-10))
		self.FlipToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)
		
		self.var.tool.flip.vertical = IntVar()
		self.FilpToolCheckV = Checkbutton(self.FlipToolFrame, text="Vertically", variable=self.var.tool.flip.vertical)
		self.FilpToolCheckV.pack(side='left', padx=padx, pady=pady)
		
		self.var.tool.flip.horizontal = IntVar()
		self.FilpToolCheckH = Checkbutton(self.FlipToolFrame, text="Horizontally", variable=self.var.tool.flip.horizontal)
		self.FilpToolCheckH.pack(side='left', padx=padx, pady=pady)

		#Instrument tool
		self.InstToolFrame = LabelFrame(self.ToolsTab, text="Note's instrument")
		self.InstToolFrame.grid(row=0, column=1, sticky='nsew', padx=fpadx, pady=fpady)
		
		self.InstToolMess = Message(self.InstToolFrame, anchor='w', text="Change all note's instrument to:")
		self.InstToolMess.bind("<Configure>", lambda e: self.InstToolMess.configure(width=e.width-10))
		self.InstToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)
		
		self.var.tool.inst = ["Harp (piano)" ,"Double Bass" ,"Bass Drum" ,"Snare Drum" ,"Click" ,"Guitar" ,"Flute" ,"Bell" ,"Chime" ,"Xylophone"]
		self.var.tool.inst.opt = ["(not applied)"] + self.var.tool.inst + ["Random"]
		self.InstToolCombox = Combobox(self.InstToolFrame, state='readonly', values=self.var.tool.inst.opt._)
		self.InstToolCombox.current(0)
		self.InstToolCombox.pack(side='left', fill='both' ,expand=True, padx=padx, pady=pady)

		#Compact tool
		self.CompactToolFrame = LabelFrame(self.ToolsTab, text="Compacting")
		self.CompactToolFrame.grid(row=1, column=0, sticky='nsew', padx=fpadx, pady=fpady)

		self.CompactToolMess = Message(self.CompactToolFrame, anchor='w', text="Remove spaces between notes vertically (by layer) and group them by instruments.")
		self.CompactToolMess.bind("<Configure>", lambda e: self.CompactToolMess.configure(width=e.width-10))
		self.CompactToolMess.pack(fill='both', expand=True, padx=padx, pady=pady)

		self.var.tool.compact = IntVar()
		self.CompactToolCheck = Checkbutton(self.CompactToolFrame, text="Compact notes"+" "*40, variable=self.var.tool.compact, command=self.toggleCompactToolOpt)
		self.CompactToolCheck.pack(anchor='w', padx=padx, pady=pady)

		self.var.tool.compact.opt1 = IntVar()
		self.CompactToolOpt1 = Checkbutton(self.CompactToolFrame, text="Automatic separate notes by instruments (remain some spaces)", variable=self.var.tool.compact.opt1, state='disabled', justify='left')
		self.CompactToolOpt1.bind("<Configure>", lambda e: self.CompactToolOpt1.configure(wraplength=e.width-20))
		self.CompactToolOpt1.select()
		#print(dir(self.CompactToolOpt1))
		self.CompactToolOpt1.pack(anchor='w', padx=padx*5, pady=pady)
		
		#'Apply' botton
		self.ToolsTabButton = Button(self.ToolsTab, text="Apply", state='disabled', command = self.OnApplyTool )
		self.ToolsTabButton.grid(row=2, column=1, sticky='se', padx=fpadx, pady=fpady)
	
	def RawTabElements(self):
		self.txt = ScrolledText(self.RawTab)
		self.txt.pack(side='left', fill='both', expand=1, padx=10, pady=10)
	
	def footerElements(self):
		self.footerLabel = Label(self.footer, text="Footer")
		self.footerLabel.pack(side='left', fill='x')
		self.var.footerLabel = 0
		
		self.progressbar = Progressbar(self.footer,orient="horizontal",length=300,mode="determinate")		#self.progressbar.pack(side='right')
		self.progressbar["value"] = 0
		self.progressbar["maximum"] = 100
		#self.progressbar.start()
		#self.progressbar.stop()
	
	def WindowBind(self):
		#Buttons
		self.master.bind('<Escape>', lambda _: self.parent.destroy())
		self.master.bind('<Control-o>', lambda _: self.OnBrowseFile(True))
		self.master.bind('<Control-s>', self.OnSaveFile)
		
	def OnBrowseFile(self, doOpen=False):
		types = [('Note Block Studio file', '*.nbs'), ('All files', '*')]
		filename = askopenfilename(filetypes = types)
		self.OpenFileEntry.delete(0,END)
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
				template = "An exception of type {0} occurred.\nArguments: {1!r}"
				message = template.format(type(ex).__name__, ex.args)
				print(message)
				self.RaiseFooter(type(ex).__name__, 'red')
				self.UpdateProgBar(-1)
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
			self.CompactToolOpt1["state"] = "disable" if self.var.tool.compact.get() == 0 else "normal"

	def OnApplyTool(self):
		self.UpdateProgBar(0)
		data = self.inputFileData
		self.UpdateProgBar(20)
		applied = flipNotes(data, self.var.tool.flip.vertical.get(), self.var.tool.flip.horizontal.get())
		self.UpdateProgBar(40)
		instOpti = self.InstToolCombox.current()
		if instOpti > 0:
			for note in applied['notes']:
				note['inst'] = randrange(len(self.var.tool.inst)) if instOpti > len(self.var.tool.inst) else instOpti-1
		self.UpdateProgBar(60)
		if self.var.tool.compact.get() == 1: applied = compactNotes(applied, self.var.tool.compact.opt1.get(), groupPerc=0)
		self.UpdateProgBar(80)
		applied['notes'] = sorted(applied['notes'], key = operator.itemgetter('tick', 'layer') )

		self.inputFileData = applied
		self.UpdateProgBar(100)
		self.RaiseFooter('Applied')
		self.UpdateProgBar(-1)
	
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

class AboutWindow(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		self.parent = parent
		self.alarmTime = 0
		self.title("About this application...")

		logo = Label(self, text="NBSTool", font=("Arial", 44))
		logo.pack(padx=30, pady=10)

		description = Message(self, text="A tool to work with .nbs (Note Block Studio) files.\nAuthor: IoeCmcomc\nVersion: 0,1", justify='center')
		description.bind("<Configure>", lambda e: description.configure(width=e.width-10))
		description.pack(fill='both', expand=False, padx=10, pady=10)

		githubLink = Button(self, text='GitHub', command= lambda: webbrowser.open("https://github.com/IoeCmcomc/NBSTool",new=True))
		githubLink.pack(padx=10, pady=10)

		self.lift()
		self.focus_force()
		self.grab_set()
		self.grab_release()

		self.resizable(False, False)
		self.transient(self.parent)

		self.bind("<FocusOut>", self.Alarm)
		self.bind('<Escape>', lambda _: self.destroy())

		WindowGeo(self, parent, 400, 250, dialog=True)

	def Alarm(self, event):
		print(dir(event))
		self.focus_force()
		self.bell()


def WindowGeo(obj, parent, width, height, dialog=False):
		
	#print(parent.winfo_screenwidth(), parent.winfo_screenheight())

	ScreenWidth = root.winfo_screenwidth()
	ScreenHeight = root.winfo_screenheight()
	
	WindowWidth = width or obj.winfo_reqwidth()
	WindowHeight = height or obj.winfo_reqheight()
	
	#print(WindowWidth, WindowHeight)

	WinPosX = int(ScreenWidth / 2 - WindowWidth / 2)
	WinPosY = int(ScreenHeight / 2.3 - WindowHeight / 2)

	#print(WinPosX, WinPosY)

	obj.geometry("{}x{}+{}+{}".format(WindowWidth, WindowHeight, WinPosX, WinPosY))
	obj.update()
	obj.minsize(obj.winfo_width(), obj.winfo_height())

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
			lastNote = {'layer':-1, 'tick':-1}
			for note in r['notes']:
				if note['inst'] == inst:
					c += 1
					if note['tick'] == lastNote['tick']:
						LocalLayer += 1
						InnerLayer = max(InnerLayer, LocalLayer)
						note['layer'] = LocalLayer + OuterLayer
					else:
						LocalLayer = 0
						note['layer'] = LocalLayer + OuterLayer
						lastNote = note
					#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
			OuterLayer += InnerLayer + 1
			#print('OuterLayer: {}; Innerlayer: {}; LocalLayer: {}; c: {}'.format(OuterLayer, InnerLayer, LocalLayer, c))
	else:
		lastNote = {'layer':-1, 'tick':-1}
		layer = 0
		for note in r['notes']:
			if note['tick'] == lastNote['tick']:
				layer += 1
				note['layer'] = layer
			else:
				layer = 0
				note['layer'] = layer
				lastNote = note
	return r

root = Tk()
app = MainWindow(root)
root.mainloop()

print("The app was closed.")