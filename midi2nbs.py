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


from math import gcd
from asyncio import sleep
from collections import namedtuple
from os.path import basename
from typing import Tuple, Union
from numpy import interp

from mido import MidiFile, tempo2bpm, merge_tracks

from nbsio import Layer, NbsSong, Note

MidiInstrument = namedtuple(
    "MidiInstrument", ("name", "nbs_instrument", "octave_shift", "short_name")
)
MidiDrum = namedtuple("MidiDrum", ("pitch", "name", "nbs_instrument", "nbs_pitch"))

MIDI_INSTRUMENTS = (
    MidiInstrument("Acoustic Grand Piano", 0, 0, "Grand Piano"),
    MidiInstrument("Bright Acoustic Piano", 0, 0, "Acoustic Piano"),
    MidiInstrument("Electric Grand Piano", 13, 0, "E. Grand Piano"),
    MidiInstrument("Honky - tonk Piano", 0, 0, "H.T. Piano"),
    MidiInstrument("Electric Piano 1", 13, 0, "E. Piano 1"),
    MidiInstrument("Electric Piano 2", 13, 0, "E. Piano 2"),
    MidiInstrument("Harpsichord", 0, 1, ""),
    MidiInstrument("Clavinet", 0, 0, ""),
    MidiInstrument("Celesta", 11, -1, ""),
    MidiInstrument("Glockenspiel", 11, 0, ""),
    MidiInstrument("Music Box", 11, 0, ""),
    MidiInstrument("Vibraphone", 11, 0, ""),
    MidiInstrument("Marimba", 11, 0, ""),
    MidiInstrument("Xylophone", 9, 0, ""),
    MidiInstrument("Tubular Bells", 7, -1, "T. Bells"),
    MidiInstrument("Dulcimer", 7, 0, ""),
    MidiInstrument("Drawbar Organ", 1, 1, "D. Organ"),
    MidiInstrument("Percussive Organ", 1, 1, "P. Organ"),
    MidiInstrument("Rock Organ", 0, 0, ""),
    MidiInstrument("Church Organ", 0, 0, ""),
    MidiInstrument("Reed Organ", 0, 0, ""),
    MidiInstrument("Accordion", 0, 0, ""),
    MidiInstrument("Harmonica", 0, 0, ""),
    MidiInstrument("Tango Accordion", 0, 0, "T. Accordion"),
    MidiInstrument("Acoustic Guitar (nylon)", 5, 0, "A.Guitar(nylon)"),
    MidiInstrument("Acoustic Guitar (steel)", 5, 0, "A.Guitar(steel)"),
    MidiInstrument("Electric Guitar (jazz)", 5, 1, "E.Guitar(jazz)"),
    MidiInstrument("Electric Guitar (clean)", 5, 0, "E.Guitar(clean)"),
    MidiInstrument("Electric Guitar (muted)", 5, 0, "E.Guitar(mute)"),
    MidiInstrument("Overdriven Guitar", 5, -1, "OD Guitar"),
    MidiInstrument("Distortion Guitar", 5, -1, "Dist. Guitar"),
    MidiInstrument("Guitar Harmonics", 5, 0, "Guitar H."),
    MidiInstrument("Acoustic Bass", 1, 1, "A. Bass"),
    MidiInstrument("Electric Bass (finger)", 1, 2, "E.Bass (finger)"),
    MidiInstrument("Electric Bass (pick)", 1, 2, "E.Bass (pick)"),
    MidiInstrument("Fretless Bass", 1, 2, ""),
    MidiInstrument("Slap Bass 1", 1, 2, ""),
    MidiInstrument("Slap Bass 2", 1, 2, ""),
    MidiInstrument("Synth Bass 1", 1, 2, ""),
    MidiInstrument("Synth Bass 2", 1, 2, ""),
    MidiInstrument("Violin", 6, 0, ""),
    MidiInstrument("Viola", 6, 0, ""),
    MidiInstrument("Cello", 6, 0, ""),
    MidiInstrument("Contrabass", 6, 0, ""),
    MidiInstrument("Tremolo Strings", 0, 0, "T. Strings"),
    MidiInstrument("Pizzicato Strings", 0, 0, "P. Strings"),
    MidiInstrument("Orchestral Harp", 8, 0, "O. Harp"),
    MidiInstrument("Timpani", 3, 1, ""),
    MidiInstrument("String Ensemble 1", 0, 0, "String E. 1"),
    MidiInstrument("String Ensemble 2", 0, 0, "String E. 2"),
    MidiInstrument("Synth Strings 1", 0, 0, "S. Strings 1"),
    MidiInstrument("Synth Strings 2", 0, 0, "S. Strings 2"),
    MidiInstrument("Choir Aahs", 0, 0, ""),
    MidiInstrument("Voice Oohs", 0, 0, ""),
    MidiInstrument("Synth Choir", 0, 0, ""),
    MidiInstrument("Orchestra hit", 0, 0, "O. Hit"),
    MidiInstrument("Trumpet", 0, 0, ""),
    MidiInstrument("Trombone", 0, 0, ""),
    MidiInstrument("Tuba", 0, 0, ""),
    MidiInstrument("Muted Trumpet", 0, 0, ""),
    MidiInstrument("French Horn", 0, 0, ""),
    MidiInstrument("Brass Section", 0, 0, ""),
    MidiInstrument("Synth Brass 1", 1, 1, "S. Brass 1"),
    MidiInstrument("Synth Brass 2", 1, 1, "S. Brass 2"),
    MidiInstrument("Soprano Sax", 6, 0, ""),
    MidiInstrument("Alto Sax", 6, 0, ""),
    MidiInstrument("Tenor Sax", 6, 0, ""),
    MidiInstrument("Baritone Sax", 6, 0, ""),
    MidiInstrument("Oboe", 6, 0, ""),
    MidiInstrument("English Horn", 6, 0, ""),
    MidiInstrument("Bassoon", 6, -1, ""),
    MidiInstrument("Clarinet", 6, 0, ""),
    MidiInstrument("Piccolo", 6, -1, ""),
    MidiInstrument("Flute", 6, -1, ""),
    MidiInstrument("Recorder", 6, -1, ""),
    MidiInstrument("Pan Flute", 6, -1, ""),
    MidiInstrument("Blown Bottle", 6, -1, ""),
    MidiInstrument("Shakuhachi", 6, -1, ""),
    MidiInstrument("Whistle", 6, -1, ""),
    MidiInstrument("Ocarina", 6, -1, ""),
    MidiInstrument("Lead 1 (square)", 13, 0, "L.1 (square)"),
    MidiInstrument("Lead 2 (sawtooth)", 13, 0, "L.2 (sawtooth)"),
    MidiInstrument("Lead 3 (calliope)", 13, 0, "L.3 (calliope)"),
    MidiInstrument("Lead 4 (chiff)", 13, 0, "L.4 (chiff)"),
    MidiInstrument("Lead 5 (charang)", 13, 0, "L.5 (charang)"),
    MidiInstrument("Lead 6 (voice)", 13, 0, "L.6 (voice)"),
    MidiInstrument("Lead 7 (fifths)", 13, 0, "L.7 (fifths)"),
    MidiInstrument("Lead 8 (bass + lead)", 13, 1, "L.8 (bass + lead)"),
    MidiInstrument("Pad 1 (new age)", 0, 0, "P.1 (new age)"),
    MidiInstrument("Pad 2 (warm)", 0, 0, "P.2 (warm)"),
    MidiInstrument("Pad 3 (polysynth)", 0, 0, "P.3 (polysynth)"),
    MidiInstrument("Pad 4 (choir)", 0, 0, "P.4 (choir)"),
    MidiInstrument("Pad 5 (bowed)", 0, 0, "P.5 (bowed)"),
    MidiInstrument("Pad 6 (metallic)", 0, 0, "P.6 (metallic)"),
    MidiInstrument("Pad 7 (halo)", 0, 0, "P.7 (halo)"),
    MidiInstrument("Pad 8 (sweep)", 0, 0, "P.8 (sweep)"),
    MidiInstrument("FX 1 (rain)", -1, 0, "Fx (rain)"),
    MidiInstrument("FX 2 (soundtrack)", -1, 0, "Fx (strack)"),
    MidiInstrument("FX 3 (crystal)", 13, 0, "Fx (crystal)"),
    MidiInstrument("FX 4 (atmosphere)", 0, 0, "Fx (atmosph.)"),
    MidiInstrument("FX 5 (brightness)", 0, 0, "Fx (bright.)"),
    MidiInstrument("FX 6 (goblins)", -1, 0, "Fx (goblins)"),
    MidiInstrument("FX 7 (echoes)", -1, 0, "Fx (echoes)"),
    MidiInstrument("FX 8 (sci - fi)", -1, 0, "Fx (sci - fi)"),
    MidiInstrument("Sitar", 14, 0, ""),
    MidiInstrument("Banjo", 14, 0, ""),
    MidiInstrument("Shamisen", 14, 0, ""),
    MidiInstrument("Koto", 14, 0, ""),
    MidiInstrument("Kalimba", 1, 1, ""),
    MidiInstrument("Bagpipe", 0, 0, ""),
    MidiInstrument("Fiddle", 0, 0, ""),
    MidiInstrument("Shanai", 0, 0, ""),
    MidiInstrument("Tinkle Bell", 7, -1, ""),
    MidiInstrument("Agogo", 0, 0, ""),
    MidiInstrument("Steel Drums", 10, 0, ""),
    MidiInstrument("Woodblock", 4, 0, ""),
    MidiInstrument("Taiko Drum", 3, 0, ""),
    MidiInstrument("Melodic Tom", 3, -1, ""),
    MidiInstrument("Synth Drum", 3, 0, ""),
    MidiInstrument("Reverse Cymbal", -1, 0, "Rev. Cymbal"),
    MidiInstrument("Guitar Fret Noise", -1, 0, "Guitar F. Noise"),
    MidiInstrument("Breath Noise", -1, 0, ""),
    MidiInstrument("Seashore", -1, 0, ""),
    MidiInstrument("Bird Tweet", -1, 0, ""),
    MidiInstrument("Telephone Ring", -1, 0, "Telephone"),
    MidiInstrument("Helicopter", -1, 0, ""),
    MidiInstrument("Applause", -1, 0, ""),
    MidiInstrument("Gunshot", 0, 0, ""),
    MidiInstrument("Percussion", -1, 0, ""),
)

MIDI_DRUMS = (
    MidiDrum(27, "High-Q", -1, 0),
    MidiDrum(28, "Slap", -1, 0),
    MidiDrum(29, "Scratch Push", -1, 0),
    MidiDrum(30, "Scratch Pull", -1, 0),
    MidiDrum(31, "Sticks", -1, 0),
    MidiDrum(32, "Square Click", -1, 0),
    MidiDrum(33, "Metronome Click", -1, 0),
    MidiDrum(34, "Metronome Bell", -1, 0),
    MidiDrum(35, "Acoustic Bass Drum", 2, 10),
    MidiDrum(36, "Bass Drum 1", 2, 6),
    MidiDrum(37, "Side Stick", 4, 6),
    MidiDrum(38, "Acoustic Snare", 3, 8),
    MidiDrum(39, "Hand Clap", 4, 6),
    MidiDrum(40, "Electric Snare", 3, 4),
    MidiDrum(41, "Low Floor Tam", 2, 6),
    MidiDrum(42, "Closed Hi - hat", 3, 22),
    MidiDrum(43, "High Floor Tom", 2, 13),
    MidiDrum(44, "Pedal Hi - hat", 3, 22),
    MidiDrum(45, "Low Tom", 2, 15),
    MidiDrum(46, "Open Hi - hat", 3, 18),
    MidiDrum(47, "Low-mid Tom", 2, 20),
    MidiDrum(48, "Hi-mid Tom", 2, 23),
    MidiDrum(49, "Crash Cymbal 1", 3, 17),
    MidiDrum(50, "High Tom", 2, 23),
    MidiDrum(51, "Ride Cymbal 1", 3, 24),
    MidiDrum(52, "Chinese Cymbal", 3, 8),
    MidiDrum(53, "Ride Bell", 3, 13),
    MidiDrum(54, "Tambourine", 4, 18),
    MidiDrum(55, "Splash Cymbal", 3, 18),
    MidiDrum(56, "Cowbell", 4, 1),
    MidiDrum(57, "Crash Cymbal 2", 3, 13),
    MidiDrum(58, "Vibra Slap", 4, 2),
    MidiDrum(59, "Ride Cymbal 2", 3, 13),
    MidiDrum(60, "High Bongo", 4, 9),
    MidiDrum(61, "Low Bongo", 4, 2),
    MidiDrum(62, "Mute High Conga", 4, 8),
    MidiDrum(63, "Open High Conga", 2, 22),
    MidiDrum(64, "Low Conga", 2, 15),
    MidiDrum(65, "High Timbale", 3, 13),
    MidiDrum(66, "Low Timbale", 3, 8),
    MidiDrum(67, "High Agogo", 4, 8),
    MidiDrum(68, "Low Agogo", 4, 3),
    MidiDrum(69, "Cabasa", 4, 20),
    MidiDrum(70, "Maracas", 4, 23),
    MidiDrum(71, "Short Whistle", 4, 23),
    MidiDrum(72, "Long Whistle", 4, 23),
    MidiDrum(73, "Short Guiro", 4, 17),
    MidiDrum(74, "Long Guiro", 4, 11),
    MidiDrum(75, "Claves", 4, 18),
    MidiDrum(76, "High Wood Block", 4, 9),
    MidiDrum(77, "Low Wood Block", 4, 5),
    MidiDrum(78, "Mute Cuica", 3, 4),
    MidiDrum(79, "Open Cuica", 3, 16),
    MidiDrum(80, "Mute Triangle", 4, 17),
    MidiDrum(81, "Open Triangle", 4, 22),
    MidiDrum(82, "Shaker", 3, 22),
    MidiDrum(83, "Jingle bell", -1, 0),
    MidiDrum(84, "Bell tree", -1, 0),
    MidiDrum(85, "Castanets", 4, 21),
    MidiDrum(86, "Mute Surdo", 2, 14),
    MidiDrum(87, "Open Surdo", 2, 7),
)

MIDI_DRUMS_BY_MIDI_PITCH = {obj.pitch: obj for obj in MIDI_DRUMS}

NOTE_POS_MULTIPLIER = 18
"""The value must be divisible by 2, 3 (to handle triplets).
It also limits the maximum expand multiplier."""

NBS_PITCH_IN_MIDI_PITCHBEND = 40.96


def extractKeyAndInst(
    msg, trackInst: int, keyShift: int
) -> Union[Tuple[int, int], None]:
    if msg.channel == 9:
        midiDrum = MIDI_DRUMS_BY_MIDI_PITCH.get(msg.note, MIDI_DRUMS_BY_MIDI_PITCH[27])
        if midiDrum.nbs_instrument == -1:
            return None
        key = midiDrum.nbs_pitch + 36
        inst = midiDrum.nbs_instrument
        return key, inst
    else:
        key = max(0, (msg.note - 21) + keyShift)
        return key, trackInst


async def midi2nbs(
    filepath: str,
    expandMultiplier=1,
    importDurations=False,
    durationSpacing=1,
    importVelocities=True,
    importPanning=True,
    importPitches=True,
    dialog=None,
) -> NbsSong:
    autoExpand = expandMultiplier == 0
    if autoExpand:
        expandMultiplier = 1

    mid = MidiFile(filepath)
    tpb = mid.ticks_per_beat
    timeSign = 4
    tempo = -1

    nbs: NbsSong = NbsSong()
    headers, notes, layers = nbs.header, nbs.notes, nbs.layers
    headers.import_name = basename(filepath)

    if dialog:
        dialog.currentProgress.set(10)
        await sleep(0.001)

    absTime: int = 0
    notePosGcd: int = -1
    for msg in merge_tracks(mid.tracks):
        absTime += msg.time
        if msg.is_meta:
            if msg.type == "time_signature":
                headers.time_sign = msg.numerator
            elif (msg.type == "set_tempo") and (tempo == -1):
                tempo = tempo2bpm(msg.tempo)
                headers.tempo = tempo * timeSign / 60
        elif autoExpand:
            #  Perform automatic space expanding (if specified)
            if msg.type == "note_on":
                if msg.velocity > 0:
                    notePos = round(absTime * timeSign * NOTE_POS_MULTIPLIER / tpb)
                    if notePos % 2 == 1:
                        notePos += 1  # Make all notePos even
                        # to reduce the expand multiplier
                    if notePosGcd != -1:
                        notePosGcd = gcd(notePosGcd, notePos)
                    else:
                        notePosGcd = notePos
    if autoExpand:
        expandMultiplier = NOTE_POS_MULTIPLIER / notePosGcd
    headers.tempo *= expandMultiplier
    headers.time_sign = int(headers.time_sign * expandMultiplier)

    emptyTracks = []  # Tracks which don't have any 'note_on' message
    percTracks = []  # Tracks containing only percussion messages
    for i, track in enumerate(mid.tracks):
        isEmpty = True
        isPerc = True
        for msg in track:
            if msg.type == "note_on":
                isEmpty = False
                if msg.channel != 9:
                    isPerc = False
                    break
        if isEmpty:
            emptyTracks.append(i)
        if isPerc:
            percTracks.append(i)

    if dialog:
        dialog.currentProgress.set(40)
        await sleep(0.001)

    baseLayer = -1
    totalTracks = len(mid.tracks)
    ceilingLayer = baseLayer
    for i, track in enumerate(mid.tracks):
        if i in emptyTracks:
            continue
        absTime: int = 0
        isPerc = i in percTracks
        trackName = "Percussion" if isPerc else ""
        trackInst: int = 0
        keyShift: int = 0
        trackVel = 100
        pan = 0
        pitch = 0
        baseLayer = ceilingLayer + 1
        layer = -1
        lastTick = -1
        duration = 0
        currentNotes = []  # Notes in the current tick
        for msg in track:
            innerBaseLayer = baseLayer
            absTime += msg.time
            if msg.is_meta:
                if (msg.type == "track_name") and not trackName:
                    trackName = msg.name
                    layers.append(Layer(trackName, False, trackVel))
            else:
                tick = round(absTime * timeSign / tpb * expandMultiplier)
                if msg.type == "note_on":
                    extracted = extractKeyAndInst(msg, trackInst, keyShift)
                    if not extracted:
                        continue
                    key, inst = extracted
                    velocity = (
                        int(msg.velocity * 100 / 127) if importVelocities else 100
                    )
                    if velocity > 0:
                        enoughSpace = tick != lastTick
                        if not enoughSpace:
                            layer += 1
                            if layer >= len(layers):
                                layers.append(
                                    Layer(
                                        f"{trackName} ({layer-innerBaseLayer+1})",
                                        False,
                                        trackVel,
                                    )
                                )
                        else:
                            layer = innerBaseLayer

                        note = Note(tick, layer, inst, key, velocity, pan, pitch)
                        notes.append(note)
                        currentNotes.append(note)
                        ceilingLayer = max(ceilingLayer, layer)
                        lastTick = tick
                    elif importDurations:
                        duration = tick - lastTick
                elif importDurations and (msg.type == "note_off"):
                    duration = tick - lastTick
                elif (msg.type == "program_change") and not isPerc:
                    midiInst: MidiInstrument = MIDI_INSTRUMENTS[msg.program]  # type: ignore
                    trackInst = midiInst.nbs_instrument
                    if trackInst == -1:
                        trackInst = 0
                    keyShift = midiInst.octave_shift * 12
                    if not trackName:
                        trackName = (
                            midiInst.short_name
                            if midiInst.short_name
                            else midiInst.name
                        )
                        layers.append(Layer(trackName, False, trackVel))
                elif msg.type == "control_change":
                    if importPanning and (msg.control == 10):  # Pan
                        pan = int(interp(msg.value, (0, 127), (-100, 100)))
                    elif importVelocities and (msg.control == 7):  # Volume
                        trackVel = int(msg.value * 100 / 127)
                elif importPitches and (msg.type == "pitchwheel"):
                    pitch = int(msg.pitch / NBS_PITCH_IN_MIDI_PITCHBEND)

                if duration > 0 and currentNotes:
                    extracted = extractKeyAndInst(msg, trackInst, keyShift)
                    if not extracted:
                        continue
                    key, inst = extracted
                    note = next(
                        filter(
                            lambda note: (note.key == key)
                            and (note.inst == inst)
                            and not note.isPerc,
                            currentNotes,
                        ),
                        None,
                    )
                    if note:
                        for durationIndex, newTick in enumerate(
                            range(tick - duration, tick)
                        ):
                            vel = int(note.vel * (duration - durationIndex) / duration)
                            if (vel > 1) and (durationIndex % durationSpacing == 0):
                                newNote = Note(
                                    newTick,
                                    note.layer,
                                    note.inst,
                                    note.key,
                                    vel,
                                    pan,
                                    pitch,
                                )
                                notes.append(newNote)
                        currentNotes.remove(note)
                    duration = 0
        
        if dialog:
            dialog.currentProgress.set(40 + i * 40 / totalTracks)
            await sleep(0.001)

    nbs.correctData()
    return nbs
