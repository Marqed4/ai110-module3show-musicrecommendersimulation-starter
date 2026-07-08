from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    numeric_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in numeric_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

# Point-based Algorithm Recipe. Genre is worth roughly double mood and
# double the max energy award so a genre match dominates the score, and a
# genre mismatch is only forgiven when the song is an extremely close
# energy match (near-identical vibe) - this keeps recommendations on-topic.
GENRE_MATCH_POINTS = 2.0
GENRE_MISMATCH_PENALTY = -1.0
GENRE_MISMATCH_CLOSE_ENERGY_POINTS = 0.5
GENRE_MISMATCH_ENERGY_THRESHOLD = 0.05
MOOD_MATCH_POINTS = 1.0
ENERGY_MAX_POINTS = 1.0
ACOUSTIC_MATCH_POINTS = 0.5

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Algorithm Recipe:
      - Genre match:        +2.0 pts
      - Genre mismatch:     -1.0 pt, UNLESS the song's energy is within
                             0.05 of the user's target energy, in which
                             case it earns +0.5 pts instead (an on-vibe
                             exception, not a full genre swap)
      - Mood match:          +1.0 pt
      - Energy closeness:    up to +1.0 pt, scaled by 1 - |diff|, so a
                             perfect energy match earns the full point
                             and it decays linearly as the gap grows
      - Acoustic preference: +0.5 pts when likes_acoustic agrees with
                             whether the song's acousticness >= 0.5
    """
    reasons: List[str] = []
    score = 0.0

    user_genre = user_prefs.get("genre")
    user_mood = user_prefs.get("mood")
    user_energy = user_prefs.get("energy", 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic")

    energy_diff = abs(song["energy"] - user_energy)

    if song["genre"] == user_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match ({song['genre']}) (+{GENRE_MATCH_POINTS:.1f})")
    elif energy_diff <= GENRE_MISMATCH_ENERGY_THRESHOLD:
        # Only step outside the user's genre when the energy match is nearly identical.
        score += GENRE_MISMATCH_CLOSE_ENERGY_POINTS
        reasons.append(
            f"outside your usual {user_genre} genre, but energy is nearly identical "
            f"(+{GENRE_MISMATCH_CLOSE_ENERGY_POINTS:.1f})"
        )
    else:
        score += GENRE_MISMATCH_PENALTY
        reasons.append(f"genre mismatch ({song['genre']}) ({GENRE_MISMATCH_PENALTY:+.1f})")

    if song["mood"] == user_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match ({song['mood']}) (+{MOOD_MATCH_POINTS:.1f})")

    energy_points = ENERGY_MAX_POINTS * max(0.0, 1 - energy_diff)
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    if likes_acoustic is not None:
        if likes_acoustic and song["acousticness"] >= 0.5:
            score += ACOUSTIC_MATCH_POINTS
            reasons.append(f"acoustic preference match (+{ACOUSTIC_MATCH_POINTS:.1f})")
        elif not likes_acoustic and song["acousticness"] < 0.5:
            score += ACOUSTIC_MATCH_POINTS
            reasons.append(f"acoustic preference match (+{ACOUSTIC_MATCH_POINTS:.1f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    def to_result(song: Dict) -> Tuple[Dict, float, str]:
        """Scores one song and packages it into a (song, score, explanation) tuple."""
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "General match based on your profile"
        return song, score, explanation

    scored = [to_result(song) for song in songs]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
