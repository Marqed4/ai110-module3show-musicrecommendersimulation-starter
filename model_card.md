# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder takes a short list of stated taste preferences (favorite genre, favorite mood, target energy, and whether the listener likes acoustic songs) and ranks a fixed catalog of songs to surface the top few matches, along with a plain-language reason for each one.

- It assumes the user can name their own genre, mood, energy, and acoustic preference up front. It does not learn from listening history or skips.
- It is built for classroom exploration of how a simple, transparent scoring rule turns stated preferences into a ranked list, not for real-world deployment. The catalog is only 18 songs, far too small to serve real listeners.

---

## 3. How the Model Works

Imagine handing a friend your list of favorite genre, mood, target energy, and whether you like acoustic songs, and asking them to go through a stack of 18 songs one at a time, giving each one a "vibe score."

For every song, the friend adds points:

- **+2 points** if the song's genre matches your favorite genre. If it doesn't match, the song loses a point, unless its energy is nearly identical to what you asked for, in which case it gets a small consolation point instead of the penalty.
- **+1 point** if the song's mood matches your favorite mood.
- **Up to +1 point** for how close the song's energy is to your target energy. A perfect match earns the full point; the further off it is, the fewer points it gets.
- **+0.5 points** if the song being acoustic (or not) matches whether you said you like acoustic songs.

Once every song has a score, the friend sorts the whole stack from highest to lowest and hands you the top 5, along with a note of exactly which of the above reasons earned each song its points.

Genre is weighted the heaviest on purpose, so recommendations stay "on-topic" for the genre you said you like, and only step outside it when a song's energy is a near-perfect match. This is the same core idea as the starter logic, just filled in and tuned so genre clearly outweighs the other signals.

---

## 4. Data

- The catalog (`data/songs.csv`) has **18 songs** total, spanning 13 different genres (pop, rock, house, lofi, hip-hop-adjacent, dream pop, indie pop, synthwave, electronic, dance, hyperpop, ambient, breakcore) and moods like happy, chill, energetic, nostalgic, and sad.
- Each song carries: `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`.
- No songs were added or removed from the starter dataset.
- With 13 genres spread across only 18 songs, most genres have just 1-2 songs, so there's very little variety within any single genre. Several plausible tastes (classical, jazz-adjacent that isn't just labeled "jazz," metal, country) aren't represented at all.

---

## 5. Strengths

- **Users whose stated genre is well represented** (pop, rock, lofi, house) get results that clearly match their intuition: the top pick is consistently a same-genre, same-mood, close-energy song.
- The energy-closeness scoring behaves smoothly and predictably across the whole 0-1 range, including at the extremes (tested at `energy=1.0`), with no boundary bugs.
- The genre-mismatch "close energy" exception is a nice touch: a song from a different genre can still surface if its vibe (energy) lines up almost exactly, instead of being flatly excluded.
- Every recommendation comes with a itemized, human-readable explanation of exactly why it scored the way it did, which makes the system easy to audit and debug.

---

## 6. Limitations and Bias

The biggest weakness is that **the current scoring logic makes genre almost impossible to overcome, which quietly punishes users whose stated genre isn't in the catalog at all.** When a user asks for a genre with zero catalog coverage (tested with `genre: classical`), every single song mismatches, so the entire ranking collapses onto the "close energy" exception path; the recommender never signals "we don't have anything for you," it just confidently returns its best energy-guess instead. This is a filter-bubble risk in reverse: rather than over-narrowing to one genre, an unsupported user gets recommendations that look just as confident as everyone else's, with no genre relevance at all, and no way for the system to flag that it's operating outside its coverage.

A second, related issue showed up during the weight-shift experiment (see "Experiments You Tried" in README.md): when genre's weight is reduced relative to energy, off-genre songs start winning the top spot purely because their energy happens to match, which shows the system's "correctness" is fragile and entirely dependent on genre staying the dominant signal. A third bias comes from the dataset itself: with only 1-2 songs per genre, a user's "top 5" is often just "every song in the catalog that shares their genre," so there's effectively no room for the system to discover variety even for well-covered genres. Finally, the mood signal can silently contribute nothing (as seen with the `mood: sad, energy: 0.95` adversarial profile, a combination the catalog simply doesn't contain), which isn't wrong, but means a user's mood preference can be entirely ignored without any indication that it happened.

---

## 7. Evaluation

Eight user profiles were run end-to-end through `python -m src.main` against the full 18-song catalog (full output pasted in README.md's "Sample Recommendation Output" section): five representative personas (Default Pop/Happy, Soft Rock Nostalgic, EDM Raver, Lofi Chill Studier, Hip-Hop Head) and three adversarial edge cases designed to probe the scoring logic (conflicting mood/energy, an unrepresented genre, and maximum energy).

**What was tested and what was surprising:**

- **Default (Pop/Happy) vs. EDM Raver** - both ask for high energy (0.8 and 0.9) but different genres and moods. The top picks are genre-correct in both cases ("Sunrise City" for pop, "They Don't Know" for house), which matched intuition and confirmed genre is doing its job as the dominant signal.
- **Soft Rock Nostalgic vs. Lofi Chill Studier** - one wants mid-energy rock with a nostalgic mood, the other wants low-energy lofi with a chill mood. The rankings look nothing alike (guitar-driven rock tracks vs. quiet lofi beats), which is exactly what should happen when energy and genre both move in opposite directions between two profiles.
- **Hip-Hop Head** was the most surprising result: the catalog has **no hip-hop songs at all**, so every result is an "outside your usual genre" pick. The #1 result ("I Wish") only wins because it happens to match mood and energy almost exactly, not because it's remotely hip-hop. This surprised us; it's the same underlying issue as the "Unrepresented Genre" adversarial profile, just discovered organically from a "normal-looking" persona rather than a deliberately adversarial one.
- **Adversarial: Hyped But Sad vs. Default (Pop/Happy)** - both ask for `genre: pop`, but one wants `mood: happy` and the other `mood: sad` at a much higher energy. Both return pop songs at the top, but the "sad" profile's top picks score noticeably lower overall (no song in the catalog is both very high-energy and sad), showing the system correctly reflects "we don't really have this mood/energy combo" through lower scores rather than crashing or erroring.
- **Adversarial: Unrepresented Genre vs. Adversarial: Max Energy Extreme** - one has a genre with zero catalog matches, the other has a real genre (lofi) but pushes energy to its maximum. The "unrepresented genre" profile's results are entirely genre-mismatched "close energy" picks, while the "max energy" profile still surfaces true lofi genre matches first, showing that a real, well-covered genre stays robust even at an extreme energy value, while a genre with zero coverage cannot be "saved" by any other signal.

A recurring, non-programmer-friendly way to explain the "Gym Hero keeps showing up for Happy Pop" pattern: **the recommender is not thinking about what a "happy pop" song *sounds* like, it's just checking three boxes** (is the genre labeled "pop," is the mood labeled "happy," is the energy close to what you asked for) and adding up points. "Gym Hero" checks the pop and high-energy boxes very well, so it keeps floating to the top for any high-energy pop request, even if a human listener might describe it as more "pumped-up" than "happy." The system can't tell the difference between those two vibes because it was never given a signal for it, so it leans on the boxes it does have.

---

## 8. Future Work

- Add a minimum-coverage check: if a user's requested genre has zero (or very few) catalog matches, surface an explicit "we don't have much for this genre yet" note instead of silently falling back to the energy-only exception path.
- Add more songs per genre so "top 5" results reflect genuine ranking within a genre rather than just listing every song that happens to share it.
- Let `explanation` also state when a signal (like mood) contributed nothing, so users can see when their stated preference had no effect on the ranking, instead of just seeing what did.

---

## 9. Personal Reflection

The biggest learning moment was seeing how much a recommender's "personality" comes down to just a handful of weight numbers. Doubling the energy weight and halving the genre weight as a quick experiment was enough to flip the #1 recommendation for a profile from an actual rock song to a song from a completely different genre; nothing about the code's structure changed, only the relative size of a couple of constants.

Using an AI coding assistant helped speed up writing the scoring loop and the CLI formatting, and it was genuinely useful for generating adversarial test profiles I hadn't thought of (like pairing high energy with a sad mood). The place I had to double-check it most was verifying its claims about *why* a specific song ranked where it did; the safest way to confirm that was to actually read the itemized reasons printed by the CLI rather than trust a summary, since the score breakdown is the ground truth.

What surprised me most is how convincing a very simple, additive point system can feel. Even though the recommender has no idea what any of these songs actually sound like, checking three or four boxes and adding up points produces rankings that "feel" like real taste-matching, right up until you test an edge case (like an unrepresented genre) and see how confidently it keeps producing a top 5 anyway. If I extended this project, I'd want to add some notion of catalog coverage or confidence, so the system can distinguish "I found you a great match" from "I did my best with what I have."
