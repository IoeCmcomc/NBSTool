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


from asyncio import sleep
from numpy import interp

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from nbsio import NbsSong
from common import MIDI_DRUMS, MIDI_INSTRUMENTS, NBS_PITCH_IN_MIDI_PITCHBEND

MIDI_DRUMS_BY_NBS_KEY_INST = {
    (obj.nbs_pitch, obj.nbs_instrument): obj.pitch for obj in MIDI_DRUMS}

INST_PROGRAMS = {
    0: 1, # Harp: Piano
    1: 32, # Double bass: Acoustic bass
    5: 28, # Guitar: Acoustic guitar (steel)
    6: 73, # Flute: Flute
    7: 10, # Bell: Music box
    8: 112, # Chime: Tinkle bell (wind chime)
    9: 13, # Xylophone: Xylophone
    10: 11, # Iron Xylophone: Vibraphone
    11: 12, # Cow Bell: Marimba
    12: 43, # Didgeridoo: Contrabass
    13: 80, # Bit: Lead 1 (square)
    14: 105, # Banjo: Banjo
    15: 16, # Pling: Drawbar organ
}

INST2PITCH = {
    2: 36,
    3: 44,
    4: 81,
}

def firstInstInLayer(nbs: NbsSong, layer: int) -> int:
    '''It returns the instrument of the first note in a layer
    
    Parameters
    ----------
    nbs : NbsSong
        The NBS file to be converted.
    layer : int
        The layer to check for the first instrument.
    
    Returns
    -------
        The instrument of the first note in the layer.
    
    '''
    if layer > nbs.maxLayer:
        return 0
    for note in nbs.notes:
        if note.layer == layer:
            return note.inst
    return 0

class MsgComparator:
    def __init__(self, msg: Message) -> None:
        self.msg = msg

    def __lt__(self, other: 'MsgComparator') -> bool:
        if (not self.msg.is_meta) and other.msg.is_meta:
            return self.msg.time < other.msg.time # type: ignore
        else:
            return False

def absTrack2DeltaTrack(track) -> MidiTrack:
    '''It takes a track of absolute time messages and returns a track of delta
    time messages'''
    track.sort(key=MsgComparator)
    ret = MidiTrack()
    ret.append(track[0])
    for i in range(1, len(track)):
        msg = track[i]
        # print(msg.time - track[i-1].time)
        ret.append(msg.copy(time=msg.time - track[i-1].time))
    return ret


async def nbs2midi(data: NbsSong, filepath: str, dialog = None):
    '''It converts a NBS song to a MIDI file
    
    Parameters
    ----------
    data : NbsSong
        NbsSong
    filepath : str
        The path to the file you want to save to.
    dialog
        the dialog that shows the progress bar
    
    '''
    headers, notes, layers = data.header, data.notes, data.layers

    # The time signature upper number in ONBS
    # doesn't affect the overall tempo at all.
    # timeSign = headers.time_sign
    timeSign = 4
    tempo = headers.tempo * 60 / timeSign # BPM
    layersLen = len(layers)

    mid = MidiFile(type=1)
    tpb = mid.ticks_per_beat
    note_tpb = int(tpb / timeSign)
    tracks: list[MidiTrack] = []

    for i in range(data.maxLayer+1):
        layer = layers[i]
        programCode = INST_PROGRAMS.get(firstInstInLayer(data, i), 1) - 1

        track = MidiTrack()
        track.append(MetaMessage(
            'time_signature', numerator=headers.time_sign, denominator=4, time=0))
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo), time=0))
        track.append(Message('program_change', program=programCode, time=0))
        track.append(Message(
            'control_change', control=7, value=int(layer.volume * 127 / 100), time=0))
        pan = int(interp(layer.pan, (-100, 100), (0, 127)))
        track.append(Message('control_change', control=10, value=pan, time=0))

        tracks.append(track)
    if dialog:
        dialog.currentProgress.set(25) # 25%
        await sleep(0.001)

    accumulate_time = 0
    for note in notes:
        abs_time = int(note.tick / timeSign * tpb)
        pitch = note.key + 21
        trackIndex = note.layer
        velocity = int(note.vel * 127 / 100)
        pan = int(interp(layers[trackIndex].pan, (-100, 100), (0, 127)))

        tracks[trackIndex].append(Message(
            'control_change', control=10, value=pan, time=abs_time))
        
        if note.isPerc:
            inst: int = note.inst
            pitch = MIDI_DRUMS_BY_NBS_KEY_INST.get((pitch, inst), INST2PITCH[inst])
            keyShift = MIDI_INSTRUMENTS[inst].octave_shift * 12
            pitch -= keyShift

            tracks[trackIndex].append(Message('note_on', channel=9, note=pitch, velocity=velocity, time=abs_time))
            tracks[trackIndex].append(Message('note_off', channel=9, note=pitch, velocity=velocity, time=abs_time + note_tpb))
        else:
            tracks[trackIndex].append(Message('note_on', note=pitch, velocity=velocity, time=abs_time))
            tracks[trackIndex].append(Message('note_off', note=pitch, velocity=velocity, time=abs_time + note_tpb))

    if dialog:
        dialog.currentProgress.set(50) # 50%
        await sleep(0.001)
    mid.tracks = [absTrack2DeltaTrack(track) for track in tracks]
    if dialog:
        dialog.currentProgress.set(75) # 75%
        await sleep(0.001)

    if not filepath.endswith('.mid'):
        filepath += '.mid'
    mid.save(filepath)
