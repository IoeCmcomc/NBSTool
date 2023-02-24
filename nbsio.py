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


import traceback
import warnings
from dataclasses import dataclass
from functools import total_ordering
from pprint import pprint
from struct import Struct
from typing import BinaryIO, List, Tuple
from warnings import warn

BYTE = Struct('<B')
SHORT = Struct('<H')
SHORT_SIGNED = Struct('<h')
INT = Struct('<I')

NBS_VERSION = 5
PERC_INSTS = {2, 3, 4}

warnings.filterwarnings(action='once')


def read_numeric(f: BinaryIO, fmt: Struct) -> int:
    '''Read the following bytes from file and return a number.'''

    raw = f.read(fmt.size)
    # rawInt = int.from_bytes(raw, byteorder='little', signed=True)
    # print("{0:<2}{1:<20}{2:<10}{3:<11}".format(fmt.size, str(raw), raw.hex(), rawInt))
    return fmt.unpack(raw)[0]


def read_string(f: BinaryIO) -> str:
    '''Read the following bytes from file and return a ASCII string.'''

    length = read_numeric(f, INT)
    raw = f.read(length)
    # print("{0:<20}{1}".format(length, raw))
    return raw.decode('unicode_escape')  # ONBS doesn't support UTF-8


def write_numeric(f: BinaryIO, fmt: Struct, v) -> None:
    f.write(fmt.pack(v))


def write_string(f: BinaryIO, v) -> None:
    if not v.isascii():
        previewStr = v.encode("ascii", "replace")
        warn(f"The string '{v}' will be written to file as '{previewStr}'.")
        v = v.encode("ascii", "replace")
    else:
        v = v.encode()
    write_numeric(f, INT, len(v))
    f.write(v)


@total_ordering
@dataclass
class Note:
    tick: int = -1
    layer: int = -1
    inst: int = -1
    key: int = -1
    vel: int = 100
    pan: int = 0 # from -100 to 100 (saved as 0 to 200)
    pitch: int = 0

    @property
    def isPerc(self):
        return self.inst in PERC_INSTS

    def __eq__(self, other) -> bool:
        if isinstance(other, Note):
            return (self.tick, self.layer, self.key, self.inst) \
                == (other.tick, other.layer, other.key, other.inst)
        
        return False

    def __lt__(self, other) -> bool:
        return (self.tick, self.layer, self.key, self.inst) \
                < (other.tick, other.layer, other.key, other.inst)


@dataclass
class Header:
    file_version = NBS_VERSION
    vani_inst = 16
    length = 0
    height = 0
    name = ''
    author = ''
    orig_author = ''
    description = ''
    auto_save = True
    auto_save_time = 10
    tempo = 10.0  # 10 TPS
    time_sign = 4
    minutes_spent = 0
    left_clicks = 0
    right_clicks = 0
    block_added = 0
    block_removed = 0
    import_name = ''
    loop = False
    loop_max = 0
    loop_start = 0


@dataclass
class Layer:
    name: str
    lock: bool = False
    volume: int = 100
    pan: int = 0 # same as Note.pan
    # solo: bool = False


@dataclass
class Instrument:
    name: str
    filePath: str
    pitch: int
    pressKeys: bool
    sound_id: str = ''

VANILLA_INSTS = [
    Instrument("Harp", 'harp.ogg', 0, True, 'harp'),
    Instrument("Double Bass", 'dbass.ogg', 0, False, 'bass'),
    Instrument("Bass Drum", 'bdrum.ogg', 0, False, 'basedrum'),
    Instrument("Snare Drum", 'sdrum.ogg', 0, False, 'snare'),
    Instrument("Click", 'click.ogg', 0, False, 'hat'),
    Instrument("Guitar", 'guitar.ogg', 0, False, 'guitar'),
    Instrument("Flute", 'flute.ogg', 0, False, 'flute'),
    Instrument("Bell", 'bell.ogg', 0, False, 'bell'),
    Instrument("Chime", 'icechime.ogg', 0, False, 'chime'),
    Instrument("Xylophone", 'xylobone.ogg', 0, False, 'xylophone'),
    Instrument("Iron Xylophone", 'iron_xylophone.ogg', 0, False, 'iron_xylophone'),
    Instrument("Cow Bell", 'cow_bell.ogg', 0, False, 'cow_bell'),
    Instrument("Didgeridoo", 'didgeridoo.ogg', 0, False, 'didgeridoo'),
    Instrument("Bit", 'bit.ogg', 0, False, 'bit'),
    Instrument("Banjo", 'banjo.ogg', 0, False, 'banjo'),
    Instrument("Pling", 'pling.ogg', 0, False, 'pling'),
]


class NbsSong:
    def __init__(self, f=None):
        self.header = Header()
        self.notes: List[Note] = []
        self.layers: List[Layer] = []
        self.customInsts: List[Instrument] = []
        self.appendix = None
        self.hasPerc = False
        self.maxLayer = 0
        self.usedInsts: Tuple[Tuple[Instrument], Tuple[Instrument]]

        if f:
            self.read(f)

    def __len__(self) -> int:
        return self.header.length

    def __repr__(self):
        return f"<NbsSong notes={len(self.notes)}, layers={len(self.layers)}, customInsts={len(self.customInsts)}>"

    def readHeader(self, f: BinaryIO) -> None:
        '''Read a .nbs file header from a file object'''

        header = self.header
        header.length = -1
        readNumeric = read_numeric
        readString = read_string

        # Header
        first = readNumeric(f, SHORT)  # Sign
        if first != 0:  # File is old type
            header.file_version = file_version = 0
            header.vani_inst = 10
            header.length = first
        else:  # File is new type
            header.file_version = file_version = readNumeric(
                f, BYTE)  # Version
            if file_version > NBS_VERSION:
                raise NotImplementedError(
                    f"This format version ({file_version}) is not supported.")
            header.vani_inst = readNumeric(f, BYTE)
        if file_version >= 3:
            header.length = readNumeric(f, SHORT)
        header.height = readNumeric(f, SHORT)  # Height
        header.name = readString(f)  # Name
        header.author = readString(f)  # Author
        header.orig_author = readString(f)  # OriginalAuthor
        header.description = readString(f)  # Description
        header.tempo = readNumeric(f, SHORT)/100  # Tempo
        header.auto_save = readNumeric(f, BYTE) == 1  # auto_save enabled
        header.auto_save_time = readNumeric(f, BYTE)  # auto_save duration
        header.time_sign = readNumeric(f, BYTE)  # Time signature
        header.minutes_spent = readNumeric(f, INT)  # Minutes spent
        header.left_clicks = readNumeric(f, INT)  # Left clicks
        header.right_clicks = readNumeric(f, INT)  # Right clicks
        header.block_added = readNumeric(f, INT)  # Total block added
        header.block_removed = readNumeric(f, INT)  # Total block removed
        header.import_name = readString(f)  # MIDI file name
        if file_version >= 4:
            header.loop = readNumeric(f, BYTE) == 1  # Loop enabled
            header.loop_max = readNumeric(f, BYTE)  # Max loop count
            header.loop_start = readNumeric(f, SHORT)  # Loop start tick
        # self.header = header

    def read(self, fn) -> None:
        '''Read a .nbs file from disk or URL.'''

        notes = []
        maxLayer = 0
        usedInsts = [[], []]
        hasPerc = False
        layers = []
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
                # Notes
                tick = -1
                tickJumps = layerJumps = 0
                while True:
                    tickJumps = readNumeric(f, SHORT)
                    if tickJumps == 0:
                        break
                    tick += tickJumps
                    layer = -1
                    while True:
                        layerJumps = readNumeric(f, SHORT)
                        if layerJumps == 0:
                            break
                        layer += layerJumps
                        inst = readNumeric(f, BYTE)
                        key = readNumeric(f, BYTE)  # +21
                        if file_version >= 4:
                            vel = readNumeric(f, BYTE)
                            pan = readNumeric(f, BYTE) - 100
                            pitch = readNumeric(f, SHORT_SIGNED)
                        else:
                            vel = 100
                            pan = 0
                            pitch = 0
                        if inst in PERC_INSTS:
                            if inst not in usedInsts[1]:
                                usedInsts[1].append(inst)
                        else:
                            if inst not in usedInsts[0]:
                                usedInsts[0].append(inst)
                        notes.append(
                            Note(tick, layer, inst, key, vel, pan, pitch))
                    maxLayer = max(layer, maxLayer)
                # if header['length'] is None:
                header.length = tick + 1
                # indexByTick = tuple([ (tk, tuple([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(header['length']+1) ])
                # Layers
                for _ in range(header.height):
                    name = readString(f)  # Layer name
                    if header.file_version >= 4:
                        lock = readNumeric(f, BYTE) == 1  # Lock
                    else:
                        lock = False
                    vol = readNumeric(f, BYTE)  # Volume
                    vol = 100 if vol == -1 else vol
                    stereo = (readNumeric(f, BYTE) - 100) if file_version >= 2 else 0  # Stereo
                    layers.append(Layer(name, lock, vol, stereo))
                name = vol = stereo = None
                # Custom instrument
                inst_count = readNumeric(f, BYTE)
                for i in range(inst_count):
                    name = readString(f)  # Instrument name
                    filePath = readString(f)  # Sound file path
                    pitch = readNumeric(f, BYTE)  # Pitch
                    shouldPressKeys = bool(readNumeric(f, BYTE))  # Press key
                    customInsts.append(Instrument(
                        name, filePath, pitch, shouldPressKeys))
                # Rest of the file
                appendix = f.read()
            finally:
                try:
                    f.close()
                except:
                    print(traceback.format_exc())
        self.notes, self.layers, self.customInsts, self.hasPerc, self.maxLayer, self.usedInsts = \
            notes, layers, customInsts, hasPerc, maxLayer, (tuple(
                usedInsts[0]), tuple(usedInsts[1]))
        if appendix:
            self.appendix = appendix

    def sortNotes(self) -> None:
        self.notes = sorted(self.notes)

    def correctData(self) -> None:
        '''Make song data consistent.'''

        self.sortNotes()
        notes = self.notes
        header = self.header
        usedInsts = [[], []]
        maxLayer = 0
        maxInst = 0
        tick = -1
        self.hasPerc = False
        for note in notes:
            tick, inst, layer = note.tick, note.inst, note.layer
            maxInst = max(maxInst, inst)
            if inst in PERC_INSTS:
                if inst not in usedInsts[1]:
                    usedInsts[1].append(inst)
            else:
                if inst not in usedInsts[0]:
                    usedInsts[0].append(inst)
            maxLayer = max(layer, maxLayer)

        header.length = tick
        header.height = len(self.layers)
        header.vani_inst = 16 if header.file_version > 0 else 10
        self.maxLayer = maxLayer
        self.usedInsts = (tuple(usedInsts[0]), tuple(usedInsts[1]))
        # self['indexByTick'] = tuple([ (tk, set([notes.index(nt) for nt in notes if nt['tick'] == tk]) ) for tk in range(header['length']+1) ])

    def downgradeToClassic(self):
        for note in self.notes:
            if 10 <= note.inst <= 15:
                note.inst = 0  # Change newer instrument to harp
            elif note.inst > 15:
                note.inst -= 6  # Update custom instrument index

    def write(self, fn: str) -> None:
        '''Save nbs data to a file on disk with the given path.'''

        if not fn.endswith('.nbs'):
            fn += '.nbs'

        if fn != '' and self.header and self.notes:
            writeNumeric = write_numeric
            writeString = write_string
            self.correctData()
            header, notes, layers, customInsts = \
                self.header, self.notes, self.layers, self.customInsts
            file_version = header.file_version

            with open(fn, "wb") as f:
                # Header
                if file_version != 0:
                    writeNumeric(f, SHORT, 0)
                    writeNumeric(f, BYTE, file_version)  # Version
                    writeNumeric(f, BYTE, getattr(header, 'vani_inst', 10))
                if (file_version == 0) or (file_version >= 3):
                    writeNumeric(f, SHORT, header.length)  # Length
                writeNumeric(f, SHORT, header.height)  # Height
                writeString(f, header.name)  # Name
                writeString(f, header.author)  # Author
                writeString(f, header.orig_author)  # OriginalAuthor
                writeString(f, header.description)  # Description
                writeNumeric(f, SHORT, int(header.tempo*100))  # Tempo
                writeNumeric(f, BYTE, header.auto_save)  # auto_save enabled
                # auto_save duration
                writeNumeric(f, BYTE, header.auto_save_time)
                writeNumeric(f, BYTE, header.time_sign)  # Time signature
                writeNumeric(f, INT, header.minutes_spent)  # Minutes spent
                writeNumeric(f, INT, header.left_clicks)  # Left clicks
                writeNumeric(f, INT, header.right_clicks)  # Right clicks
                writeNumeric(f, INT, header.block_added)  # Total block added
                # Total block removed
                writeNumeric(f, INT, header.block_removed)
                writeString(f, header.import_name)  # Import file name
                if file_version >= 4:
                    writeNumeric(f, BYTE, getattr(
                        header, 'loop', False))  # Loop enabled
                    writeNumeric(f, BYTE, getattr(
                        header, 'loop_max', 0))  # Max loop count
                    writeNumeric(f, SHORT, getattr(
                        header, 'loop_start', 0))  # Loop start tick
                # Notes
                tick = layer = -1
                fstNote = notes[0]
                for note in notes:
                    if tick != note.tick:
                        if note != fstNote:
                            writeNumeric(f, SHORT, 0)
                            layer = -1
                        writeNumeric(f, SHORT, note.tick - tick)
                        tick = note.tick
                    if layer != note.layer:
                        writeNumeric(f, SHORT, note.layer - layer)
                        layer = note.layer
                        writeNumeric(f, BYTE, note.inst)
                        writeNumeric(f, BYTE, note.key)  # -21
                        if file_version >= 4:
                            writeNumeric(f, BYTE, note.vel)
                            writeNumeric(f, BYTE, note.pan + 100)
                            writeNumeric(f, SHORT_SIGNED, note.pitch)
                # writeNumeric(f, SHORT, 0)
                # writeNumeric(f, SHORT, 0)
                writeNumeric(f, INT, 0)
                # Layers
                for layer in layers:
                    writeString(f, layer.name)  # Layer name
                    if file_version >= 4:
                        writeNumeric(f, BYTE, layer.lock)  # Lock
                    writeNumeric(f, BYTE, layer.volume)  # Volume
                    if file_version >= 2:
                        writeNumeric(f, BYTE, layer.pan + 100)  # Panning
                # Custom instrument
                if len(customInsts) == 0:
                    writeNumeric(f, BYTE, 0)
                else:
                    writeNumeric(f, BYTE, len(customInsts))
                    if len(customInsts) > 0:
                        for customInst in customInsts:
                            # Instrument name
                            writeString(f, customInst.name)
                            # Sound file path
                            writeString(f, customInst.filePath)
                            writeNumeric(f, BYTE, customInst.pitch)  # Pitch
                            # Press key
                            writeNumeric(f, BYTE, customInst.pressKeys)
                # Appendix
                if self.appendix:
                    f.write(self.appendix)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            in_ra = True
        else:
            in_ra = sys.argv[2]
        data = NbsSong(sys.argv[1])
        if in_ra:
            pprint(data)
