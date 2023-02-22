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

import zipfile

from lxml import etree
from nbsio import Layer, NbsSong, Note
from functools import lru_cache
from os.path import basename
from asyncio import sleep

from common import MIDI_INSTRUMENTS, MIDI_DRUMS

MIDI_DRUMS_BY_MIDI_PITCH = {obj.pitch: obj for obj in MIDI_DRUMS}

expandMulDict = {
    "64th": 4,
    "32nd": 2,
}
tupletMulDict = {
    "64th": 6,
    "32nd": 5,
    "16th": 4,
    "eighth": 3,
    "quarter": 2,
}

durationMap = {
    "128th": 0.125,
    "64th": 0.25,
    "32nd": 0.5,
    "16th": 1,
    "eighth": 2,
    "quarter": 4,
    "half": 8,
    "whole": 16,
}

MAX_TEMPO = 60

class FileError(Exception):
    pass

@lru_cache
def fraction2length(fraction: str) -> int:
    '''It takes a string in the form of a fraction, and returns the length of
    the note in 16th notes
    
    Parameters
    ----------
    fraction : str
        str
    
    Returns
    -------
        The length of the note in 16th notes.
    
    '''
    if isinstance(fraction, str):
        parts = fraction.split('/')
        return int(parts[0]) * int(16 / int(parts[1]))
    return 0

async def musescore2nbs(filepath: str, expandMultiplier=1, autoExpand=True, dialog=None) -> NbsSong:
    """Convert a MuseScore file and return a NbsSong instance.

if the conversation fails, this function returns None.

Args:
- filepath: The path of the input file. .mscz and .mscx files are supported.
- expandMultiplier: Multiplys all note positions by this variable.
    The default is 1, meaning not multiplying
- autoExpand: Optional; If it's True, the expand multiplier will be detected automatically.
- dialog: Optional; The ProgressDialog to be used for reporting progress.

Return:
    A NbsSong contains meta-information and notes' data (position, pitch, velocity
        and tuning).
    """

    if autoExpand:
        expandMultiplier = 1

    # Reads the input file

    xml = None
    if filepath.endswith(".mscz"):
        with zipfile.ZipFile(filepath, 'r') as zip:
            filename: str = ""
            for name in zip.namelist():
                if name.endswith(".mscx"):
                    filename = name
                    break
            if filename:
                with zip.open(filename) as file:
                    xml = etree.parse(file, parser=None)
            else:
                raise FileError("This file isn't a MuseScore file or it doesn't contain a MuseScore file.")
    elif filepath.endswith(".mscx"):
        xml = etree.parse(filepath, parser=None)
    else:
        raise FileError("This file isn't a MuseScore file")

    if version := xml.findtext('programVersion'):
        if not (version.startswith('3') or version.startswith('4')):
            raise NotImplementedError("This file is created by a older version of MuseScore. Please use MuseScore 3 or 4 to re-save the files before importing.")

    nbs: NbsSong = NbsSong()

    # Get meta-information

    header = nbs.header
    score = xml.find("Score")
    header.import_name = basename(filepath)
    header.name = (score.xpath("metaTag[@name='workTitle']/text()") or ('',))[0]
    header.author = (score.xpath("metaTag[@name='arranger']/text()") or ('',))[0]
    header.orig_author = (score.xpath("metaTag[@name='composer']/text()") or ('',))[0]

    if timeSign := score.findtext("Staff/Measure/voice/TimeSig/sigN"):
        header.time_sign = int(timeSign)

    if tempoTxt := score.findtext("Staff/Measure/voice/Tempo/tempo"):
        bpm: float = 60 * float(tempoTxt)
        tps: float = bpm * 4 / 60
        header.tempo = tps

    if dialog:
        dialog.currentProgress.set(20)
        await sleep(0.001)

    # Remove empty layers

    emptyStaffs: list = []
    staffCount = 0
    for staff in score.iterfind("Staff"):
        staffCount += 1
        for elem in staff.xpath("Measure/voice/*"):
            if elem.tag == "Chord":
                break
        else:
            staffId = int(staff.get("id"))
            emptyStaffs.append(staffId)

    # Get layer instruments from staff program IDs

    staffInsts = {}
    for part in score.iterfind("Part"):
        isPerc = bool(part.xpath("Instrument[@id='drumset']")) \
            or bool(part.xpath("Staff/StaffType[@group='percussion']"))
        program = int(part.find("Instrument/Channel/program").get("value"))
        for staff in part.iterfind("Staff"):
            staffId = int(staff.get("id"))
            if staffId not in emptyStaffs:
                # INST_INFO[-1] is the percussion (drumset) instrument
                staffInsts[staffId] = \
                    MIDI_INSTRUMENTS[program] if not isPerc else MIDI_INSTRUMENTS[-1]

    tempo: float = header.tempo

    if dialog:
        dialog.currentProgress.set(30)
        await sleep(0.001)

    # Perform note auto-expanding (if specified) and tuplet detection

    hasComplexTuplets = False
    for elem in score.xpath("Staff/Measure/voice/*"):
        if elem.tag == "Tuplet":
            normalNotes = int(elem.findtext("normalNotes"))
            actualNotes = int(elem.findtext("actualNotes"))
            if not hasComplexTuplets:
                hasComplexTuplets = actualNotes != normalNotes
            if hasComplexTuplets and autoExpand and (baseNote := elem.findtext("baseNote")):
                if baseNote in tupletMulDict:
                    multiplier = max(tupletMulDict[baseNote], expandMultiplier)
                    if (tempo * multiplier) <= MAX_TEMPO:
                        expandMultiplier = multiplier
        if autoExpand and (duration := elem.findtext("durationType")):
            if duration in expandMulDict:
                multiplier = max(expandMulDict[duration], expandMultiplier)
                if (tempo * multiplier) <= MAX_TEMPO:
                    expandMultiplier = multiplier

    header.tempo = int(tempo * expandMultiplier)
    header.time_sign *= expandMultiplier

    if dialog:
        dialog.currentProgress.set(40)
        await sleep(0.001)

    # Import note data

    baseLayer = -1
    ceilingLayer = baseLayer
    for staff in score.iterfind("Staff"):
        staffId = int(staff.get("id"))
        if staffId in emptyStaffs:
            continue
        baseLayer = ceilingLayer + 1
        chords = 0
        rests = 0
        tick = 0
        lastTick = -1
        layer = -1
        staffInst = staffInsts[staffId][1]
        for measure in staff.iterfind("Measure"):
            beginTick = tick
            endTick = -1
            innerBaseLayer = baseLayer
            innerCeilingLayer = innerBaseLayer
            for voi, voice in enumerate(measure.iterfind("voice")):
                tick = beginTick
                tick += fraction2length(voice.findtext("location/fractions")) * expandMultiplier
                tupletNotesRemaining = 0
                normalNotes = 0
                actualNotes = 0
                for elem in voice:
                    #print(f'{elem.tag=}, {tick=}, {tickCheckpoint=}')
                    dots = int(elem.findtext("dots") or 0)
                    if elem.tag == "Chord":
                        chords += 1
                        enoughSpace = int(tick) != int(lastTick)
                        # print(f'{int(lastTick)=} {int(tick)=} {enoughSpace=}')
                        for i, note in enumerate(elem.iterfind("Note")):
                            if voi > 0:
                                innerBaseLayer = innerCeilingLayer
                            if note.xpath("Spanner[@type='Tie']/prev"):
                                break
                            if not enoughSpace:
                                layer += 1
                            else:
                                layer = innerBaseLayer+i
                            if layer >= len(nbs.layers):
                                nbs.layers.append(Layer("{} (v. {})".format(staffInsts[staffId][0], voi+1), False, 100, 100))
                            inst = staffInst
                            isPerc = False
                            key = -1
                            if inst > -1:
                                key = int(note.find("pitch").text) - 21
                            else:
                                drumIndex = int(note.find("pitch").text)
                                _, _, inst, key = MIDI_DRUMS_BY_MIDI_PITCH.get(drumIndex, MIDI_DRUMS[27])
                                key += 36
                                isPerc = True
                                if inst == -1: inst = 0
                            tuning = note.find("tuning")
                            pitch = int(float(tuning.text)) if tuning is not None else 0
                            # TODO: Support relative velocity
                            vel = max(min(int(note.findtext("velocity") or 100), 127), 0)
                            nbs.notes.append(Note(int(tick), layer, inst, key, vel, 100, pitch))
                            ceilingLayer = max(ceilingLayer, layer)
                            innerCeilingLayer = max(innerCeilingLayer, i)
                        lastTick = tick
                        length = durationMap[elem.findtext("durationType")] * (2-(1/(2**dots))) * expandMultiplier
                        if hasComplexTuplets and (tupletNotesRemaining > 0):
                            length = length * normalNotes / actualNotes
                            tupletNotesRemaining -= 1
                        tick += length
                    elif elem.tag == "Rest":
                        rests += 1
                        durationType = elem.findtext("durationType")
                        length = 0
                        if durationType == "measure":
                            length = fraction2length(elem.findtext("duration")) * expandMultiplier
                        else:
                            length = int(durationMap[durationType] * (2-(1/(2**dots))) * expandMultiplier)
                        if hasComplexTuplets and (tupletNotesRemaining > 0):
                            length = length * normalNotes / actualNotes
                            tupletNotesRemaining -= 1
                        tick += length
                    elif (elem.tag == "Tuplet") and hasComplexTuplets:
                        normalNotes = int(elem.findtext("normalNotes"))
                        actualNotes = int(elem.findtext("actualNotes"))
                        tupletNotesRemaining = actualNotes
                endTick = max(endTick, tick)
            tick = round(endTick)
        # print(f'{tick=}, {chords=}, {rests=}, {ceilingLayer=}')
        if dialog:
            dialog.currentProgress.set(40 + staffId * 40 / staffCount)
            await sleep(0.001)

    nbs.correctData()
    return nbs
