"""
CineMind FastAPI backend — hybrid recommender (sentence-transformers + Groq LLM).

Development::

    uvicorn api.main:app --reload --port 8000

Production (after building the frontend)::

    cd frontend && npm run build && cd ..
    uvicorn api.main:app --host 0.0.0.0 --port 8000

Hybrid architecture:
    1. User query → Groq (llama-3.1-8b-instant) query expansion
    2. Original query → filter extraction (language / genre / rating threshold)
    3. Expanded query → sentence-transformer encoding → cosine similarity
    4. Final score = 0.45·semantic + 0.35·rating + 0.20·popularity (all normalised)

Config (via .env / environment):
    GROQ_API_KEY     — Groq API key (required for LLM features)
    HOST             — bind host (default: 127.0.0.1)
    PORT             — bind port (default: 8000)
    ALLOWED_ORIGINS  — comma-separated CORS origins (default: localhost dev ports)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Bootstrap — ensure project root is on sys.path
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import get_settings  # noqa: E402
from recommender.engine import MovieRecommender  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("cinemind.api")

# ---------------------------------------------------------------------------
# Settings singleton
# ---------------------------------------------------------------------------
_settings = get_settings()

# ---------------------------------------------------------------------------
# App-level singletons
# ---------------------------------------------------------------------------
_recommender: MovieRecommender | None = None
_groq: OpenAI | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle — load models once, release on exit."""
    global _recommender, _groq
    logger.info("Starting CineMind API — loading models…")

    if not os.path.exists(_settings.CSV_PATH):
        raise RuntimeError(f"Dataset not found: {_settings.CSV_PATH}")
    if not os.path.exists(_settings.EMBEDDINGS_PATH):
        raise RuntimeError(f"Embeddings not found: {_settings.EMBEDDINGS_PATH}")

    _recommender = MovieRecommender(
        csv_path=_settings.CSV_PATH,
        embeddings_path=_settings.EMBEDDINGS_PATH,
    )

    if _settings.GROQ_API_KEY:
        _groq = OpenAI(
            api_key=_settings.GROQ_API_KEY,
            base_url=_settings.GROQ_BASE_URL,
        )
        logger.info("Groq LLM client ready (model: %s).", _settings.GROQ_MODEL)
    else:
        logger.warning(
            "GROQ_API_KEY not set — LLM query expansion and movie details "
            "will fall back to local inference only."
        )

    logger.info(
        "CineMind API ready. CORS origins: %s",
        _settings.allowed_origins_list,
    )
    yield
    _recommender = None
    _groq = None


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CineMind API",
    version="1.0.0",
    description="Hybrid movie recommendation engine — semantic search + Groq LLM.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins_list,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------------
# Middleware — request ID for log tracing
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Inject a unique request ID into each response for observability."""
    request_id = str(uuid.uuid4())[:8]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return a structured JSON response for any unhandled server error."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language movie query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")


class MovieResult(BaseModel):
    title: str
    genres: list[str]
    averageRating: float
    finalScore: float
    why: str


class RecommendResponse(BaseModel):
    results: list[MovieResult]
    query: str
    enhancedQuery: str | None = None


class MovieDetailsResponse(BaseModel):
    title: str
    summary: str
    cast: list[str]


# ---------------------------------------------------------------------------
# Groq helpers
# ---------------------------------------------------------------------------
def _expand_query(query: str) -> str:
    """Rewrite the user query as a rich semantic description via Groq LLM.

    The expanded text is used only for sentence-transformer encoding so the
    vector search benefits from richer context.  Structured filter signals
    (language, genre, rating) are still extracted from the *original* query
    by the engine, so nothing is lost.

    Falls back to the original query when Groq is unavailable or errors out.
    """
    if _groq is None:
        return query
    try:
        resp = _groq.chat.completions.create(
            model=_settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a movie search assistant. Rewrite the user's movie "
                        "preference query as a detailed 2-3 sentence description that "
                        "captures the genre, themes, emotional tone, pacing, and any "
                        "specific elements they mentioned. This description will be used "
                        "for semantic similarity search against movie plot summaries. "
                        "Do NOT include phrases like 'above 8 IMDb', language names, "
                        "or rating thresholds — those are handled separately. "
                        "Return only the rewritten description, nothing else."
                    ),
                },
                {"role": "user", "content": query},
            ],
            max_tokens=150,
            temperature=0.3,
        )
        expanded = resp.choices[0].message.content.strip()
        logger.info("Groq query expansion: %r → %r", query, expanded)
        return expanded
    except Exception as exc:  # noqa: BLE001
        logger.warning("Groq query expansion failed (%s) — using raw query.", exc)
        return query


@lru_cache(maxsize=256)
def _fetch_movie_details(title: str, overview: str) -> dict:
    """Ask Groq for a polished story summary and cast list for *title*.

    Results are LRU-cached per process so repeated clicks on the same movie
    do not re-hit the Groq API.
    """
    if _groq is None:
        return {"summary": overview or "No summary available.", "cast": []}
    try:
        resp = _groq.chat.completions.create(
            model=_settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a movie expert. Given a movie title and its plot overview, "
                        "return a JSON object with exactly two keys:\n"
                        '  "summary": an engaging 2-3 sentence description of the story '
                        "that makes a viewer want to watch it (no spoilers),\n"
                        '  "cast": an array of 3-5 main actors/actresses by name.\n'
                        "Use your own knowledge to fill in cast details not mentioned in "
                        "the overview. Return only valid JSON, nothing else."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Movie: {title}\nOverview: {overview or 'Not available.'}",
                },
            ],
            max_tokens=300,
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return {
            "summary": str(data.get("summary", overview or "No summary available.")),
            "cast": [str(c) for c in data.get("cast", [])],
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Groq movie details failed for %r (%s).", title, exc)
        return {"summary": overview or "No summary available.", "cast": []}


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Liveness probe."""
    return {
        "status": "ok",
        "model_loaded": _recommender is not None,
        "groq_ready": _groq is not None,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """Return ranked movie recommendations for *query*.

    The query is expanded by Groq LLM for richer semantic matching.
    """
    if _recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Model is still loading — try again shortly.",
        )

    expanded = _expand_query(req.query)

    try:
        df = _recommender.recommend(
            query=req.query,
            top_k=req.top_k,
            semantic_query=expanded,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    results: list[MovieResult] = []
    for _, row in df.iterrows():
        raw_genres = str(row.get("genres", "") or "")
        genres_list = [g.strip() for g in raw_genres.split(",") if g.strip()]
        results.append(
            MovieResult(
                title=str(row["title"]),
                genres=genres_list,
                averageRating=float(row["averageRating"]),
                finalScore=float(row["final_score"]),
                why=str(row["why"]),
            )
        )

    return RecommendResponse(
        results=results,
        query=req.query,
        enhancedQuery=expanded if expanded != req.query else None,
    )


@app.get("/movie/details", response_model=MovieDetailsResponse)
def movie_details(title: str = Query(..., min_length=1)):
    """Return an AI-generated story summary and cast list for *title*."""
    if _recommender is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")

    overview = _recommender.get_movie_overview(title) or ""
    details = _fetch_movie_details(title, overview)

    return MovieDetailsResponse(
        title=title,
        summary=details["summary"],
        cast=details["cast"],
    )


# ---------------------------------------------------------------------------
# Production static file serving — only active when frontend/dist exists.
# Run `cd frontend && npm run build` first.
# ---------------------------------------------------------------------------
if os.path.isdir(_settings.FRONTEND_DIST):
    _assets_dir = os.path.join(_settings.FRONTEND_DIST, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Serve the React SPA for any non-API route."""
        return FileResponse(os.path.join(_settings.FRONTEND_DIST, "index.html"))
