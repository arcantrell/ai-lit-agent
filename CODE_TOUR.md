# Code Tour

This project is organized so the scientific workflow and the software responsibilities are separated.

## Why Python

Python is common in biology, data analysis, and scientific computing. It also has strong libraries for web apps, PDFs, databases, and API integrations. That makes it a practical choice for a scientist-built research tool.

## Main Pieces

### `models.py`

Defines the core `Paper` data model. Search results from PubMed and PDF imports are normalized into this shared shape. Crossref is used for DOI lookup when a PDF contains a DOI.

Important fields include:

- `title`
- `authors`
- `year`
- `abstract`
- `doi`
- `url`
- `source`
- `paper_type`

### `providers.py`

Contains the search connectors.

- `PubMedProvider` searches PubMed.
- `CrossrefProvider` can search Crossref and is currently used for DOI metadata lookup during PDF import.
- `ScienceDirectProvider` can search ScienceDirect when `ELSEVIER_API_KEY` is configured, but it is not enabled in the current UI.
- `MultiSearchProvider` can combine results across providers and remove duplicates.

The app currently uses PubMed as the primary search source because PubMed metadata is stronger for biomedical literature. The provider layer still exists so new sources can be added without rewriting the rest of the app.

### `storage.py`

Manages the local SQLite database.

SQLite stores papers, notes, subjects, screening status, extracted full text, and saved Research Briefing searches in one local database file.

### `pdf_text.py`

Extracts text from PDFs using `pypdf` and searches the extracted text for DOIs.

This lets the app import a downloaded paper directly, detect its DOI, and retrieve citation metadata when possible.

### `research_agent.py`

This is the agent workflow layer.

It reads saved Research Briefing searches, runs them across selected sources, ranks candidate results, and produces a briefing with Read First papers, newest papers, recurring themes, and suggested review actions. It does not save candidate papers into the library until the user approves them.

### `summarizer.py`

Provides simple local ranking and extractive summaries. It does not require an LLM.

Future versions can add OpenAI or Claude calls for deeper synthesis while keeping this local fallback.

### `web.py`

Defines the FastAPI web app. It exposes routes such as:

- `/api/search`
- `/api/papers`
- `/api/import/pdf`
- `/api/saved-searches`
- `/api/weekly-update/run`
- `/api/export/bibtex`
- `/api/export/ris`

### `static/`

Contains the browser interface:

- `index.html` for structure
- `styles.css` for visual design
- `app.js` for browser interactions

The frontend is plain HTML, CSS, and JavaScript so the project stays understandable without a heavy frontend framework.

## Design Tradeoffs

- Local-first storage protects private notes and PDFs.
- API providers are separated from storage and UI so sources can be swapped or added.
- The app works without an LLM, but has a clear place to add LLM-backed synthesis later.
- The GUI is intentionally practical rather than flashy, because this is a research workflow tool.
