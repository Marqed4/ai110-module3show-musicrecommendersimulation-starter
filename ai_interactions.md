# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Across several sessions: implement `score_song`/`recommend_songs`/`load_songs` in `recommender.py`, format the CLI output in `main.py`, design adversarial user profiles to stress-test the scoring logic, run a weight-shift sensitivity experiment, write up `model_card.md` and the README's evaluation/bias sections, and finally audit the whole project against the assignment's checklist to catch anything unfinished or undocumented.

**Prompts used (representative examples):**

- "Ask your AI coding assistant to suggest 'adversarial' or 'edge case' user profiles ... e.g., a user with conflicting preferences like energy: 0.9 and mood: sad."
- "Choose one change to test your system's sensitivity: Weight Shift: Double the importance of energy and half the importance of genre ... Note whether the change made the recommendations more accurate or just different."
- "any notes from this project that should be included for grading?" (a self-audit prompt that led to finding the unimplemented `Recommender` class below)

**What did the agent generate or change?**

- Implemented `score_song`, `recommend_songs`, and the CLI formatting in `main.py`; added 3 adversarial profiles (`Hyped But Sad`, `Unrepresented Genre`, `Max Energy Extreme`) to stress-test genre/mood/energy edge cases.
- Ran a temporary weight-shift experiment (doubled energy weight, halved genre weight), captured the before/after output, then reverted the code and documented the finding in README's "Experiments You Tried".
- Wrote up `model_card.md` (all 9 sections) and the README sections covering real-world collaborative-vs-content-based filtering context, the algorithm recipe, biases, and personal reflection.
- Fixed an unclosed markdown code fence in the README Setup section.

**What did you verify or fix manually (or catch the agent doing wrong)?**

- The agent initially left `Recommender.recommend()` and `explain_recommendation()` in `recommender.py` as unimplemented `TODO` stubs from the starter template, even though `tests/test_recommender.py` targets exactly those methods. The existing tests only passed because the test fixture's song order happened to match the stub's no-op `self.songs[:k]` behavior; reversing the input order proved it wasn't actually ranking anything. This was caught during a self-audit pass and fixed by having both methods delegate to `score_song`.
- During a later step, the agent's `Write` tool call to create `assignment_prompt.txt` was independently followed by an unrelated, unexplained overwrite of `data/songs.csv` on disk with unrelated text content. This was caught immediately by re-running `python -m src.play` as a sanity check after touching an unrelated file, and fixed with `git restore data/songs.csv` since the corruption was never committed. Lesson: re-run the test suite and a smoke test after *any* file-writing step, not just the one you think you changed.
- Verified the `play.py` "bonus" module (PyAudio playback + play-count tracking) actually worked before documenting it, which surfaced a second real bug (a bare `from recommender import load_songs` that only resolved when run from inside `src/`, not via the project's standard `python -m src.xxx` invocation).

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
