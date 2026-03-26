# dummy-finder

Index local files into a Gemini-powered vector catalog and search them with ChromaDB.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Set your `GEMINI_API_KEY` in `.env`.

## Python usage

```python
from dummy_finder.ingest import ingest_directory, ingest_file, ingest_text
from dummy_finder.search import format_results, search

ingest_file("./assets/beach.jpg", source="manual", description="Sunset photo")
ingest_file("./docs/travel.pdf", source="manual", description="Beach travel guide")
ingest_directory("./data", source="batch", recursive=True)
ingest_text("sunset at the beach with orange sky", description="sample text")

results = search("sunset at the beach", n_results=5)
print(format_results(results))
```

## CLI usage

Index a single file:

```bash
dummy-finder ingest-file ./assets/beach.jpg --description "Sunset photo"
```

Index a directory:

```bash
dummy-finder ingest-dir ./data --recursive
```

Search:

```bash
dummy-finder search "sunset at the beach" --limit 5
```

Filter by media type:

```bash
dummy-finder search "sunset at the beach" --media-type image
```

## Modules

- `dummy_finder/config.py` configuration and environment loading
- `dummy_finder/helpers.py` file helpers and metadata
- `dummy_finder/embedder.py` Gemini multimodal embedding wrapper
- `dummy_finder/db.py` ChromaDB access layer
- `dummy_finder/ingest.py` ingestion pipeline
- `dummy_finder/search.py` search and result formatting
- `dummy_finder/cli.py` terminal commands
