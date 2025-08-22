# 🎵 Story & Scene Music Director (Non-Commercial)

> Tools for pairing text (stories, scenes, books) with mood-matched music using the Spotify Web API + lightweight NLP.
> **SPDX-License-Identifier:** `PolyForm-Noncommercial-1.0.0`

* `musicDirector.py` — finds mood-appropriate tracks for a single story passage.
* `musicDirectorPDF.py` — scans a **PDF** (book/screenplay) and suggests songs per paragraph.
* `SceneSongs.py` — recommends music for a **scene** (location/time/weather/emotions/actions/genre).
* `textAnalysis.py` — segments long text and performs NER, topics, and sentiment analysis.

---

## ✨ Features

* spaCy-based parsing (entities, noun chunks, mood words)
* Synonym expansion via NLTK WordNet
* Spotify search + audio features (valence/energy/instrumentalness/acousticness)
* PDF paragraph extraction & per-paragraph recommendations
* Scene-aware matching with curated mood mappings
* Optional topic modeling + transformer sentiment (helper script)

---

## 🧩 Structure

```
.
├── musicDirector.py
├── musicDirectorPDF.py
├── SceneSongs.py
├── textAnalysis.py
├── requirements.txt            # example below
├── .env.example                # example below
└── README.md
```

---

## 🚀 Quick Start

### 1) Requirements

* Python 3.9–3.11
* `ffmpeg` (needed by `pydub` if you process local audio)

```bash
# macOS
brew install ffmpeg
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### 2) Virtual env

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3) Install deps + models

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('wordnet')"
```

**Suggested `requirements.txt`:**

```
spacy>=3.7
spotipy>=2.24
requests>=2.31
pydub>=0.25
nltk>=3.9
PyPDF2>=3.0
numpy>=1.26
scikit-learn>=1.5
gensim>=4.3
transformers>=4.43
torch>=2.3 ; platform_system != "Darwin" or platform_machine != "arm64"
```

> On Apple Silicon you can skip `torch` or install a compatible build for `transformers` sentiment.

### 4) Spotify credentials

1. Create an app in the **Spotify Developer Dashboard**.
2. Copy **Client ID** and **Client Secret**.
3. Put them in a `.env` file (or directly in the scripts):

`.env.example`

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

---

## 📘 Usage

### A) `musicDirector.py` — Single passage

* Edit `spotify_client_id`, `spotify_client_secret`, and `chosen_artists` at the bottom of the script.
* Replace the `story` string with your text.
* Run:

```bash
python musicDirector.py
```

Notes:

* Filters to tracks with a preview and matching `chosen_artists`.
* Uses Spotify audio features (`valence`, `energy`) to steer mood.
* `get_music_from_url` expects a **direct audio URL** (e.g., MP3), not a Spotify page link.

---

### B) `musicDirectorPDF.py` — Full PDF

* Edit credentials and `chosen_artists`.
* **Important fix-up:** Set a real PDF path and remove Colab-only calls.
  Replace the bottom section with:

```python
spotify_client_id = "..."
spotify_client_secret = "..."

chosen_artists = [
    "Hans Zimmer", "Max Richter", "Ludovico Einaudi",
    "Johann Johannsson", "Ólafur Arnalds", "Nicholas Britell",
    "Gustavo Santaolalla", "Philip Glass", "Thomas Newman",
    "Nils Frahm", "Jon Hopkins", "Joep Beving"
]

recommender = BookMusicRecommender(spotify_client_id, spotify_client_secret, chosen_artists)
pdf_path = "path/to/your/book.pdf"
output_file = "book_recommendations.txt"
recommender.process_book(pdf_path, output_file)
```

* Run:

```bash
python musicDirectorPDF.py
```

Output: `book_recommendations.txt` with top 3 songs per paragraph (title/artist/Spotify link/mood score).

---

### C) `SceneSongs.py` — Scene-aware recommender

* Edit credentials, `chosen_artists`, and the `scene_description`.
* Run:

```bash
python SceneSongs.py
```

Prints a list of recommendations sorted by `mood_score`, each with a `match_reason`.

---

### D) `textAnalysis.py` — Segmentation & analytics

* Update the example `file_path` (top/bottom of the script).
* Run:

```bash
python textAnalysis.py
```

Shows named entities, top topic(s) via LDA, and transformer sentiment per segment.

---

## ⚙️ Tuning Tips

* **Artists filter:** Expand `chosen_artists` to steer the vibe (film composers vs pop/alt/ambient).
* **Preview requirement:** If you get few results, relax the preview filter or increase Spotify search `limit`.
* **Weights/thresholds:** Adjust valence/energy/instrumentalness weights in `SceneSongs.py` to your taste.

---

## 🧪 Troubleshooting

* `OSError: [E050] Can't find model 'en_core_web_sm'`
  → `python -m spacy download en_core_web_sm`
* `LookupError: Resource 'wordnet' not found`
  → `python -c "import nltk; nltk.download('wordnet')"`
* `ffmpeg` not found / audio load errors
  → Install `ffmpeg` and ensure it’s on PATH.
* Undefined `filename` or `files.download(...)` in `musicDirectorPDF.py`
  → Use `pdf_path` and **remove** any Colab-only calls.
* Sparse results / rate limits
  → Widen `chosen_artists`, raise search `limit`, and avoid rapid repeated calls.

---

## 🔒 Legal & Content Notes

* Uses Spotify Web API for metadata and audio features; respect Spotify’s Developer Terms.
* Scripts return metadata/links; they **do not** download full audio from Spotify.
* If you integrate playback/downloads, obtain proper content licenses.

---

## 🤝 Contributing

PRs welcome for:

* Better mood heuristics/weights
* New extractors (screenplays/subtitles)
* Caching, retries, rate-limit handling
* Optional web UI (Streamlit/FastAPI)

Please keep contributions aligned with the **non-commercial** license.

---

## 📜 License (Non-Commercial)

This project is released under the **PolyForm Noncommercial License 1.0.0** (SPDX: `PolyForm-Noncommercial-1.0.0`).
**Commercial use is not permitted** without a separate written agreement from the author.

* Add a `LICENSE` file containing the full text of **PolyForm Noncommercial 1.0.0**.
* You may dual-license docs/media under **CC BY-NC 4.0** if desired.

For commercial licensing, open an issue to discuss terms.

---

## 🙌 Acknowledgments

* spaCy · NLTK WordNet · Spotipy · PyPDF2 · Gensim · Transformers

---

**TL;DR:** Add your Spotify keys → run the scripts → get mood-matched song suggestions for passages, scenes, or whole PDFs. **Non-commercial only.**



Thank you :)

