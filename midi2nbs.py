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
from math import gcd
from os.path import basename
from typing import Optional, Tuple

from mido import MidiFile, merge_tracks, tempo2bpm
from numpy import interp

from common import MIDI_DRUMS, MIDI_INSTRUMENTS, NBS_PITCH_IN_MIDI_PITCHBEND
from nbsio import Layer, NbsSong, Note

MIDI_DRUMS_BY_MIDI_PITCH = {obj.pitch: obj for obj in MIDI_DRUMS}

NOTE_POS_MULTIPLIER = 18
"""The value must be divisible by 2, 3 (to handle triplets).
It also limits the maximum expand multiplier."""


def extractKeyAndInst(
    msg, trackInst: int, keyShift: int
) -> Optional[Tuple[int, int]]:
    if msg.channel == 9:
        midiDrum = MIDI_DRUMS_BY_MIDI_PITCH.get(msg.note, MIDI_DRUMS_BY_MIDI_PITCH[27])
        if midiDrum.nbs_instrument == -1:
            return None
        key = midiDrum.nbs_pitch + 36
        inst = midiDrum.nbs_instrument
    else:
        key = max(0, (msg.note - 21) + keyShift)
        inst = trackInst
    return key, inst

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
    # The time signature upper number in ONBS
    # doesn't affect the overall tempo at all.
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
                    note = None
                    key, inst = extracted
                    for headNote in currentNotes:
                        if (headNote.key == key)  and (headNote.inst == inst) \
                                and not headNote.isPerc:
                            note = headNote
                            break
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
