from addict import Dict
from lxml import etree
import zipfile
from nbsio import NbsSong
from functools import lru_cache
from os.path import basename
from re import search
from asyncio import sleep

INST_INFO = (
    ('Acoustic Grand Piano', 0, 0, 'Grand Piano'),
    ('Bright Acoustic Piano', 0, 0, 'Acoustic Piano'),
    ('Electric Grand Piano', 13, 0, 'E. Grand Piano'),
    ('Honky - tonk Piano', 0, 0, 'H.T. Piano'),
    ('Electric Piano 1', 13, 0, 'E. Piano 1'),
    ('Electric Piano 2', 13, 0, 'E. Piano 2'),
    ('Harpsichord', 0, 1, ''),
    ('Clavinet', 0, 0, ''),
    ('Celesta', 11, -1, ''),
    ('Glockenspiel', 11, 0, ''),
    ('Music Box', 11, 0, ''),
    ('Vibraphone', 11, 0, ''),
    ('Marimba', 11, 0, ''),
    ('Xylophone', 9, 0, ''),
    ('Tubular Bells', 7, -1, 'T. Bells'),
    ('Dulcimer', 7, 0, ''),
    ('Drawbar Organ', 1, 1, 'D. Organ'),
    ('Percussive Organ', 1, 1, 'P. Organ'),
    ('Rock Organ', 0, 0, ''),
    ('Church Organ', 0, 0, ''),
    ('Reed Organ', 0, 0, ''),
    ('Accordion', 0, 0, ''),
    ('Harmonica', 0, 0, ''),
    ('Tango Accordion', 0, 0, 'T. Accordion'),
    ('Acoustic Guitar (nylon)', 5, 0, 'A.Guitar(nylon)'),
    ('Acoustic Guitar (steel)', 5, 0, 'A.Guitar(steel)'),
    ('Electric Guitar (jazz)', 5, 1, 'E.Guitar(jazz)'),
    ('Electric Guitar (clean)', 5, 0, 'E.Guitar(clean)'),
    ('Electric Guitar (muted)', -1, 0, 'E.Guitar(mute)'),
    ('Overdriven Guitar', 5, -1, 'OD Guitar'),
    ('Distortion Guitar', 5, -1, 'Dist. Guitar'),
    ('Guitar Harmonics', 5, 0, 'Guitar H.'),
    ('Acoustic Bass', 1, 1, 'A. Bass'),
    ('Electric Bass (finger)', 1, 2, 'E.Bass (finger)'),
    ('Electric Bass (pick)', 1, 2, 'E.Bass (pick)'),
    ('Fretless Bass', 1, 2, ''),
    ('Slap Bass 1', 1, 2, ''),
    ('Slap Bass 2', 1, 2, ''),
    ('Synth Bass 1', 1, 2, ''),
    ('Synth Bass 2', 1, 2, ''),
    ('Violin', 6, 0, ''),
    ('Viola', 6, 0, ''),
    ('Cello', 6, 0, ''),
    ('Contrabass', 6, 0, ''),
    ('Tremolo Strings', 0, 0, 'T. Strings'),
    ('Pizzicato Strings', 0, 0, 'P. Strings'),
    ('Orchestral Harp', 8, 0, 'O. Harp'),
    ('Timpani', 3, 1, ''),
    ('String Ensemble 1', 0, 0, 'String E. 1'),
    ('String Ensemble 2', 0, 0, 'String E. 2'),
    ('Synth Strings 1', 0, 0, 'S. Strings 1'),
    ('Synth Strings 2', 0, 0, 'S. Strings 2'),
    ('Choir Aahs', 0, 0, ''),
    ('Voice Oohs', 0, 0, ''),
    ('Synth Choir', 0, 0, ''),
    ('Orchestra hit', 0, 0, 'O. Hit'),
    ('Trumpet', 0, 0, ''),
    ('Trombone', 0, 0, ''),
    ('Tuba', 0, 0, ''),
    ('Muted Trumpet', 0, 0, ''),
    ('French Horn', 0, 0, ''),
    ('Brass Section', 0, 0, ''),
    ('Synth Brass 1', 1, 1, 'S. Brass 1'),
    ('Synth Brass 2', 1, 1, 'S. Brass 2'),
    ('Soprano Sax', 6, 0, ''),
    ('Alto Sax', 6, 0, ''),
    ('Tenor Sax', 6, 0, ''),
    ('Baritone Sax', 6, 0, ''),
    ('Oboe', 6, 0, ''),
    ('English Horn', 6, 0, ''),
    ('Bassoon', 6, -1, ''),
    ('Clarinet', 6, 0, ''),
    ('Piccolo', 6, -1, ''),
    ('Flute', 6, -1, ''),
    ('Recorder', 6, -1, ''),
    ('Pan Flute', 6, -1, ''),
    ('Blown Bottle', 6, -1, ''),
    ('Shakuhachi', 6, -1, ''),
    ('Whistle', 6, -1, ''),
    ('Ocarina', 6, -1, ''),
    ('Lead 1 (square)', 0, 0, 'L.1 (square)'),
    ('Lead 2 (sawtooth)', 0, 0, 'L.2 (sawtooth)'),
    ('Lead 3 (calliope)', 0, 0, 'L.3 (calliope)'),
    ('Lead 4 (chiff)', 0, 0, 'L.4 (chiff)'),
    ('Lead 5 (charang)', 0, 0, 'L.5 (charang)'),
    ('Lead 6 (voice)', 0, 0, 'L.6 (voice)'),
    ('Lead 7 (fifths)', 0, 0, 'L.7 (fifths)'),
    ('Lead 8 (bass + lead)', 0, 1, 'L.8 (bass + lead)'),
    ('Pad 1 (new age)', 0, 0, 'P.1 (new age)'),
    ('Pad 2 (warm)', 0, 0, 'P.2 (warm)'),
    ('Pad 3 (polysynth)', 0, 0, 'P.3 (polysynth)'),
    ('Pad 4 (choir)', 0, 0, 'P.4 (choir)'),
    ('Pad 5 (bowed)', 0, 0, 'P.5 (bowed)'),
    ('Pad 6 (metallic)', 0, 0, 'P.6 (metallic)'),
    ('Pad 7 (halo)', 0, 0, 'P.7 (halo)'),
    ('Pad 8 (sweep)', 0, 0, 'P.8 (sweep)'),
    ('FX 1 (rain)', -1, 0, 'Fx (rain)'),
    ('FX 2 (soundtrack)', -1, 0, 'Fx (strack)'),
    ('FX 3 (crystal)', 13, 0, 'Fx (crystal)'),
    ('FX 4 (atmosphere)', 0, 0, 'Fx (atmosph.)'),
    ('FX 5 (brightness)', 0, 0, 'Fx (bright.)'),
    ('FX 6 (goblins)', -1, 0, 'Fx (goblins)'),
    ('FX 7 (echoes)', -1, 0, 'Fx (echoes)'),
    ('FX 8 (sci - fi)', -1, 0, 'Fx (sci - fi)'),
    ('Sitar', 14, 0, ''),
    ('Banjo', 14, 0, ''),
    ('Shamisen', 14, 0, ''),
    ('Koto', 14, 0, ''),
    ('Kalimba', 1, 1, ''),
    ('Bagpipe', 0, 0, ''),
    ('Fiddle', 0, 0, ''),
    ('Shanai', 0, 0, ''),
    ('Tinkle Bell', 7, -1, ''),
    ('Agogo', 0, 0, ''),
    ('Steel Drums', 10, 0, ''),
    ('Woodblock', 4, 0, ''),
    ('Taiko Drum', 3, 0, ''),
    ('Melodic Tom', 3, -1, ''),
    ('Synth Drum', 3, 0, ''),
    ('Reverse Cymbal', -1, 0, 'Rev. Cymbal'),
    ('Guitar Fret Noise', -1, 0, 'Guitar F. Noise'),
    ('Breath Noise', -1, 0, ''),
    ('Seashore', -1, 0, ''),
    ('Bird Tweet', -1, 0, ''),
    ('Telephone Ring', -1, 0, 'Telephone'),
    ('Helicopter', -1, 0, ''),
    ('Applause', -1, 0, ''),
    ('Gunshot', 0, 0, ''),
    ('Percussion', -1, 0, ''),
)

DRUM_INFO = (
    None, None, None, None, None,
    None, None, None, None, None,
    None, None, None, None, None,
    None, None, None, None, None,
    None, None, None, None,
    ('Zap', -1, 0),
    ('Brush hit hard', -1, 0),
    ('Brush circle', -1, 0),
    ('Brush hit soft', -1, 0),
    ('Brush hit and circle', -1, 0),
    ('Drumroll', -1, 0),
    ('Castanets', -1, 0),
    ('Snare Drum 3', -1, 0),
    ('Drumsticks hitting', -1, 0),
    ('Bass Drum 3', -1, 0),
    ('Hard hit snare', -1, 0),
    ('Bass Drum 2', 2, 10),
    ('Bass Drum 1', 2, 6),
    ('Side Stick', 4, 6),
    ('Snare Drum 1', 3, 8),
    ('Hand Clap', 4, 6),
    ('Snare Drum 2', 3, 4),
    ('Low Tom 2', 2, 6),
    ('Closed Hi - hat', 3, 22),
    ('Low Tom 1', 2, 13),
    ('Pedal Hi - hat', 3, 22),
    ('Mid Tom 2', 2, 15),
    ('Open Hi - hat', 3, 18),
    ('Mid Tom 1', 2, 20),
    ('High Tom 2', 2, 23),
    ('Crash Cymbal 1', 3, 17),
    ('High Tom 1', 2, 23),
    ('Ride Cymbal 1', 3, 24),
    ('Chinese Cymbal', 3, 8),
    ('Ride Bell', 3, 13),
    ('Tambourine', 4, 18),
    ('Splash Cymbal', 3, 18),
    ('Cowbell', 4, 1),
    ('Crash Cymbal 2', 3, 13),
    ('Vibra Slap', 4, 2),
    ('Ride Cymbal 2', 3, 13),
    ('High Bongo', 4, 9),
    ('Low Bongo', 4, 2),
    ('Mute High Conga', 4, 8),
    ('Open High Conga', 2, 22),
    ('Low Conga', 2, 15),
    ('High Timbale', 3, 13),
    ('Low Timbale', 3, 8),
    ('High Agog�', 4, 8),
    ('Low Agog�', 4, 3),
    ('Cabasa', 4, 20),
    ('Maracas', 4, 23),
    ('Short Whistle', -1, 0),
    ('Long Whistle', -1, 0),
    ('Short G�iro', 4, 17),
    ('Long G�iro', 4, 11),
    ('Claves', 4, 18),
    ('High Wood Block', 4, 9),
    ('Low Wood Block', 4, 5),
    ('Mute Cu�ca', -1, 0),
    ('Open Cu�ca', -1, 0),
    ('Mute Triangle', 4, 17),
    ('Open Triangle', 4, 22),
    ('Shaker', 3, 22),
    ('Jingle bell', -1, 0),
    ('Bell tree', -1, 0),
    ('Castanets', 4, 21),
    ('Mute Surdo', 2, 14),
    ('Open Surdo', 2, 7),
)

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

MAX_TEMPO = 30

@lru_cache
def fraction2length(fraction: str) -> int:
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
        and tuning). None if the conversation fails.
    """

    if autoExpand:
        expandMultiplier = 1

    # Reads the input file

    xml: etree.ElementTree = None
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
    elif filepath.endswith(".mscx"):
        xml = etree.parse(filepath, parser=None)

    if xml is None:
        return None
    if version := xml.findtext('programVersion'):
        if version.startswith('2.'):
            raise NotImplementedError("MuseScore 2 files are not supported. Please use MuseScore 3 to re-save the files before importing.")

    nbs: NbsSong = NbsSong()

    # Get meta-information

    header: Dict = nbs.header
    score: etree.Element = xml.find("Score")
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
        isPerc = bool(part.xpath("Instrument[@id='drumset']")) or bool(part.xpath("Staff/StaffType[@group='percussion']"))
        program = int(part.find("Instrument/Channel/program").get("value"))
        for staff in part.iterfind("Staff"):
            staffId = int(staff.get("id"))
            if staffId not in emptyStaffs:
                # INST_INFO[-1] is the percussion (drumset) instrument
                staffInsts[staffId] = INST_INFO[program] if not isPerc else INST_INFO[-1]

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
                                nbs.layers.append(Dict({'name': "{} (v. {})".format(staffInsts[staffId][0], voi+1), 'lock':False, 'volume':100, 'stereo':100}))
                            inst = staffInst
                            isPerc = False
                            if inst > -1:
                                key = int(note.find("pitch").text) - 21
                            else:
                                drumIndex = int(note.find("pitch").text)
                                if drumIndex > 23: # Vrevent access to None values in DRUM_INFO
                                    _, inst, key = DRUM_INFO[drumIndex if drumIndex < len(DRUM_INFO) else 24]
                                    key += 36
                                    isPerc = True
                                    if inst == -1: inst = 0
                            tuning = note.find("tuning")
                            pitch = int(float(tuning.text)) if tuning is not None else 0
                            # TODO: Support relative velocity
                            vel = max(min(int(note.findtext("velocity") or 100), 127), 0)
                            nbs.notes.append(Dict({'tick': int(tick), 'layer': layer, 'inst': inst,
                                                'key': key, 'vel': vel, 'pan': 100, 'pitch': pitch, 'isPerc': isPerc}))
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

if __name__ == '__main__':
    # filepath = "sayonara_30_seconds.mscx"
    # filepath = "chord.mscx"
    # filepath = "Vì_yêu_cứ_đâm_đầu.mscx"
    # filepath = "Ai_yêu_Bác_Hồ_Chí_Minh.mscz"
    # filepath = "test.mscx"
    # filepath = "test_microtones.mscx"
    # filepath = "Shining_in_the_Sky.mscx"
    # filepath = "voices.mscx"
    # filepath = "AYBHCM_1_2.mscx"
    # filepath = "inst.mscx"
    # filepath = "Chay ngay di.mscx"
    # filepath = "1note.mscx"
    # filepath = "Ai_đưa_em_về_-_Nguyễn_Ánh_9_-_Phiên_bản_dễ_(Easy_version).mscx"
    # filepath = 'halfTempo.mscx'
    filepath = "A_Tender_Feeling_(Sword_Art_Online).mscz"
    nbs = musescore2nbs(filepath, autoExpand=False)
    print(nbs)
    nbs.write(filepath.rsplit('.', 1)[0] + '.nbs')
