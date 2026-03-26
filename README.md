# dummy-finder

Index local files into a Gemini-powered vector catalog and search them with ChromaDB.

Supports images, PDFs, audio, video, and text files. Search in plain English. A native macOS app watches folders and auto-embeds new files the moment they land.

---

## how it works

**embed**
```
file (image / pdf / audio / video / text)
        │
        ▼
  Gemini Embedding 2
        │
        ▼
  768-dim vector
        │
        ▼
  ChromaDB  ──── stored locally on disk
```

**search**
```
"sunset at the beach"  (plain english query)
        │
        ▼
  Gemini Embedding 2  (query mode)
        │
        ▼
  768-dim query vector
        │
        ▼
  ChromaDB cosine similarity search
        │
        ▼
  top N results  ──── ranked by similarity score
```

---

## requirements

- Python 3.10+
- macOS 14+ (for the app)
- Gemini API key — get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## setup

```bash
git clone https://github.com/Nishu0/dummy_finder.git
cd dummy_finder

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
```

Open `.env` and set your key:

```
GEMINI_API_KEY=AIzaSy...your_key_here
```

Everything else in `.env` has sensible defaults and can be left as-is.

---

## embed a folder

Point it at any folder on your machine — Downloads, Desktop, a project directory, anything:

```bash
source .venv/bin/activate
dummy-finder ingest-dir /Users/yourname/Downloads --recursive
```

Embed a single file:

```bash
dummy-finder ingest-file /Users/yourname/Downloads/report.pdf --description "Q4 report"
```

Embed a text snippet directly:

```bash
dummy-finder ingest-text "sunset at the beach with orange sky" --title "beach note"
```

---

## search

```bash
dummy-finder search "sunset at the beach" --limit 5
```

Filter by file type:

```bash
dummy-finder search "project proposal" --media-type document
dummy-finder search "team standup recording" --media-type audio
dummy-finder search "logo design" --media-type image
```

Output as JSON:

```bash
dummy-finder search "rate limiting" --json
```

---

## supported file types

| category | extensions |
|---|---|
| image | `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` `.tiff` |
| audio | `.mp3` `.wav` `.m4a` `.ogg` `.flac` `.aac` |
| video | `.mp4` `.mov` `.avi` `.mkv` `.webm` |
| document | `.pdf` |
| text / code | `.txt` `.md` `.csv` `.json` `.yaml` `.toml` `.html` `.py` `.js` `.ts` `.go` `.rs` `.sh` |

---

## macOS app

Open the Xcode project:

```bash
open app/DummyFinder.xcodeproj
```

Build and run with `Cmd+R`.

Make sure your `.venv` is set up at the project root before launching — the app calls the Python backend directly via subprocess.

**Using the app:**

1. Type any query in the search bar — results appear as you type
2. Click the folder icon in the top right to pick a folder to watch
3. Toggle the switch next to the folder name to enable auto-embed
4. Any new file dropped into that folder gets embedded automatically
5. Filter results by file type using the pills at the top
6. Click any result card to reveal the file in Finder

---

## python usage

```python
from dummy_finder.ingest import ingest_directory, ingest_file, ingest_text
from dummy_finder.search import format_results, search

ingest_file("/Users/yourname/Downloads/beach.jpg", description="Sunset photo")
ingest_file("/Users/yourname/Documents/travel.pdf", description="Beach travel guide")
ingest_directory("/Users/yourname/Downloads", recursive=True)

results = search("sunset at the beach", n_results=5)
print(format_results(results))
```

---

## env reference

| variable | default | description |
|---|---|---|
| `GEMINI_API_KEY` | required | your Gemini API key |
| `EMBEDDING_MODEL` | `gemini-embedding-2-preview` | embedding model name |
| `EMBEDDING_DIMENSIONS` | `768` | output vector size |
| `MAX_TEXT_TOKENS` | `8192` | max tokens for text embedding |
| `DUMMY_FINDER_DATA_DIR` | `./data` | where ChromaDB is stored |
| `DUMMY_FINDER_CHROMA_DIR` | `./data/chromadb` | ChromaDB path |
| `DUMMY_FINDER_COLLECTION_NAME` | `dummy_finder` | collection name |

---

## modules

- `dummy_finder/config.py` — settings and environment loading
- `dummy_finder/helpers.py` — file hashing, metadata, mime detection
- `dummy_finder/embedder.py` — Gemini multimodal embedding wrapper
- `dummy_finder/db.py` — ChromaDB access layer
- `dummy_finder/ingest.py` — ingestion pipeline for files and directories
- `dummy_finder/search.py` — cosine search and result formatting
- `dummy_finder/cli.py` — terminal commands
- `app/` — native macOS SwiftUI app
