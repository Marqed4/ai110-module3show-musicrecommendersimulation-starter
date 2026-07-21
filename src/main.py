"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(persona: str, user_prefs: dict, recommendations: list) -> None:
    prefs_line = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    header = f"Recommendations for: {persona}"

    print("=" * 60)
    print(header)
    print(f"Profile: {prefs_line}")
    print("=" * 60)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}  (Score: {score:.2f})")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print()

    # Exemplary user profiles, deliberately varied to stress-test the recommender
    user_profiles = {
        "Default (Pop / Happy)": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        # Late 90s/early 2000s soft rock fan (e.g. Green Day, other pop-punk/alt-rock era bands)
        "Soft Rock Nostalgic": {"genre": "rock", "mood": "nostalgic", "energy": 0.55, "likes_acoustic": True},
        "EDM Raver": {"genre": "house", "mood": "energetic", "energy": 0.9, "likes_acoustic": False},
        "Lofi Chill Studier": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "Hip-Hop Head": {"genre": "hip-hop", "mood": "nostalgic", "energy": 0.6, "likes_acoustic": False},
        # Adversarial: conflicting signals - high energy but a sad mood, and no
        # stated acoustic preference, to see how the scorer resolves the tension.
        "Adversarial: Hyped But Sad": {"genre": "pop", "mood": "sad", "energy": 0.95, "likes_acoustic": None},
        # Adversarial: genre with zero catalog coverage, to see whether the
        # mismatch penalty/energy-exception logic degrades gracefully.
        "Adversarial: Unrepresented Genre": {"genre": "classical", "mood": "chill", "energy": 0.4, "likes_acoustic": True},
        # Adversarial: extreme energy at both ends of the scale with a neutral mood,
        # to check whether energy closeness alone can override genre weighting.
        "Adversarial: Max Energy Extreme": {"genre": "lofi", "mood": "chill", "energy": 1.0, "likes_acoustic": False},
    }

    for persona, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(persona, user_prefs, recommendations)


if __name__ == "__main__":
    main()
