from functools import lru_cache

from pydub import AudioSegment


@lru_cache(maxsize=32)
def load_sound(path: str) -> AudioSegment:
    """A patched version of nbswave.audio.load_song() which caches loaded sounds"""
    if not path:
        return AudioSegment.empty()
    else:
        return AudioSegment.from_file(path)
