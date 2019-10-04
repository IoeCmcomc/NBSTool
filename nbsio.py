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
# Version: 0,50
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


from struct import Struct
from pprint import pprint
from random import shuffle
import operator

BYTE = Struct('<b')
SHORT = Struct('<h')
INT = Struct('<i')

def readNumeric(f, fmt):
	return fmt.unpack(f.read(fmt.size))[0]

def readString(f):
	length = readNumeric(f, INT)
	return f.read(length).decode()

def readnbs(filename, cls=None):
	IsOldVersion = False
	headers = {}
	notes = []
	maxLayer = 0
	usedInsts = [[], []]
	hasPerc = False
	layers = []
	customInsts = []

	if filename is not '':
		with open(filename, "rb") as f:
			#Header
			if cls: cls.UpdateProgBar(25)
			sign = readNumeric(f, SHORT) == 0 #Sign
			if not sign:
				IsOldVersion = True
				headers['file_version'] = headers['vani_inst'] = -999
				f.seek(0, 0)
			else:
				headers['file_version'] = readNumeric(f, BYTE) #Version
				headers['vani_inst'] = readNumeric(f, BYTE)
			if IsOldVersion or headers['file_version'] >= 3:
				headers['length'] = readNumeric(f, SHORT)
			else:
				headers['length'] = None
			headers['height'] = readNumeric(f, SHORT) #Height
			headers['name'] = readString(f) #Name
			headers['author'] = readString(f) #Author
			headers['orig_author'] = readString(f) #OriginalAuthor
			headers['description'] = readString(f) #Description 
			headers['tempo'] = readNumeric(f, SHORT)/100 #Tempo
			headers['auto-saving'] = readNumeric(f, BYTE) == 1 #Auto-saving enabled
			headers['auto-saving_time'] = readNumeric(f, BYTE) #Auto-saving duration
			headers['time_sign'] = readNumeric(f, BYTE) #Time signature
			headers['minutes_spent'] = readNumeric(f, INT) #Minutes spent
			headers['left_clicks'] = readNumeric(f, INT) #Left clicks
			headers['right_clicks'] = readNumeric(f, INT) #Right clicks
			headers['block_added'] = readNumeric(f, INT) #Total block added
			headers['block_removed'] = readNumeric(f, INT) #Total block removed
			headers['import_name'] = readString(f) #MIDI file name
			#Notes
			tick = -1
			tickJumps = layerJumps = 0
			while True:
				tickJumps = readNumeric(f, SHORT)
				#if notes: notes[-1]['duration'] = tickJumps
				if tickJumps == 0: break
				tick += tickJumps
				layer = -1
				if 'length' in headers and cls: cls.UpdateProgBar(25 + (tick / headers['length'] * 50))
				while True:
					layerJumps = readNumeric(f, SHORT)
					if layerJumps == 0: break
					layer += layerJumps
					inst = readNumeric(f, BYTE)
					key = readNumeric(f, BYTE)#+21
					if inst in (2, 3, 4):
						hasPerc = isPerc = True
						if inst not in usedInsts[1]: usedInsts[1].append(inst)
					else:
						isPerc = False
						if inst not in usedInsts[0]: usedInsts[0].append(inst)
					duraKey = None
					for idx, note in enumerate(notes):
						if note['layer'] == layer: duraKey = idx
					if duraKey is not None:
						if notes: notes[duraKey]['duration'] = tick - notes[duraKey]['tick']
					notes.append({'tick':tick, 'layer':layer, 'inst':inst, 'key':key, 'isPerc':isPerc, 'duration':8})
				maxLayer = max(layer, maxLayer)
			if headers['length'] is None: headers['length'] = tick + 1
			tick = tickJumps = layerJumps = layer = inst = key = duraKey = isPerc = None
			#Layers
			if cls: cls.UpdateProgBar(80)
			for i in range(headers['height']):
				name = readString(f) #Layer name
				vol = readNumeric(f, BYTE) #Volume
				if sign:
					stereo = readNumeric(f, BYTE) #Stereo
				else:
					stereo = None
				layers.append({'index':i, 'name':name, 'volume':vol, 'stereo':stereo})
			name = vol = stereo = None
			#Custom instrument
			if cls: cls.UpdateProgBar(85)
			headers['inst_count'] = readNumeric(f, BYTE)
			for i in range(headers['inst_count']):
				name = readString(f) #Instrument name
				file = readString(f) #Sound filename
				pitch = readNumeric(f, BYTE) #Pitch
				shouldPressKeys = bool(readNumeric(f, BYTE)) #Press key
				customInsts.append({'name':name, 'filename':file, 'pitch':pitch, 'pressKeys':shouldPressKeys})
	sortedNotes = sorted(notes, key = operator.itemgetter('tick', 'layer') )
	data = {'headers':headers, 'notes':sortedNotes, 'layers':layers, 'customInsts':customInsts, 'IsOldVersion':IsOldVersion, 'hasPerc':hasPerc, 'maxLayer':maxLayer, 'usedInsts':usedInsts}
	return data

def opennbs(filename, printOutput=False, cls=None):
	data = readnbs(filename, cls)
	if printOutput: pprint(data)
	return data
	

def writeNumeric(f, fmt, v):
	f.write(fmt.pack(v))

def writeString(f, v):
	writeNumeric(f, INT, len(v))
	f.write(v.encode())
	
def writenbs(filename, data):
	if filename is not '' and data is not None:
		headers, notes, layers, customInsts, IsOldVersion, hasPerc, maxLayer, usedInsts = \
		data['headers'], data['notes'], data['layers'], data['customInsts'], data['IsOldVersion'], data['hasPerc'], data['maxLayer'], data['usedInsts']
		with open(filename+'_saved.nbs', "wb") as f:
			#Header
			if not IsOldVersion:
				writeNumeric(f, SHORT, 0)
				writeNumeric(f, BYTE, headers['file_version']) #Version
				writeNumeric(f, BYTE, headers['vani_inst'])
			if IsOldVersion or headers['file_version'] >= 3:
				writeNumeric(f, SHORT, headers['length']) #Length
			writeNumeric(f, SHORT, headers['height']) #Height
			writeString(f, headers['name']) #Name
			writeString(f, headers['author']) #Author
			writeString(f, headers['orig_author']) #OriginalAuthor
			writeString(f, headers['description']) #Description 
			writeNumeric(f, SHORT, headers['tempo']*100) #Tempo
			writeNumeric(f, BYTE, headers['auto-saving']) #Auto-saving enabled
			writeNumeric(f, BYTE, headers['auto-saving_time']) #Auto-saving duration
			writeNumeric(f, BYTE, headers['time_sign']) #Time signature
			writeNumeric(f, INT, headers['minutes_spent']) #Minutes spent
			writeNumeric(f, INT, headers['left_clicks']) #Left clicks
			writeNumeric(f, INT, headers['right_clicks']) #Right clicks
			writeNumeric(f, INT, headers['block_added']) #Total block added
			writeNumeric(f, INT, headers['block_removed']) #Total block removed
			writeString(f, headers['import_name']) #MIDI file name
			#Notes
			shuffle(notes)
			sortedNotes = sorted(notes, key = operator.itemgetter('tick', 'layer') )
			#pprint(sortedNotes)
			tick = layer = -1
			fstNote = sortedNotes[0]
			for note in sortedNotes:
				if tick != note['tick']:
					if note != fstNote:
						writeNumeric(f, SHORT, 0)
						layer = -1
					writeNumeric(f, SHORT, note['tick'] - tick)
					tick = note['tick']
				if layer != note['layer']:
					writeNumeric(f, SHORT, note['layer'] - layer)
					layer = note['layer']
					writeNumeric(f, BYTE, note['inst'])
					writeNumeric(f, BYTE, note['key'])#-21
			writeNumeric(f, SHORT, 0)
			writeNumeric(f, SHORT, 0)
			#Layers
			for layer in layers:
				writeString(f, layer['name']) #Layer name
				writeNumeric(f, BYTE, layer['volume']) #Volume
				if not IsOldVersion:
					writeNumeric(f, BYTE, layer['stereo']) #Stereo
			#Custom instrument
			writeNumeric(f, BYTE, len(customInsts))
			if len(customInsts) > 0:
				for customInst in customInsts:
					writeString(f, customInst['name']) #Instrument name
					writeString(f, customInst['filepath']) #Sound filename
					writeNumeric(f, BYTE, customInst['pitch']) #Pitch
					writeNumeric(f, BYTE, customInst['pressKeys']) #Press key

if __name__ == "__main__":
	import sys
	opennbs(sys.argv[1], sys.argv[2])