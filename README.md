# UkAsk

A Persian-language RAG (Retrieval-Augmented Generation) system that answers student questions about University of Kerman's academic regulations, grounded strictly in the university's own PDF documents.

## How it works

```text
PDFs (data/pdfs) → extract + OCR → normalize → chunk → embed → ChromaDB
                                                                    │
question ──────────────────────────────────────────────► hybrid search (dense + BM25)
                                                                    │
                                                         retrieved chunks → LLM → answer
```

- **`pipeline/`** — offline ingestion: PDF text/table extraction, OCR fallback for scans, Persian text normalization, chunking, embedding (`BAAI/bge-m3`), and storage in ChromaDB.
- **`backend/`** — FastAPI service exposing `/api/ask`. Hybrid retrieval (dense + BM25 via Reciprocal Rank Fusion), answer generation, access-code auth.
- **`frontend/`** — React + Vite chat UI.
- **`evaluation/`** — retrieval metrics (hit rate, MRR, MAP) and LLM-judged answer correctness.
- **`notebooks/`** — exploratory notebooks mirroring the pipeline/backend stages, used during development and tuning.

## Prerequisites

- Python 3.12 + [conda](https://docs.conda.io/) (or another env manager — `environment.yml` has the exact deps)
- Node.js 18+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) with the Persian (`fas`) language pack installed
- API keys: a [Hugging Face](https://huggingface.co/) token (`HF_TOKEN`, for downloading the embedding model) and a [GapGPT](https://gapgpt.app/) key (`GAPGPT_API_KEY`, used for both generation and eval)

## Setup

### 1. Backend environment

```bash
conda env create -f environment.yml
conda activate ukask
```

### 2. Tesseract

Install it, then point `TESSERACT_CMD` in [pipeline/config.py](pipeline/config.py) at your binary (or leave it `None` if `tesseract` is already on your `PATH`).

### 3. Environment variables

Create a `.env` file in the project root:

```text
HF_TOKEN=your_huggingface_token
GAPGPT_API_KEY=your_gapgpt_key
ACCESS_CODE=pick_a_shared_access_code
SESSION_SECRET=generate_a_long_random_string
```

`.env` is gitignored — never commit it. Generate `SESSION_SECRET` with something like `python -c "import secrets; print(secrets.token_hex(32))"`.

### 4. Add your documents

Drop PDFs into `data/pdfs/`, then add each filename to `DOCUMENT_MANIFEST` in `pipeline/config.py` with its title and publication date.

### 5. Build the vector index

```bash
python -m pipeline.build_index
```

Re-run this any time the source PDFs or chunking/normalization logic change — it rebuilds the ChromaDB collection from scratch.

### 6. Frontend environment

`frontend/.env` already points at `http://localhost:8000` for local dev — no changes needed unless the backend runs elsewhere.

### 7. Install JS dependencies

```bash
npm install
npm --prefix frontend install
```

## Running locally

From the project root, with the conda env active:

```bash
npm run dev
```

This starts the FastAPI backend (`:8000`) and the Vite dev server (`:5173`) together. Open `http://localhost:5173` and log in with your `ACCESS_CODE`.

To run them separately:

```bash
uvicorn backend.main:app --reload --port 8000
npm --prefix frontend run dev
```

## Evaluation

```python
from evaluation import dataset, retrieval_metrics, rag_metrics
```

See `notebooks/03_retrieval tuning.ipynb` and `notebooks/04_answer_correctness.ipynb` for worked examples — retrieval metrics are free to run repeatedly (no API calls), answer-correctness evaluation calls the LLM judge and costs real requests.

Eval data lives under `data/eval/`:

- `data/eval/evalset.json` — the full labeled question set.
- `data/eval/split.json` — the dev/test split, generated once by `dataset.stratified_split` and reused after (so runs stay comparable).
- `data/eval/results/` — saved metrics from each run (`results.save_results`), one JSON per run, used to compare configurations after the fact.

## Best practices followed here

- **Secrets stay out of git.** All keys/tokens live in `.env` (gitignored), never hardcoded.
- **Config is centralized.** Tunables (chunk sizes, thresholds, model names) live in one place (`pipeline/config.py`) instead of scattered magic numbers.
- **Ingestion is idempotent.** Rebuilding the index always starts from a clean collection, so no stale chunks survive a config change.
- **Retrieval and generation are decoupled** (`retriever.py` vs `generator.py`), so either can be evaluated or swapped independently.
- **Evaluation is separated from the app** and checkpoints results incrementally, so a failed run doesn't waste API calls already spent.
- **Pin your dependencies** (see `environment.yml` / `package.json`) so the environment is reproducible across machines.

## Notes

- `data/pdfs/` (source documents) and `data/eval/` (eval set, split, and results) are tracked in the repo. Only `data/chroma/` (the built vector index) is gitignored.
