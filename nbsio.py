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
from collections import deque
from operator import itemgetter
from typing import BinaryIO

from addict import Dict

BYTE = Struct('<b')
SHORT = Struct('<h')
SHORT_SIGNED = Struct('<H')
INT = Struct('<i')

NBS_VERSION = 5

def read_numeric(f: BinaryIO, fmt: Struct) -> int:
    '''Read the following bytes from file and return a number.'''

    raw = f.read(fmt.size)
    rawInt = int.from_bytes(raw, byteorder='little', signed=True)
    # print("{0:<2}{1:<20}{2:<10}{3:<11}".format(fmt.size, str(raw), raw.hex(), rawInt))
    return fmt.unpack(raw)[0]

def read_string(f: BinaryIO) -> str:
    '''Read the following bytes from file and return a ASCII string.'''

    length = read_numeric(f, INT)
    raw = f.read(length)
    # print("{0:<20}{1}".format(length, raw))
    return raw.decode('unicode_escape') # ONBS doesn't support UTF-8

def write_numeric(f: BinaryIO, fmt: Struct, v) -> None:
    f.write(fmt.pack(v))

def write_string(f: BinaryIO, v) -> None:
    write_numeric(f, INT, len(v))
    f.write(v.encode())

class NbsSong(Dict):
    def __init__(self, f=None):
        self.header = Dict({
            'file_version': 5,
            'vani_inst': 16,
            'length': 0,
            'length': 0,
            'height': 0,
            'name': '',
            'author': '',
            'orig_author': '',
            'description': '',
            'tempo': 10,
            'time_sign': 4,
            'minutes_spent': 0,
            'left_clicks': 0,
            'right_clicks': 0,
            'block_added': 0,
            'block_removed': 0,
            'import_name': '',
            'loop': False,
            'loop_max': 0,
            'loop_start': 0,
        })
        self.notes = deque()
        self.layers = deque()
        self.customInsts = []
        self.appendix = None
        if f: self.read(f)

    def __repr__(self):
        return "<NbsSong notes={}, layers={}, customInsts={}>".format(len(self.notes), len(self.layers), len(self.customInsts))

    def readHeader(self, f: BinaryIO) -> None:
        '''Read a .nbs file header from a file object'''

        header = Dict()
        header['length'] = None
        readNumeric = read_numeric
        readString = read_string

        #Header
        first = readNumeric(f, SHORT) #Sign
        if first != 0: #File is old type
            header['file_version'] = file_version = 0
            header['vani_inst'] = 10
            header['length'] = first
        else: #File is new type
            header['file_version'] = file_version = readNumeric(f, BYTE) #Version
            if file_version > NBS_VERSION:
                raise NotImplementedError("This format version ({}) is not supported.".format(file_version))
            header['vani_inst'] = readNumeric(f, BYTE)
        if file_version >= 3:
            header['length'] = readNumeric(f, SHORT)
        header['height'] = readNumeric(f, SHORT) #Height
        header['name'] = readString(f) #Name
        header['author'] = readString(f) #Author
        header['orig_author'] = readString(f) #OriginalAuthor
        header['description'] = readString(f) #Description
        header['tempo'] = readNumeric(f, SHORT)/100 #Tempo
        header['auto_save'] = readNumeric(f, BYTE) == 1 #auto_save enabled
        header['auto_save_time'] = readNumeric(f, BYTE) #auto_save duration
        header['time_sign'] = readNumeric(f, BYTE) #Time signature
        header['minutes_spent'] = readNumeric(f, INT) #Minutes spent
        header['left_clicks'] = readNumeric(f, INT) #Left clicks
        header['right_clicks'] = readNumeric(f, INT) #Right clicks
        header['block_added'] = readNumeric(f, INT) #Total block added
        header['block_removed'] = readNumeric(f, INT) #Total block removed
        header['import_name'] = readString(f) #MIDI file name
        if file_version >= 4:
            header['loop'] = readNumeric(f, BYTE) #Loop enabled
            header['loop_max'] =  readNumeric(f, BYTE) #Max loop count
            header['loop_start'] =  readNumeric(f, SHORT) #Loop start tick
        self.header = header

    def read(self, fn) -> None:
        '''Read a .nbs file from disk or URL.'''

        notes = deque()
        maxLayer = 0
        usedInsts = [[], []]
        hasPerc = False
        layers = deque()
        customInsts = []
        appendix = None
        readNumeric = read_numeric
        readString = read_string

        if fn != '':
            if fn.__class__.__name__ == 'HTTPResponse':
                f = fn
            else:
                f = open(fn, "rb")
            try:
                self.readHeader(f)
                header = self.header
                file_version = header.file_version
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
                            pitch = readNumeric(f, SHORT_SIGNED)
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
                        notes.append(Dict({'tick':tick, 'layer':layer, 'inst':inst, 'key':key, 'vel':vel, 'pan':pan, 'pitch':pitch, 'isPerc':isPerc}))
                    maxLayer = max(layer, maxLayer)
                # if header['length'] is None:
                header['length'] = tick + 1
                # indexByTick = tuple([ (tk, tuple([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(header['length']+1) ])
                #Layers
                for i in range(header['height']):
                    name = readString(f) #Layer name
                    if header['file_version'] >= 4:
                        lock = readNumeric(f, BYTE) == 1 #Lock
                    else:
                        lock = False
                    vol = readNumeric(f, BYTE) #Volume
                    vol = 100 if vol == -1 else vol
                    stereo = readNumeric(f, BYTE) if file_version >= 2 else 100 #Stereo
                    layers.append(Dict({'name':name, 'lock':lock, 'volume':vol, 'stereo':stereo}))
                name = vol = stereo = None
                #Custom instrument
                header['inst_count'] = readNumeric(f, BYTE)
                for i in range(header['inst_count']):
                    name = readString(f) #Instrument name
                    file = readString(f) #Sound fn
                    pitch = readNumeric(f, BYTE) #Pitch
                    shouldPressKeys = bool(readNumeric(f, BYTE)) #Press key
                    customInsts.append(Dict({'name':name, 'fn':file, 'pitch':pitch, 'pressKeys':shouldPressKeys}))
                #Rest of the file
                appendix = f.read()
            finally:
                try:
                    f.close()
                except:
                    pass
        self.notes, self.layers, self.customInsts, self.hasPerc, self.maxLayer, self.usedInsts = \
            notes, layers, customInsts, hasPerc, maxLayer, (tuple(usedInsts[0]), tuple(usedInsts[1]))
        if appendix: self.appendix = appendix

    def sortNotes(self) -> None:
        self.notes = sorted(self.notes, key=itemgetter('tick', 'layer', 'key', 'inst'))

    def correctData(self) -> None:
        '''Make song data consistent.'''

        self.sortNotes()
        notes = self.notes
        usedInsts = [[], []]
        maxLayer = 0
        self.hasPerc = False
        for i, note in enumerate(notes):
            tick, inst, layer = note['tick'], note['inst'], note['layer']
            if inst in {2, 3, 4}:
                self.hasPerc = note['isPerc'] = True
                if inst not in usedInsts[1]: usedInsts[1].append(inst)
            else:
                note['isPerc'] = False
                if inst not in usedInsts[0]: usedInsts[0].append(inst)
            maxLayer = max(layer, maxLayer)
        self['header']['length'] = tick
        self['maxLayer'] = maxLayer
        self['usedInsts'] = (tuple(usedInsts[0]), tuple(usedInsts[1]))
        # self['indexByTick'] = tuple([ (tk, set([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(header['length']+1) ])

    def write(self, fn: str) -> None:
        '''Save nbs data to a file on disk with the path given.'''

        if fn != '' and self.header and self.notes:
            writeNumeric = write_numeric
            writeString = write_string
            self.correctData()
            header, notes, layers, customInsts = \
            self['header'], self['notes'], self['layers'], self['customInsts']
            file_version = header['file_version']

            with open(fn, "wb") as f:
                #Header
                if file_version != 0:
                    writeNumeric(f, SHORT, 0)
                    writeNumeric(f, BYTE, file_version) #Version
                    writeNumeric(f, BYTE, header.get('vani_inst', 10))
                if (file_version == 0) or (file_version >= 3):
                    writeNumeric(f, SHORT, header['length']) #Length
                writeNumeric(f, SHORT, header['height']) #Height
                writeString(f, header['name']) #Name
                writeString(f, header['author']) #Author
                writeString(f, header['orig_author']) #OriginalAuthor
                writeString(f, header['description']) #Description
                writeNumeric(f, SHORT, int(header['tempo']*100)) #Tempo
                writeNumeric(f, BYTE, header['auto_save']) #auto_save enabled
                writeNumeric(f, BYTE, header['auto_save_time']) #auto_save duration
                writeNumeric(f, BYTE, header['time_sign']) #Time signature
                writeNumeric(f, INT, header['minutes_spent']) #Minutes spent
                writeNumeric(f, INT, header['left_clicks']) #Left clicks
                writeNumeric(f, INT, header['right_clicks']) #Right clicks
                writeNumeric(f, INT, header['block_added']) #Total block added
                writeNumeric(f, INT, header['block_removed']) #Total block removed
                writeString(f, header['import_name']) #MIDI file name
                if file_version >= 4:
                    writeNumeric(f, BYTE, header.get('loop', False)) #Loop enabled
                    writeNumeric(f, BYTE, header.get('loop_max', 0)) #Max loop count
                    writeNumeric(f, SHORT, header.get('loop_start', 0)) #Loop start tick
                #Notes
                tick = layer = -1
                fstNote = notes[0]
                for note in notes:
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
                            writeNumeric(f, BYTE, note.get('vel', 100))
                            writeNumeric(f, BYTE, note.get('pan', 100))
                            writeNumeric(f, SHORT_SIGNED, note.get('pitch', 0))
                # writeNumeric(f, SHORT, 0)
                # writeNumeric(f, SHORT, 0)
                writeNumeric(f, INT, 0)
                #Layers
                for layer in layers:
                    writeString(f, layer['name']) #Layer name
                    if file_version >= 4:
                        writeNumeric(f, BYTE, layer.get('lock', False)) #Lock
                    writeNumeric(f, BYTE, layer['volume']) #Volume
                    if file_version >= 2:
                        writeNumeric(f, BYTE, layer.get('stereo', 100)) #Stereo
                #Custom instrument
                if len(customInsts) == 0: writeNumeric(f, BYTE, 0)
                else:
                    writeNumeric(f, BYTE, len(customInsts))
                    if len(customInsts) > 0:
                        for customInst in customInsts:
                            writeString(f, customInst['name']) #Instrument name
                            writeString(f, customInst['fn']) #Sound fn
                            writeNumeric(f, BYTE, customInst['pitch']) #Pitch
                            writeNumeric(f, BYTE, customInst['pressKeys']) #Press key
                #Appendix
                if self.appendix: f.write(self.appendix)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if len(sys.argv) == 2: in_ra = True
        else: in_ra = sys.argv[2]
        data = NbsSong(sys.argv[1])
        if in_ra: pprint(data)