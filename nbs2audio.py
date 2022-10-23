from asyncio import sleep
from os import environ
from typing import Optional, Sequence

from pynbs import File, Header, Note, Layer, Instrument

from common import resource_path
environ["PATH"] += resource_path('ffmpeg', 'bin')

from nbswave import audio, nbs, SongRenderer
from nbswave.main import MissingInstrumentException

from nbsio import VANILLA_INSTS, NbsSong

SOUND_FOLDER = resource_path('sounds')

def convert(data: NbsSong) -> File:
    oldHeader = data.header
    header = Header(
        version=oldHeader.file_version,
        default_instruments=oldHeader.vani_inst,
        song_length=oldHeader.length,
        song_layers=oldHeader.height,
        song_name=oldHeader.name,
        song_author=oldHeader.author,
        original_author=oldHeader.orig_author,
        description=oldHeader.description,
        auto_save=oldHeader.auto_save,
        auto_save_duration=oldHeader.auto_save_time,
        tempo=oldHeader.tempo,
        time_signature=oldHeader.time_sign,
        minutes_spent=oldHeader.minutes_spent,
        left_clicks=oldHeader.left_clicks,
        right_clicks=oldHeader.right_clicks,
        blocks_added=oldHeader.block_added,
        blocks_removed=oldHeader.block_removed,
        song_origin=oldHeader.import_name,
        loop=oldHeader.loop,
        max_loop_count=oldHeader.loop_max,
        loop_start=oldHeader.loop_start
    )

    notes = [Note(tick=note.tick, layer=note.layer, instrument=note.inst, key=note.key,
                  velocity=note.vel, panning=note.pan, pitch=note.pitch) for note in data.notes]

    layers = [Layer(id=i, name=layer.name, lock=layer.lock, volume=layer.volume,
                    panning=layer.pan) for i, layer in enumerate(data.layers)]

    instruments = [Instrument(id=i, name=inst.name, file=inst.filePath, pitch=inst.pitch,
                              press_key=inst.pressKeys) for i, inst in enumerate(VANILLA_INSTS + data.customInsts)]

    return File(header, notes, layers, instruments)

class Renderer(SongRenderer):
    def __init__(self, song, dialog):
        super().__init__(song, SOUND_FOLDER)
        self.dialog = dialog

    async def mix_song(
        self,
        ignore_missing_instruments=False,
        exclude_locked_layers=False,
        **kwargs,
    ):
        if exclude_locked_layers:
            notes_to_mix = list(self._song.get_unlocked_notes())
        else:
            notes_to_mix = list(self._song.weighted_notes())

        mixed = await self._mix(
            notes_to_mix,
            ignore_missing_instruments=ignore_missing_instruments,
            **kwargs,
        )
        return mixed

    async def _mix(
        self,
        notes: Sequence[nbs.Note],
        ignore_missing_instruments: bool = False,
        sample_rate: Optional[int] = 44100,
        channels: Optional[int] = 2,
        bit_depth: Optional[int] = 16,
    ) -> audio.Track:

        track_length = self.get_length(self._song.weighted_notes())  # type: ignore

        assert bit_depth is not None
        mixer = audio.Mixer(
            sample_width=bit_depth // 8,
            frame_rate=sample_rate,
            channels=channels,
            length=track_length,
        )

        sorted_notes = nbs.sorted_notes(notes)

        last_ins = None
        last_key = None
        last_vol = None
        last_pan = None

        note_count = len(sorted_notes)
        sound = sound1 = sound2 = sound3 = None
        for i, note in enumerate(sorted_notes):

            ins = note.instrument
            key = note.key
            vol = note.velocity
            pan = note.panning

            if ins != last_ins:
                last_key = None
                last_vol = None
                last_pan = None

                try:
                    sound1 = self._instruments[note.instrument]
                except KeyError:  # Sound file missing
                    if not ignore_missing_instruments:
                        custom_ins_id = ins - self._song.header.default_instruments
                        instrument_data = self._song.instruments[custom_ins_id]
                        ins_name = instrument_data.name
                        ins_file = instrument_data.file
                        raise MissingInstrumentException(
                            f"The sound file for instrument {ins_name} was not found: {ins_file}"
                        )
                    else:
                        continue

                if sound1 is None:  # Sound file not assigned
                    continue

                sound1 = audio.sync(sound1)

            assert sound1 is not None
            if key != last_key:
                last_vol = None
                last_pan = None
                pitch = audio.key_to_pitch(key)
                sound2 = audio.change_speed(sound1, pitch)

            assert sound2 is not None
            if vol != last_vol:
                last_pan = None
                gain = audio.vol_to_gain(vol)
                sound3 = sound2.apply_gain(gain)
            
            if pan != last_pan:
                sound4 = sound3.pan(pan)  # type: ignore
                sound = sound4

            last_ins = ins
            last_key = key
            last_vol = vol
            last_pan = pan

            pos = note.tick / self._song.header.tempo * 1000

            mixer.overlay(sound, position=pos)

            if self.dialog:
                newPercent = 30 + i * 50 / note_count
                if newPercent - self.dialog.currentProgress.get() >= 0.5:
                    self.dialog.currentProgress.set(newPercent)
                    await sleep(0.001)

        return mixer.to_audio_segment()

async def nbs2audio(data: NbsSong, filepath: str, dialog=None,
    format: str = 'wav',
    sample_rate: int = 44100,
    channels: int = 2,
    bit_depth: int = 16,
    target_bitrate: int = 320,
    target_size = None,
    ignore_missing_instruments: bool = False,
    exclude_locked_layers: bool = False,
) -> None:

    renderer = Renderer(convert(data), dialog)

    if (not ignore_missing_instruments) and (missingInsts := renderer.missing_instruments()):
        instFiles = '\n'.join(inst.file for inst in missingInsts)
        raise MissingInstrumentException(
            f"The following sound files are missing in the sounds/ folder:\n{instFiles}")

    if dialog:
        dialog.currentProgress.set(20) # 20%
        await sleep(0.001)
    
    renderer.load_instruments(SOUND_FOLDER)
    
    if dialog:
        dialog.currentProgress.set(30) # 30%
        await sleep(0.001)

    track = await renderer.mix_song(
        ignore_missing_instruments,
        exclude_locked_layers,
        sample_rate=sample_rate,
        bit_depth=bit_depth,
        channels=channels,
    )
    
    if dialog:
        dialog.currentProgress.set(80) # 80%
        await sleep(0.001)

    track.save(
        filepath,
        format,
        bit_depth // 8,
        sample_rate,
        channels,
        target_bitrate,
        target_size,
    )

    if dialog:
            dialog.currentProgress.set(90) # 90%
            await sleep(0.001)
