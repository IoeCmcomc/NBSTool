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


from collections.abc import Iterable
from struct import Struct
from typing import BinaryIO, Optional
from math import ceil
from enum import Enum, Flag, IntFlag, auto
from pprint import pprint
from itertools import groupby
from dataclasses import dataclass, asdict
from functools import total_ordering
from os import path
from asyncio import sleep
from warnings import warn

from pydub import AudioSegment
from pydub.effects import normalize

from nbsio import Note as NbsNote
from nbsio import NbsSong, Layer, Instrument, VANILLA_INSTS

from common import SOUND_FOLDER
from audio_common import load_sound


DEFAULT_PATTERN_LENGTH = 64
TRACKER_VERSION = 0xa00a
SAMPLE_PITCH_SHIFT = -10
LAST_SAMPLE_PITCH_SHIFT = 6  # The last need special treatment
DEFAULT_SPEED = 6
MAX_LENGTH = 40000
MAX_CHANNEL = 127

BYTE = Struct("<b")
UBYTE = Struct("<B")
SHORT = Struct("<h")
USHORT = Struct("<H")
UINT = Struct("<I")


@dataclass
@total_ordering
class Note(NbsNote):
    tick_in_pattern: int = -1

    # Adapted from: https://stackoverflow.com/a/55065215/12682038
    @classmethod
    def from_instance(cls, instance, pattern_length):
        return cls(**asdict(instance), tick_in_pattern=instance.tick % pattern_length)


class HeaderFlag(Flag):
    NONE = 0
    STEREO = auto()
    MIXING = auto()
    USE_INSTRUMENTS = auto()
    LINEAR_SLIDES = auto()
    OLD_EFFECTS = auto()
    LINK_G_MEMORIES_WITH_E_F_EFFECTS = auto()
    MIDI_PITCH_CONTROLLER = auto()
    REQUEST_MIDI_MACROS = auto()
    DEFAULT = STEREO | USE_INSTRUMENTS | LINEAR_SLIDES | MIDI_PITCH_CONTROLLER


class HeaderSpecial(Flag):
    NONE = 0
    ATTACH_SONG_MESSAGES = auto()
    EMBED_EDIT_HISTORY = auto()
    EMBED_HIGHLIGHT = auto()
    EMBED_MIDI_MACRO = auto()
    # EMBED_EDIT_HISTORY is set with offset 0 to ensure compatibility
    DEFAULT = EMBED_EDIT_HISTORY | EMBED_HIGHLIGHT


class NewNoteAction(Enum):
    NOTE_CUT = 0
    CONTINUE = auto()
    NOTE_OFF = auto()
    NOTE_FADE = auto()
    DEFAULT = CONTINUE


class DuplicateCheckType(Enum):
    OFF = 0
    Note = auto()
    Sample = auto()
    Instrument = auto()
    DEFAULT = OFF


class DuplicateCheckAction(Enum):
    CUT = 0
    NOTE_OFF = auto()
    NOTE_FADE = auto()
    DEFAULT = CUT


class EnvelopeFlag(Flag):
    NONE = 0
    ENVELOPE_ON = auto()
    LOOP_ON = auto()
    DEFAULT = NONE


class SampleFlag(Flag):
    NONE = 0
    SAMPLE_ASSOC_WITH_HEADER = auto()
    IS_16_BIT = auto()
    STEREO = auto()
    COMPRESSED = auto()
    LOOP_ON = auto()
    SUSTAIN_ON = auto()
    PING_PONG_LOOP = auto()
    PING_PONG_SUSTAIN = auto()
    DEFAULT = SAMPLE_ASSOC_WITH_HEADER | IS_16_BIT


class SampleConvertFlag(Flag):
    NONE = 0
    SIGNED_DATA = auto()
    BIG_ENDIAN = auto()
    DELTA_ENCODED = auto()
    BYTE_DELTA = auto()
    TX_WAVE_VALUES = auto()
    PROMPT_LEFT_RIGHT_STEREO = auto()
    DEFAULT = SIGNED_DATA


class ChannelMask(IntFlag):
    NONE = 0
    HAS_NOTE_KEY = auto()
    HAS_INSTRUMENT = auto()
    HAS_VOLUME_PAN = auto()
    HAS_COMMAND = auto()
    USE_LAST_NOTE_KEY = auto()
    USE_LAST_INSTRUMENT = auto()
    USE_LAST_VOLUME_PAN = auto()
    USE_LAST_COMMAND = auto()
    DEFAULT = HAS_NOTE_KEY | HAS_INSTRUMENT | HAS_VOLUME_PAN | HAS_COMMAND


@dataclass
class Channel(Layer):
    last_mask: ChannelMask = ChannelMask.NONE
    last_volume_value: int = -1
    last_effect: int = -1
    last_effect_value: int = -1
    last_note: Note = Note()

    @classmethod
    def from_instance(cls, instance):
        return cls(**asdict(instance))

    def reset_info(self) -> None:
        self.last_mask = ChannelMask.NONE
        self.last_volume_value = -1
        self.last_effect = -1
        self.last_effect_value = -1
        self.last_note = Note()


def write_numeric(f: BinaryIO, fmt: Struct, v) -> None:
    f.write(fmt.pack(v))


def to_bytes(string: str) -> bytes:
    return string.encode("ascii")


def name_to_bytes(string: str, max_length: int = 26) -> bytes:
    return to_bytes(string.ljust(max_length, '\0')[:max_length])


def null_bytes(count: int) -> bytes:
    return to_bytes('\0' * count)


def key_to_pitch(key: int) -> float:
    return 2 ** ((key) / 12)


def write_curr_pos_to(f, offset: int):
    pos = f.tell()
    f.seek(offset)
    f.write(UINT.pack(pos))
    f.seek(pos)


def groupby_with_empty(iterable: Iterable, f, start=0, stop: Optional[int] = None):
    last_i = start - 1
    for i, v in groupby(iterable, f):
        while last_i + 1 < i:
            last_i += 1
            yield last_i, {}
        yield i, v
        last_i = i
    if isinstance(stop, int):
        while last_i < stop-1:
            last_i += 1
            yield last_i, {}


def get_audio_segment(file_name: str) -> Optional[AudioSegment]:
    try:
        return load_sound(path.join(SOUND_FOLDER, file_name) if file_name else '')
    except FileNotFoundError:
        return None


DUMMY_INSTRUMENT = Instrument('', '', 0, False)


def delete_missing_instruments(song: NbsSong, insts: list):
    missing_indexes = set()
    for i in reversed(range(len(insts))):
        inst = insts[i]
        if not inst.filePath or get_audio_segment(inst.filePath) is None:
            warn(f"Missing instrument: {inst.filePath}")
            missing_indexes.add(i)
            del insts[i]

    song.notes = list(
        filter(lambda note: note.inst not in missing_indexes, song.notes))

    customInsts = song.customInsts
    for i in reversed(range(len(customInsts))):
        if i in missing_indexes:
            del customInsts[i]

    song.correctData()


# ________________________________________________________________________________
# MAIN FUNCTION
# ________________________________________________________________________________
async def nbs2it(song: NbsSong, fn: str, dialog=None) -> None:
    song.correctData()
    header = song.header

    if not fn.endswith('.it'):
        fn += '.it'

    song.notes = list(
        filter(lambda note: note.tick < MAX_LENGTH and note.layer < MAX_CHANNEL, song.notes))
    song.correctData()
    layers = song.layers

    all_instruments = VANILLA_INSTS[:header.vani_inst] + song.customInsts
    delete_missing_instruments(song, all_instruments)

    instrument_indexes = sorted([*song.usedInsts[0], *song.usedInsts[1]])

    instruments = [all_instruments[index] for index in instrument_indexes]
    instruments.append(Instrument('', '', 0, False))

    if instrument_indexes:
        dummy_index = instrument_indexes[-1] + 1
        instrument_indexes.append(dummy_index)
        song.notes.append(NbsNote(0, song.maxLayer+1, dummy_index, 0, 0))
        song.correctData()

    instrument_mapping = {index: i for i,
                          index in enumerate(instrument_indexes)}
    instrument_count = len(instruments)

    pattern_length = DEFAULT_PATTERN_LENGTH
    pattern_count = ceil(header.length / pattern_length)
    while pattern_count > 200 and pattern_length <= 200:
        pattern_length += 16
        pattern_count = ceil(header.length / pattern_length)

    order_count = pattern_count + 1
    time_sign = 4
    tempo = int(header.tempo * 60 / time_sign)  # BPM
    speed = DEFAULT_SPEED
    while tempo > 255 and speed > 1:
        next_speed = speed - 1
        tempo = tempo * next_speed // speed
        speed = next_speed
    if tempo < 32:
        tempo *= 2
        speed *= 2

    samples: list[AudioSegment] = []
    sample_offset_positions: list[int] = []

    if dialog:
        dialog.currentProgress.set(20)  # 20%
        await sleep(0.001)

    for instrument in instruments:
        # AudioSegment objects are immutable
        sample = get_audio_segment(instrument.filePath)
        assert sample is not None
        # Convert to 16-bit mono audio
        sample = sample.set_channels(1).set_sample_width(2)
        sample = normalize(sample)
        # sample = change_speed(sample, key_to_pitch(instrument.pitch + SAMPLE_PITCH_SHIFT))
        samples.append(sample)

    if dialog:
        dialog.currentProgress.set(25)
        await sleep(0.001)

    with open(fn, "wb") as f:
        f.write(to_bytes("IMPM"))  # Header code
        f.write(name_to_bytes(header.name))  # Song name
        f.write(UBYTE.pack(8))  # Rows per beat
        f.write(UBYTE.pack(16))  # Rows per measure
        f.write(USHORT.pack(order_count))  # Number of sequenced patterns
        f.write(USHORT.pack(instrument_count))  # Number of instruments
        f.write(USHORT.pack(instrument_count))  # Number of samples
        f.write(USHORT.pack(pattern_count))  # Number of patterns
        f.write(USHORT.pack(TRACKER_VERSION))  # Tracker version ID
        f.write(USHORT.pack(0x0214))  # Compatible tracker version ID
        f.write(USHORT.pack(HeaderFlag.DEFAULT.value))  # Flags
        f.write(USHORT.pack(HeaderSpecial.DEFAULT.value))  # Special
        f.write(UBYTE.pack(96))  # Global volume
        f.write(UBYTE.pack(48))  # Mixing volume
        f.write(UBYTE.pack(speed))  # Initial speed
        f.write(UBYTE.pack(tempo))  # Initial tempo
        f.write(UBYTE.pack(128))  # Pan separation
        f.write(UBYTE.pack(2))  # Pitch wheel depth
        f.write(USHORT.pack(0))  # Attatched message length
        f.write(UINT.pack(0))  # Attatched message offset
        f.write(UINT.pack(0))  # Reserved

        dummy_layer = Layer("")
        initial_layers = [*layers]
        if len(initial_layers) < 64:
            for _ in range(64-len(initial_layers)):
                initial_layers.append(dummy_layer)
        for layer in initial_layers[:64]:
            layer_pan = int((layer.pan + 100) * 32 / 100)
            f.write(UBYTE.pack(layer_pan))  # Initial channel pan
        for layer in initial_layers[:64]:
            layer_vol = int(layer.volume * 64 / 100)
            f.write(UBYTE.pack(layer_vol))  # Initial channel pan

        for i in range(pattern_count):
            f.write(UBYTE.pack(i))  # Pattern order
        f.write(UBYTE.pack(255))  # Song end

        # Skip offsets, set these offsets later
        f.seek(instrument_count * 4, 1)
        f.seek(instrument_count * 4, 1)
        for _ in range(pattern_count):
            f.write(UINT.pack(0xca))

        if dialog:
            dialog.currentProgress.set(30)
            await sleep(0.001)

        channel_names = tuple(layer.name for layer in layers)
        if any(channel_names):  # Channel names
            f.write(to_bytes("CNAM"))
            f.write(UINT.pack(len(channel_names) * 20))
            for name in channel_names:
                f.write(name_to_bytes(name, 20))

        for i, instrument in enumerate(instruments):  # Instruments
            write_curr_pos_to(f, 0x00C0 + order_count + i * 4)

            f.write(to_bytes("IMPI"))
            f.write(null_bytes(12))  # DOS file name
            f.write(UBYTE.pack(0))  # Reserved
            f.write(UBYTE.pack(NewNoteAction.DEFAULT.value))  # New note action
            # Duplicate check type
            f.write(UBYTE.pack(DuplicateCheckType.DEFAULT.value))
            # Duplicate check action
            f.write(UBYTE.pack(DuplicateCheckAction.DEFAULT.value))
            f.write(SHORT.pack(8))  # Fade out
            f.write(BYTE.pack(0))  # Pitch pan separation
            f.write(UBYTE.pack(54))  # Pitch pan center
            f.write(UBYTE.pack(128))  # Global volume
            f.write(UBYTE.pack(32))  # Default pan
            f.write(UBYTE.pack(0))  # Random volume percentage
            f.write(UBYTE.pack(0))  # Random pan percentage
            f.write(USHORT.pack(TRACKER_VERSION))  # Tracker version ID
            f.write(UBYTE.pack(1))  # Number of samples
            f.write(UBYTE.pack(0))  # Reserved
            f.write(name_to_bytes(instrument.name))  # Instrument name
            f.write(BYTE.pack(0))  # Initial filter cutoff
            f.write(BYTE.pack(0))  # Initial filter resonance
            f.write(BYTE.pack(0))  # MIDI channel
            f.write(BYTE.pack(0))  # MIDI program
            f.write(USHORT.pack(0))  # MIDI bank
            for j in range(120):
                f.write(UBYTE.pack(j))
                f.write(UBYTE.pack(i + 1))

            for _ in range(3):  # Envelopes
                # Envelope flags
                f.write(UBYTE.pack(EnvelopeFlag.DEFAULT.value))
                f.write(UBYTE.pack(0))  # Valid node count
                f.write(UBYTE.pack(0))  # Loop begin
                f.write(UBYTE.pack(0))  # Loop end
                f.write(UBYTE.pack(0))  # Sustain loop begin
                f.write(UBYTE.pack(0))  # Sustain loop end
                if _ == 2:
                    f.write(null_bytes(4))  # Trailing bytes

        if dialog:
            dialog.currentProgress.set(50)
            await sleep(0.001)

        for i, (instrument, sample) in enumerate(zip(instruments, samples)):  # Samples
            write_curr_pos_to(f, 0x00C0 + order_count +
                              instrument_count * 4 + i * 4)

            f.write(to_bytes("IMPS"))
            f.write(null_bytes(12))  # DOS file name
            f.write(UBYTE.pack(0))  # Reserved
            f.write(UBYTE.pack(64))  # Global volume
            f.write(UBYTE.pack(SampleFlag.DEFAULT.value))  # Flags
            f.write(UBYTE.pack(64))  # Default volume
            f.write(name_to_bytes(instrument.sound_id))  # Sample name
            # Conversion flags
            f.write(UBYTE.pack(SampleConvertFlag.DEFAULT.value))
            f.write(UBYTE.pack(32))  # Default volume (set bit 7 to enable)
            f.write(UINT.pack(int(sample.frame_count())))  # Sample length
            f.write(UINT.pack(0))  # Loop begin
            f.write(UINT.pack(0))  # Loop end
            # semitones_to_shift = LAST_SAMPLE_PITCH_SHIFT if i + \
            #     1 == instrument_count else SAMPLE_PITCH_SHIFT
            semitones_to_shift = SAMPLE_PITCH_SHIFT
            semitones_to_shift += instrument.pitch
            c5_speed = int(sample.frame_rate *
                           key_to_pitch(semitones_to_shift))
            f.write(UINT.pack(c5_speed))  # C5 speed (sample rate)
            f.write(UINT.pack(0))  # Sustain loop begin
            f.write(UINT.pack(0))  # Sustain loop end
            sample_offset_positions.append(f.tell())
            f.write(UINT.pack(0))  # Sample pointer/offset (skip for now)
            f.write(UBYTE.pack(0))  # Vibrato speed
            f.write(UBYTE.pack(0))  # Vibrato depth
            f.write(UBYTE.pack(0))  # Vibrato waveform type
            f.write(UBYTE.pack(0))  # Vibrato sweep rate

        if dialog:
            dialog.currentProgress.set(60)
            await sleep(0.001)

        channels = list(map(Channel.from_instance, layers))
        dummy_channel = Channel("")
        if len(channels) < song.maxLayer + 1:
            for _ in range(song.maxLayer + 1 - len(channels)):
                channels.append(dummy_channel)

        def note_converter(note): return Note.from_instance(
            note, pattern_length)
        notes_by_pattern = groupby_with_empty(
            map(note_converter, song.notes),
            lambda x: x.tick // pattern_length)
        notes_by_pattern = tuple((i, tuple(notes))
                                 for i, notes in notes_by_pattern)
        for i, pattern_notes in notes_by_pattern:
            write_curr_pos_to(f, 0x00C0 + order_count +
                              instrument_count * 4 + instrument_count * 4 + i * 4)
            pattern_offset_pos = f.tell()
            # Pattern data's length, not including first 8 bytes
            f.write(USHORT.pack(0))
            f.write(USHORT.pack(pattern_length))  # Row count
            # f.write(null_bytes(4))  # Reserved
            f.write(to_bytes("hehe"))  # Reserved
            pattern_start = f.tell()

            notes_by_row = groupby_with_empty(
                pattern_notes, lambda x: x.tick_in_pattern, 0, pattern_length)
            for k, notes in notes_by_row:
                # notes = tuple(notes)
                for note in notes:
                    note: Note
                    channel = channels[note.layer]
                    last_note = channel.last_note

                    has_volume = False
                    has_pan = False
                    has_finetune = False
                    volume_value = int(note.vel * 64 / 100)
                    if note.vel != last_note.vel:
                        has_volume = True
                    elif note.pan != last_note.pan:
                        pan = (note.pan + layers[note.layer].pan) / 2
                        volume_value = int((pan + 100) * 64 // 200) + 128
                        has_pan = True

                    effect = 0
                    effect_value = 0
                    if not has_pan and note.pan != last_note.pan:
                        effect = ord('X') - 64
                        pan = (note.pan + layers[note.layer].pan) / 2
                        effect_value = int((pan + 100) * 255 // 200)
                    elif note.pitch != last_note.pitch and 0 < abs(note.pitch) < 224:
                        effect = ord('E' if note.pitch < 0 else 'F') - 64
                        effect_value = int(round(abs(note.pitch) / 100 * 16))
                        if effect_value > 0:
                            has_finetune = True
                        else:
                            effect = 0

                    mask = ChannelMask.NONE
                    if channel.last_mask == ChannelMask.NONE:
                        mask = ChannelMask.DEFAULT
                    else:
                        if note.key == last_note.key:
                            mask |= ChannelMask.USE_LAST_NOTE_KEY
                        else:
                            mask |= ChannelMask.HAS_NOTE_KEY

                        if note.inst == last_note.inst:
                            mask |= ChannelMask.USE_LAST_INSTRUMENT
                        else:
                            mask |= ChannelMask.HAS_INSTRUMENT

                        if volume_value == channel.last_volume_value:
                            mask |= ChannelMask.USE_LAST_VOLUME_PAN
                        else:
                            mask |= ChannelMask.HAS_VOLUME_PAN

                        if effect == channel.last_effect and effect_value == channel.last_effect_value:
                            mask |= ChannelMask.USE_LAST_COMMAND
                        else:
                            mask |= ChannelMask.HAS_COMMAND

                    reuse_mask = mask == channel.last_mask
                    channel_var = note.layer + 1
                    if not reuse_mask:
                        channel_var |= 128  # 128: Next byte is mask
                    f.write(UBYTE.pack(channel_var))  # Channel value and flags
                    # Channel note flags
                    if not reuse_mask:
                        # print(f"{mask=}, {int(mask)=:b}")
                        f.write(UBYTE.pack(int(mask)))
                    # Note key
                    if mask & ChannelMask.HAS_NOTE_KEY:
                        # print(f"{note.key+9=}")
                        f.write(UBYTE.pack(note.key + 9))
                    # Note instrument
                    if mask & ChannelMask.HAS_INSTRUMENT:
                        # print(f"{instrument_mapping[note.inst]+1=}")
                        f.write(UBYTE.pack(instrument_mapping[note.inst] + 1))
                    # Note volume
                    if mask & ChannelMask.HAS_VOLUME_PAN:
                        # print(f"{volume_value=}")
                        f.write(UBYTE.pack(volume_value))
                    # Note effect
                    if mask & ChannelMask.HAS_COMMAND:
                        # print(f"{effect=}, {effect_value=}")
                        f.write(UBYTE.pack(effect))  # panning
                        f.write(UBYTE.pack(effect_value))

                    channel.last_note = note
                    channel.last_volume_value = volume_value
                    channel.last_effect = effect
                    channel.last_effect_value = effect_value
                    channel.last_mask = mask

                f.write(UBYTE.pack(0))  # End of row

            for channel in channels:
                channel.reset_info()

            pos = f.tell()
            f.seek(pattern_offset_pos)
            f.write(USHORT.pack(pos - pattern_start))
            f.seek(pos)

        if dialog:
            dialog.currentProgress.set(90)
            await sleep(0.001)

        for i, sample in enumerate(samples):  # Sample audio data
            write_curr_pos_to(f, sample_offset_positions[i])

            assert sample.raw_data is not None
            f.write(sample.raw_data)


if __name__ == "__main__":
    base_name = "Note_Block_Megacollab"

    song: NbsSong = NbsSong(base_name + ".nbs")
    a = nbs2it(song, base_name + ".it")
