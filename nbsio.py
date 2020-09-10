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
# Version: 0,7.0
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


from struct import Struct
from pprint import pprint
# from random import shuffle
from collections import deque
from operator import itemgetter

BYTE = Struct('<b')
SHORT = Struct('<h')
INT = Struct('<i')

VERSION = 4

def read_numeric(f, fmt):
    raw = f.read(fmt.size)
    # print("{0:<2}{1:<20}{2:<10}{3:<11}".format(fmt.size, str(raw), raw.hex(), int(raw.hex(), 16)))
    return fmt.unpack(raw)[0]

def readString(f):
    length = read_numeric(f, INT)
    raw = f.read(length)
    # print("{0:<20}{1}".format(length, raw))
    return raw.decode('unicode_escape') # ONBS doesn't support UTF-8

def readnbsheader(f):
    headers = {}
    headers['length'] = None
    readNumeric = read_numeric
    
    #Header
    first = readNumeric(f, SHORT) #Sign
    if first != 0: #File is old type
        headers['file_version'] = 0
        headers['vani_inst'] = 10
        headers['length'] = first
    else: #File is new type
        headers['file_version'] = readNumeric(f, BYTE) #Version
        headers['vani_inst'] = readNumeric(f, BYTE)
    if headers['file_version'] >= 3:
        headers['length'] = readNumeric(f, SHORT)
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
    if headers['file_version'] >= 4:
        headers['loop'] = readNumeric(f, BYTE) #Loop enabled
        headers['loop_max'] =  readNumeric(f, BYTE) #Max loop count
        headers['loop_start'] =  readNumeric(f, SHORT) #Loop start tick
    return headers

def readnbs(fn):
    notes = deque()
    maxLayer = 0
    usedInsts = [[], []]
    hasPerc = False
    layers = deque()
    customInsts = deque()
    appendix = None
    readNumeric = read_numeric
    
    if fn != '':
        if fn.__class__.__name__ == 'HTTPResponse':
            f = fn
        else:
            f = open(fn, "rb")
        try:
            headers = readnbsheader(f)
            file_version = headers['file_version']
            #Notes
            tick = -1
            tickJumps = layerJumps = 0
            while True:
                tickJumps = readNumeric(f, SHORT)
                if tickJumps == 0: break
                tick += tickJumps
                layer = -1
                while True:
                    layerJumps = readNumeric(f, SHORT)
                    if layerJumps == 0: break
                    layer += layerJumps
                    inst = readNumeric(f, BYTE)
                    key = readNumeric(f, BYTE)#+21
                    if file_version >= 4:
                        vel = readNumeric(f, BYTE)
                        pan = readNumeric(f, BYTE)
                        pitch = readNumeric(f, SHORT)
                    else:
                        vel = 100
                        pan = 100
                        pitch = 0
            
                    if inst in {2, 3, 4}:
                        hasPerc = isPerc = True
                        if inst not in usedInsts[1]: usedInsts[1].append(inst)
                    else:
                        isPerc = False
                        if inst not in usedInsts[0]: usedInsts[0].append(inst)
                    notes.append({'tick':tick, 'layer':layer, 'inst':inst, 'key':key, 'vel':vel, 'pan':pan, 'pitch':pitch, 'isPerc':isPerc})
                maxLayer = max(layer, maxLayer)
            if headers['length'] is None: headers['length'] = tick + 1
            # indexByTick = tuple([ (tk, tuple([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(headers['length']+1) ])
            #Layers
            for i in range(headers['height']):
                name = readString(f) #Layer name
                if headers['file_version'] >= 4:
                    lock = readNumeric(f, BYTE) == 1 #Lock
                else:
                    lock = False
                vol = readNumeric(f, BYTE) #Volume
                vol = 100 if vol == -1 else vol
                stereo = readNumeric(f, BYTE) if file_version >= 2 else 100 #Stereo
                layers.append({'name':name, 'lock':lock, 'volume':vol, 'stereo':stereo})
            name = vol = stereo = None
            #Custom instrument
            headers['inst_count'] = readNumeric(f, BYTE)
            for i in range(headers['inst_count']):
                name = readString(f) #Instrument name
                file = readString(f) #Sound fn
                pitch = readNumeric(f, BYTE) #Pitch
                shouldPressKeys = bool(readNumeric(f, BYTE)) #Press key
                customInsts.append({'name':name, 'fn':file, 'pitch':pitch, 'pressKeys':shouldPressKeys})
            #Rest of the file
                appendix = f.read()
        finally:
            try:
                f.close()
            except:
                pass
    data = {'headers':headers, 'notes':notes, 'layers':layers, 'customInsts':customInsts, 'hasPerc':hasPerc, 'maxLayer':maxLayer, 'usedInsts':(tuple(usedInsts[0]), tuple(usedInsts[1])), }
    if appendix: data['appendix'] = appendix
    return data
    
def DataPostprocess(data):
    # headers = data['headers']
    notes = data['notes']
    usedInsts = [[], []]
    maxLayer = 0
    data['hasPerc'] = False
    for i, note in enumerate(notes):
        tick, inst, layer = note['tick'], note['inst'], note['layer']
        if inst in {2, 3, 4}:
            data['hasPerc'] = note['isPerc'] = True
            if inst not in usedInsts[1]: usedInsts[1].append(inst)
        else:
            note['isPerc'] = False
            if inst not in usedInsts[0]: usedInsts[0].append(inst)
        maxLayer = max(layer, maxLayer)
    data['headers']['length'] = tick
    data['maxLayer'] = maxLayer
    data['usedInsts'] = (tuple(usedInsts[0]), tuple(usedInsts[1]))
    # data['indexByTick'] = tuple([ (tk, set([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(headers['length']+1) ])
    return data

def writeNumeric(f, fmt, v):
    f.write(fmt.pack(v))

def writeString(f, v):
    writeNumeric(f, INT, len(v))
    f.write(v.encode())
    
def writenbs(fn, data):
    if fn != '' and data is not None:
        data = DataPostprocess(data)
        headers, notes, layers, customInsts = \
        data['headers'], data['notes'], data['layers'], data['customInsts']
        file_version = headers['file_version']
        with open(fn, "wb") as f:
            #Header
            if file_version != 0:
                writeNumeric(f, SHORT, 0)
                writeNumeric(f, BYTE, file_version) #Version
                writeNumeric(f, BYTE, headers['vani_inst'])
            if (file_version == 0) or (file_version >= 3):
                writeNumeric(f, SHORT, headers['length']) #Length
            writeNumeric(f, SHORT, headers['height']) #Height
            writeString(f, headers['name']) #Name
            writeString(f, headers['author']) #Author
            writeString(f, headers['orig_author']) #OriginalAuthor
            writeString(f, headers['description']) #Description 
            writeNumeric(f, SHORT, int(headers['tempo']*100)) #Tempo
            writeNumeric(f, BYTE, headers['auto-saving']) #Auto-saving enabled
            writeNumeric(f, BYTE, headers['auto-saving_time']) #Auto-saving duration
            writeNumeric(f, BYTE, headers['time_sign']) #Time signature
            writeNumeric(f, INT, headers['minutes_spent']) #Minutes spent
            writeNumeric(f, INT, headers['left_clicks']) #Left clicks
            writeNumeric(f, INT, headers['right_clicks']) #Right clicks
            writeNumeric(f, INT, headers['block_added']) #Total block added
            writeNumeric(f, INT, headers['block_removed']) #Total block removed
            writeString(f, headers['import_name']) #MIDI file name
            if file_version >= 4:
                writeNumeric(f, BYTE, headers['loop']) #Loop enabled
                writeNumeric(f, BYTE, headers['loop_max']) #Max loop count
                writeNumeric(f, SHORT, headers['loop_start']) #Loop start tick
            #Notes
            # shuffle(notes)
            sortedNotes = sorted(notes, key = itemgetter('tick', 'layer') )
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
                    if file_version >= 4:
                        writeNumeric(f, BYTE, note['vel'])
                        writeNumeric(f, BYTE, note['pan'])
                        writeNumeric(f, SHORT, note['pitch'])
            writeNumeric(f, SHORT, 0)
            writeNumeric(f, SHORT, 0)
            #Layers
            for layer in layers:
                writeString(f, layer['name']) #Layer name
                if file_version >= 4:
                    writeNumeric(f, BYTE, layer['lock']) #Lock
                writeNumeric(f, BYTE, layer['volume']) #Volume
                if file_version >= 2:
                    writeNumeric(f, BYTE, layer['stereo']) #Stereo
            #Custom instrument
            pprint(customInsts)
            if len(customInsts) == 0: writeNumeric(f, BYTE, 0)
            else:
                writeNumeric(f, BYTE, len(customInsts))
                if len(customInsts) > 0:
                    for customInst in customInsts:
                        writeString(f, customInst['name']) #Instrument name
                        writeString(f, customInst['fn']) #Sound fn
                        writeNumeric(f, BYTE, customInst['pitch']) #Pitch
                        writeNumeric(f, BYTE, customInst['pressKeys']) #Press key

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2: in_ra = True
    else: in_ra = sys.argv[2]
    data = readnbs(sys.argv[1])
    if in_ra: pprint(data)