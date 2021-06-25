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

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from nbsio import NbsSong

PERCUSSIONS = (
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

INST_PROGRAMS = {
    0: 1, # Harp: Piano
    1: 33, # Double bass: Acoustic bass
    5: 25, # Guitar: Acoustic guitar (nylon)
    6: 74, # Flute: Flute
    7: 10, # Bell: Glockenspiel
    8: 113, # Chime: Tinkle bell (wind chime)
    9: 14, # Xylophone: Xylophone
    10: 12, # Iron Xylophone: Vibraphone
    11: 1,
    12: 1,
    13: 81, # Bit: Lead 1 (square)
    14: 106, # Banjo: Banjo
    15: 6, # Pling: Electric piano 2
}

INST2PITCH = {
    2: 36,
    3: 44,
    4: 81,
}

def firstInstInLayer(nbs: NbsSong, layer: int) -> int:
    if layer > nbs['maxLayer']:
        return 0
    for note in nbs['notes']:
        if note['layer'] == layer:
            return note['inst']
    return 0

class MsgComparator:
    def __init__(self, msg) -> None:
        self.msg = msg
        self.isMeta = isinstance(msg, MetaMessage)

    def __lt__(self, other) -> bool:
        if (not self.isMeta) and isinstance(other.msg, Message):
            return self.msg.time < other.msg.time
        else:
            return False

def absTrack2DeltaTrack(track) -> MidiTrack:
    track.sort(key=MsgComparator)
    ret = MidiTrack()
    ret.append(track[0])
    for i in range(1, len(track)):
        msg = track[i]
        # print(msg.time - track[i-1].time)
        ret.append(msg.copy(time=msg.time - track[i-1].time))
    return ret


async def nbs2midi(data: NbsSong, filepath: str, dialog = None):
    headers, notes, layers = data['header'], data['notes'], data['layers']

    timeSign = headers['time_sign']
    tempo = headers['tempo'] * 60 / 4
    height = headers['height']
    layersLen = len(layers)

    mid = MidiFile(type=1)
    tpb = mid.ticks_per_beat
    note_tpb = int(tpb / 4)
    tracks = []

    for i in range(data.maxLayer+1):
        programCode = INST_PROGRAMS.get(firstInstInLayer(data, i), 1) - 1

        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo), time=0))
        track.append(Message('program_change', program=programCode, time=0))

        tracks.append(track)
    if dialog:
        dialog.currentProgress.set(25) # 25%
        await sleep(0.001)

    accumulate_time = 0
    for note in notes:
        abs_time = int(note['tick'] / timeSign * tpb)
        pitch = note['key'] + 21
        trackIndex = note['layer']
        layerVel = 100
        if trackIndex < layersLen:
            layerVel = layers[trackIndex]['volume']
        velocity = int(note['vel'] * (layerVel / 100) / 100 * 127)

        isPerc = False
        if note['isPerc']:
            inst: int = note['inst']
            for a, b, c in PERCUSSIONS:
                if c == pitch and b == inst:
                    pitch = a
                    break
            else:
                pitch = INST2PITCH[inst]
            isPerc = True

        if isPerc:
            tracks[trackIndex].append(Message('note_on', channel=9, note=pitch, velocity=127, time=abs_time))
            tracks[trackIndex].append(Message('note_off', channel=9, note=pitch, velocity=127, time=abs_time + note_tpb))
        else:
            tracks[trackIndex].append(Message('note_on', note=pitch, velocity=127, time=abs_time))
            tracks[trackIndex].append(Message('note_off', note=pitch, velocity=127, time=abs_time + note_tpb))

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

if __name__ == "__main__":
    # fn = 'graphite_diamond'
    # fn = 'AYBHCM_1_2'
    # fn = "The Ground's Colour Is Yellow"
    # fn = "sandstorm"
    # fn = "Through the Fire and Flames"
    # fn = "Vì yêu cứ đâm đầu"
    # fn = "Shining_in_the_Sky"
    fn = "Megalovania - Super Smash Bros. Ultimate"

    data = NbsSong(fn + '.nbs')
    data.correctData()
    nbs2midi(data, fn)
