"""
Playback and listening-history tracking for the recommender.

This lives outside recommender.py because it deals with actual audio I/O
and persisted play history (data/plays.json), not scoring/ranking logic.

Why PyAudio: it's a thin Python binding over PortAudio, giving direct
access to a raw output stream (open -> write PCM samples -> close) instead
of shelling out to an OS media player. That's what we need here since this
simulation has no real audio files to hand off - `play_song` synthesizes a
short tone in memory and writes it straight to the stream. A higher-level
helper like `playsound` only knows how to play an existing file path and
doesn't expose that raw buffer control.
"""

import json
import math
import os
import struct
from typing import Dict

from .recommender import load_songs

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SONGS_CSV = os.path.join(DATA_DIR, "songs.csv")
PLAYS_PATH = os.path.join(DATA_DIR, "plays.json")


def load_song_request(song_id: int, csv_path: str = SONGS_CSV) -> Dict:
    """
    Looks up a song by id in songs.csv (acting as our song "db") and
    returns a small JSON-serializable request payload naming what to play.
    """
    for song in load_songs(csv_path):
        if song["id"] == song_id:
            return {"id": song["id"], "artist": song["artist"], "title": song["title"]}
    raise ValueError(f"No song with id {song_id} in {csv_path}")


def _load_plays(plays_path: str = PLAYS_PATH) -> Dict:
    if not os.path.exists(plays_path):
        return {}
    with open(plays_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_plays(plays: Dict, plays_path: str = PLAYS_PATH) -> None:
    os.makedirs(os.path.dirname(plays_path), exist_ok=True)
    with open(plays_path, "w", encoding="utf-8") as f:
        json.dump(plays, f, indent=2)


def record_play(user: str, song_id: int, plays_path: str = PLAYS_PATH) -> int:
    """
    Marks a song as "touched" by a user and bumps its play count in
    data/plays.json. Returns the song's new play count for that user.
    """
    plays = _load_plays(plays_path)
    user_plays = plays.setdefault(user, {})
    song_key = str(song_id)
    user_plays[song_key] = user_plays.get(song_key, 0) + 1
    _save_plays(plays, plays_path)
    return user_plays[song_key]


def play_score(user: str, song_id: int, plays_path: str = PLAYS_PATH, cap: int = 5) -> float:
    """
    Converts a user's raw play count for a song into a 0-1 familiarity
    score. Capped at `cap` plays so a heavily-replayed song saturates the
    signal instead of dominating every future recommendation score.
    """
    plays = _load_plays(plays_path)
    count = plays.get(user, {}).get(str(song_id), 0)
    return min(count, cap) / cap


def play_song(song_request: Dict, user: str = "default", duration: float = 0.5) -> None:
    """
    "Plays" a song through the system's audio output via PyAudio, then
    records the play so it counts toward that user's play score.
    """
    import pyaudio

    sample_rate = 44100
    frequency = 440.0
    frame_count = int(sample_rate * duration)
    samples = [
        int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(frame_count)
    ]
    audio_bytes = struct.pack("<" + "h" * frame_count, *samples)

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
    try:
        print(f"Playing: {song_request['title']} - {song_request['artist']}")
        stream.write(audio_bytes)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    record_play(user, song_request["id"])
