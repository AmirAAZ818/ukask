"""FastAPI app exposing backend.rag over HTTP. This is purely the web layer,
it does not change how retrieval or generation work.

Run from the project root, so both `backend` and `pipeline` resolve as
packages:

    uvicorn backend.main:app --reload --port 8000
"""

import logging
import time
from contextlib import asynccontextmanager

import httpx
from chromadb.errors import NotFoundError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pipeline import config, embed, store

from . import rag
from .schemas import AskRequest, AskResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ukask")

# vite's default dev server origin, add the GitHub Pages URL here too
# once that bonus deployment exists
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# updated once at startup, read by /api/health on every request after that
_readiness = {"index_ready": False, "embedding_model_ready": False}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up, checking vector index and warming the embedding model")

    client = store.get_client()
    try:
        client.get_collection(config.COLLECTION_NAME)
        _readiness["index_ready"] = True
    except NotFoundError as exc:
        # fail fast and loud rather than serving requests with no data behind them
        raise RuntimeError(
            f"Chroma collection '{config.COLLECTION_NAME}' does not exist yet. "
            "Run pipeline/build_index.py (or the ingestion notebook) before "
            "starting the API."
        ) from exc

    # loading the model here, not on the first request, means the ~2GB
    # download and load happens once at boot instead of on someone's first question
    embed.embed_texts(["warmup"])
    _readiness["embedding_model_ready"] = True

    logger.info("startup complete, index and embedding model are ready")
    yield
    logger.info("shutting down")


app = FastAPI(
    title="UkAsk API",
    description="Persian-language RAG API for answering questions about university regulations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def index_missing_handler(request: Request, exc: NotFoundError):
    logger.error("chroma collection missing at request time: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "The vector index isn't built yet. Run pipeline/build_index.py first."},
    )


@app.exception_handler(httpx.HTTPError)
async def generation_service_error_handler(request: Request, exc: httpx.HTTPError):
    # covers HfHubHTTPError (auth, rate limit, bad request) and
    # InferenceTimeoutError, both are httpx.HTTPError subclasses
    logger.error("huggingface inference call failed: %s", exc)
    return JSONResponse(
        status_code=502,
        content={"detail": "The generation service is unavailable right now, please try again shortly."},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("unhandled error while serving %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our side."},
    )


@app.get("/api/health", response_model=HealthResponse)
def health():
    all_ready = all(_readiness.values())
    return HealthResponse(
        status="ok" if all_ready else "degraded",
        index_ready=_readiness["index_ready"],
        embedding_model_ready=_readiness["embedding_model_ready"],
    )


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    # plain def, not async def, on purpose, retriever.search and
    # generator.generate_answer are blocking calls, FastAPI runs plain def
    # routes in a worker thread pool so one slow answer doesn't stall
    # every other request hitting the server at the same time
    started = time.perf_counter()
    result = rag.answer_question(payload.question, k=payload.k)
    elapsed = time.perf_counter() - started
    logger.info(
        "answered question in %.2fs, k=%d, %d sources",
        elapsed, payload.k, len(result["sources"]),
    )
    return result