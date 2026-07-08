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
    }

    for persona, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(persona, user_prefs, recommendations)


if __name__ == "__main__":
    main()
