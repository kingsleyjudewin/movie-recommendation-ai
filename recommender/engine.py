"""
Movie Recommendation Engine
============================
Hybrid semantic + metadata ranking using precomputed sentence embeddings.

Scoring formula (all three components min-max normalised within the pool):
    final_score = 0.45 * norm(semantic_similarity)
                + 0.35 * norm(rating_score)
                + 0.20 * norm(popularity_score)

Normalising within the pool guarantees each component uses its full 0–1
range regardless of the absolute scale of raw cosine similarities or the
floor imposed by the dataset's quality filter on rating_score.  Without
normalisation the same globally popular/highly-rated movies dominate every
query, making the semantic signal irrelevant.

All filtering (language, genre/mood, rating threshold) is applied before
ranking to keep inference fast and results contextually relevant.

Key design improvements over a naïve implementation:
    - Per-pool min-max normalisation — semantic signal is always competitive
    - Genres precomputed lowercase at init — zero repeated case-folding per query
    - ``device`` parameter exposes hardware selection for the query encoder
    - Diversity re-ranking penalises same-primary-genre repetition in top-k
    - Per-result ``why`` column explains the dominant score contributor
"""

from __future__ import annotations

import logging
import pickle
import re
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lookup tables (module-level constants — not global mutable state)
# ---------------------------------------------------------------------------

_LANGUAGE_MAP: dict[str, str] = {
    "english":  "en",
    "hindi":    "hi",
    "korean":   "ko",
    "japanese": "ja",
    "french":   "fr",
    "spanish":  "es",
}

# Reverse lookup: ISO 639-1 code → human-readable name (used in explanations)
_LANG_DISPLAY: dict[str, str] = {code: kw.title() for kw, code in _LANGUAGE_MAP.items()}

# Maps individual mood/synonym words → canonical genre (title-case, CSV-ready)
_MOOD_MAP: dict[str, str] = {
    "funny":     "Comedy",
    "bored":     "Comedy",
    "sad":       "Drama",
    "romantic":  "Romance",
    "love":      "Romance",
    "scary":     "Horror",
    "thrilling": "Thriller",
    "exciting":  "Action",
}

# Supported genres in title-case (matches genre strings in the CSV)
_SUPPORTED_GENRES: tuple[str, ...] = (
    "Action",
    "Comedy",
    "Drama",
    "Thriller",
    "Romance",
    "Horror",
    "Animation",
    "Crime",
    "Fantasy",
    "Science Fiction",
)

# Regex for rating constraints — compiled once at import time
_RATING_RE = re.compile(
    r"(?:above|over|minimum|greater\s+than|at\s+least)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Hybrid score weights
_W_SEMANTIC   = 0.45
_W_RATING     = 0.35
_W_POPULARITY = 0.20

# Minimum movies in filtered pool before falling back to full dataset
_MIN_FILTER_SIZE = 15


class MovieRecommender:
    """Hybrid movie recommendation engine combining semantic search with
    IMDb rating and popularity signals.

    Parameters
    ----------
    csv_path : str
        Path to the curated movie dataset CSV
        (must contain: title, genres, original_language, averageRating,
        rating_score, popularity_score).
    embeddings_path : str
        Path to the precomputed, L2-normalised sentence embeddings pickle
        (numpy array of shape ``(n_movies, 384)``).
    model_name : str
        Sentence-Transformers model identifier used to encode queries at
        inference time.  Must match the model that produced the stored
        embeddings.
    device : str, optional
        PyTorch device for the query encoder, e.g. ``"cpu"``, ``"cuda"``,
        or ``"mps"``.  Defaults to ``None`` (auto-detected by
        SentenceTransformer — uses CUDA when available, else CPU).
    """

    def __init__(
        self,
        csv_path: str,
        embeddings_path: str,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
    ) -> None:
        logger.info("Loading movie dataset from %s", csv_path)
        df_raw = pd.read_csv(csv_path)

        logger.info("Loading precomputed embeddings from %s", embeddings_path)
        with open(embeddings_path, "rb") as fh:
            raw = pickle.load(fh)
        emb_raw: np.ndarray = np.ascontiguousarray(raw, dtype=np.float32)

        if len(df_raw) != emb_raw.shape[0]:
            raise ValueError(
                f"Row count mismatch: CSV has {len(df_raw)} rows but "
                f"embeddings have {emb_raw.shape[0]} vectors."
            )

        # Drop duplicate titles (same movie can appear multiple times in the
        # raw CSV).  keep="first" preserves the embedding-index alignment so
        # we can slice emb_raw with the same boolean mask.
        keep: np.ndarray = ~df_raw.duplicated(subset=["title"], keep="first").to_numpy()
        n_dupes = int((~keep).sum())
        if n_dupes:
            logger.info("Removed %d duplicate title rows from dataset.", n_dupes)

        self._df: pd.DataFrame = df_raw[keep].reset_index(drop=True)
        self._embeddings: np.ndarray = emb_raw[keep]

        # --- Improvement 1: precompute lowercase genre strings once ----------
        # Avoids repeated .str.lower() / case=False overhead on every query.
        # regex=False in _filter_dataset then enables fast literal matching.
        self._genres_lower: pd.Series = self._df["genres"].str.lower().fillna("")

        # --- Improvement 2: expose device for horizontal scaling -------------
        # Pass device to SentenceTransformer so callers can pin CPU replicas
        # in multi-worker deployments or leverage GPU when available.
        logger.info("Loading SentenceTransformer model: %s (device=%s)", model_name, device or "auto")
        self._model: SentenceTransformer = SentenceTransformer(model_name, device=device)

        logger.info(
            "MovieRecommender ready — %d movies, embedding dim %d, device=%s",
            len(self._df),
            self._embeddings.shape[1],
            device or "auto",
        )

    # ------------------------------------------------------------------
    # Query parsing helpers
    # ------------------------------------------------------------------

    def _detect_language(self, query: str) -> Optional[str]:
        """Return an ISO 639-1 language code if a language keyword is found
        in *query*, otherwise ``None``.

        Examples
        --------
        >>> self._detect_language("funny movies in hindi")
        'hi'
        """
        q_lower = query.lower()
        for keyword, code in _LANGUAGE_MAP.items():
            # Whole-word match to avoid "english" partially matching other words
            if re.search(rf"\b{keyword}\b", q_lower):
                return code
        return None

    def _detect_genre(self, query: str) -> Optional[str]:
        """Return a canonical genre string (title-case) by checking direct
        genre names first, then mood synonyms as a fallback.

        Direct genre keywords take priority over mood words so that a query
        like "exciting science fiction" resolves to ``Science Fiction`` rather
        than being hijacked by the mood mapping to ``Action``.

        Returns ``None`` if no genre/mood signal is found.

        Examples
        --------
        >>> self._detect_genre("I feel sad, recommend something")
        'Drama'
        >>> self._detect_genre("top action movies")
        'Action'
        >>> self._detect_genre("exciting science fiction")
        'Science Fiction'
        """
        q_lower = query.lower()

        # 1. Direct genre name match (higher priority — user is explicit)
        for genre in _SUPPORTED_GENRES:
            if re.search(rf"\b{re.escape(genre.lower())}\b", q_lower):
                return genre

        # 2. Mood-based mapping (fallback when no genre keyword is present)
        for mood_word, genre in _MOOD_MAP.items():
            if re.search(rf"\b{re.escape(mood_word)}\b", q_lower):
                return genre

        return None

    def _extract_rating_threshold(self, query: str) -> Optional[float]:
        """Extract a minimum IMDb rating from natural-language expressions.

        Supported forms: "above 8", "over 7.5", "minimum 7",
        "greater than 8 imdb", "at least 6.5".

        Returns the threshold as a ``float``, or ``None`` if not found.
        """
        match = _RATING_RE.search(query)
        if match:
            return float(match.group(1))
        return None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _filter_dataset(
        self,
        language: Optional[str],
        genre: Optional[str],
        rating_threshold: Optional[float],
    ) -> Tuple[pd.DataFrame, np.ndarray, bool]:
        """Apply language, genre, and rating filters to the movie dataset.

        If the resulting pool has fewer than ``_MIN_FILTER_SIZE`` movies the
        filter is abandoned and the full dataset is returned (with a warning).

        Returns
        -------
        filtered_df : pd.DataFrame
            Subset of ``self._df`` matching the filter criteria.
        filtered_embeddings : np.ndarray
            Corresponding embedding rows (same positional order as *filtered_df*).
        fallback : bool
            ``True`` when the filter pool was too small and the full dataset
            is returned instead.  Callers use this to suppress misleading
            filter-specific text in result explanations.
        """
        mask = np.ones(len(self._df), dtype=bool)

        if language is not None:
            mask &= (self._df["original_language"] == language).to_numpy()

        if genre is not None:
            # --- Improvement 1 payoff: hit the precomputed lowercase Series --
            # regex=False → literal substring match, skips regex compilation.
            mask &= (
                self._genres_lower
                .str.contains(genre.lower(), regex=False)
                .to_numpy()
            )

        if rating_threshold is not None:
            mask &= (self._df["averageRating"] >= rating_threshold).to_numpy()

        n_filtered = int(mask.sum())
        if n_filtered < _MIN_FILTER_SIZE:
            logger.warning(
                "Filter returned only %d movies (minimum=%d). "
                "Falling back to full dataset.",
                n_filtered,
                _MIN_FILTER_SIZE,
            )
            return self._df, self._embeddings, True

        idx = np.where(mask)[0]
        return self._df.iloc[idx], self._embeddings[idx], False

    # ------------------------------------------------------------------
    # Query encoding
    # ------------------------------------------------------------------

    def _encode_query(self, query: str) -> np.ndarray:
        """Encode *query* into a normalised 384-d vector using the loaded
        SentenceTransformer model.

        The vector is L2-normalised so that a dot product with the
        precomputed (also normalised) movie embeddings equals cosine
        similarity.

        Returns
        -------
        np.ndarray
            1-D float32 array of shape ``(384,)``.
        """
        vec = self._model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vec[0].astype(np.float32)

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _minmax_normalize(arr: np.ndarray) -> np.ndarray:
        """Scale *arr* to [0, 1] within its own range.

        When all values are identical (zero variance) every element is mapped
        to 0.5 so the component contributes a neutral equal weight to all
        candidates rather than collapsing to zero or one.
        """
        lo, hi = arr.min(), arr.max()
        if hi > lo:
            return (arr - lo) / (hi - lo)
        return np.full_like(arr, 0.5, dtype=np.float32)

    # ------------------------------------------------------------------
    # Improvement 3 — Diversity re-ranking
    # ------------------------------------------------------------------

    def _rerank_for_diversity(
        self,
        final_scores: np.ndarray,
        filtered_df: pd.DataFrame,
        top_k: int,
        genre_penalty: float = 0.05,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Greedy diversity re-ranking that penalises repeated primary genres.

        Operates over a candidate pool of ``min(top_k * 3, n)`` movies so
        that genre variety has room to surface without drifting far from
        the highest-scoring candidates.

        For each greedily selected movie, a *genre_penalty* is subtracted
        from the score of every subsequent movie that shares the same
        primary genre.  The final selection is re-sorted by adjusted score so
        the output ordering still reflects quality within the diverse set.

        Parameters
        ----------
        final_scores : np.ndarray
            1-D score array aligned with *filtered_df* rows (shape ``(n,)``).
        filtered_df : pd.DataFrame
            Filtered movie pool (positional alignment with *final_scores*).
        top_k : int
            Number of diverse results to return.
        genre_penalty : float
            Per-occurrence score deduction for repeating a primary genre.

        Returns
        -------
        local_idx : np.ndarray
            Positional indices (into *filtered_df* / *final_scores*) of the
            selected movies, ordered by adjusted score descending.
        adj_scores : np.ndarray
            Diversity-adjusted scores for each entry in *local_idx*.
        """
        pool_size = min(top_k * 3, len(final_scores))

        # O(n) partial sort to isolate the candidate pool, then full sort
        # only the small pool slice — avoids a full argsort on 14k items.
        pool_local = np.argpartition(final_scores, -pool_size)[-pool_size:]
        pool_local = pool_local[np.argsort(final_scores[pool_local])[::-1]]

        # Primary genre = first token of the comma-separated genres string
        raw_genres    = filtered_df["genres"].iloc[pool_local].fillna("").tolist()
        primary_genres = [g.split(",")[0].strip().lower() for g in raw_genres]

        selected_local: list[int]   = []
        selected_adj:   list[float] = []
        genre_counts:   dict[str, int] = {}

        for local_i, pg in zip(pool_local.tolist(), primary_genres):
            if len(selected_local) >= top_k:
                break
            count      = genre_counts.get(pg, 0)
            adj        = float(final_scores[local_i]) - genre_penalty * count
            selected_local.append(local_i)
            selected_adj.append(adj)
            genre_counts[pg] = count + 1

        # Re-sort the selected pocket by adjusted score (quality within diversity)
        order = np.argsort(selected_adj)[::-1]
        return (
            np.array(selected_local, dtype=np.intp)[order],
            np.array(selected_adj,   dtype=np.float32)[order],
        )

    # ------------------------------------------------------------------
    # Improvement 4 — Explainability
    # ------------------------------------------------------------------

    def _build_explanation(
        self,
        semantic: float,
        rating_score: float,
        popularity_score: float,
        avg_rating: float,
        genre: Optional[str],
        language: Optional[str],
    ) -> str:
        """Generate a short heuristic explanation for a recommendation.

        Identifies the dominant weighted score contributor and annotates it
        with any active query filters to surface intent alignment.

        Parameters
        ----------
        semantic : float
            Raw cosine similarity for this movie.
        rating_score : float
            Normalised IMDb rating score (0–1).
        popularity_score : float
            Normalised log-popularity score (0–1).
        avg_rating : float
            Raw IMDb ``averageRating`` value (e.g. 8.3).
        genre : str or None
            Genre filter active for this query, if any.
        language : str or None
            ISO 639-1 language code filter active for this query, if any.

        Returns
        -------
        str
            Human-readable explanation, e.g.
            ``"Strong match to your query · Comedy genre · English film"``.
        """
        sem_contrib = _W_SEMANTIC   * semantic
        rat_contrib = _W_RATING     * rating_score
        pop_contrib = _W_POPULARITY * popularity_score

        dominant = max(
            ("semantic",   sem_contrib),
            ("rating",     rat_contrib),
            ("popularity", pop_contrib),
            key=lambda x: x[1],
        )[0]

        if dominant == "semantic":
            lead = "Strong match to your query"
        elif dominant == "rating":
            lead = f"Highly rated · {avg_rating:.1f}/10 on IMDb"
        else:
            lead = "Widely popular pick"

        tags = [lead]
        if genre:
            tags.append(f"{genre} genre")
        if language:
            tags.append(f"{_LANG_DISPLAY.get(language, language.upper())} film")

        return " · ".join(tags)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_movie_overview(self, title: str) -> Optional[str]:
        """Return the ``overview`` text for a movie by exact title match.

        Parameters
        ----------
        title : str
            Exact movie title as stored in the dataset.

        Returns
        -------
        str or None
            The overview string, or ``None`` if the title is not found or
            the column is missing.
        """
        if "overview" not in self._df.columns:
            return None
        matches = self._df.loc[self._df["title"] == title, "overview"]
        if matches.empty:
            return None
        value = matches.iloc[0]
        return str(value) if value and str(value) != "nan" else None

    def recommend(
        self,
        query: str,
        top_k: int = 10,
        semantic_query: Optional[str] = None,
    ) -> pd.DataFrame:
        """Return the top-*k* movie recommendations for a natural-language
        *query*.

        The method:

        1. Parses the query for language, genre/mood, and rating signals.
        2. Filters the dataset (with automatic fallback on sparse results).
        3. Encodes the query with the sentence transformer.
        4. Computes a hybrid final score for every candidate movie.
        5. Re-ranks for genre diversity.
        6. Annotates each result with a heuristic explanation.

        Parameters
        ----------
        query : str
            Natural-language movie request used for filter extraction.
        top_k : int
            Number of recommendations to return (default: 10).
        semantic_query : str, optional
            If provided, used *only* for the embedding/semantic-search step
            while *query* is still used for filter extraction (language, genre,
            rating threshold).  Pass an LLM-expanded version of the query to
            improve semantic recall without losing structured filter signals.

        Returns
        -------
        pd.DataFrame
            Columns: ``title``, ``genres``, ``averageRating``,
            ``final_score``, ``why``.
            Sorted by diversity-adjusted score descending, index reset.

        Examples
        --------
        >>> results = recommender.recommend("scary korean movies")
        >>> print(results[["title", "final_score", "why"]].to_string())
        """
        if not query or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        # --- 1. Parse query signals ---
        language         = self._detect_language(query)
        genre            = self._detect_genre(query)
        rating_threshold = self._extract_rating_threshold(query)

        logger.debug(
            "Parsed query=%r → language=%r, genre=%r, rating_threshold=%r",
            query, language, genre, rating_threshold,
        )

        # --- 2. Filter dataset ---
        filtered_df, filtered_embeddings, fallback = self._filter_dataset(
            language, genre, rating_threshold
        )
        # When fallback is active, filter-specific tags in explanations would
        # be misleading (e.g. "Korean film" when Korean pool was too small).
        explain_genre    = None if fallback else genre
        explain_language = None if fallback else language

        # --- 3. Encode query ---
        # Use semantic_query (LLM-expanded) when available for better recall;
        # fall back to the original query for pure local inference.
        encode_text = semantic_query.strip() if semantic_query and semantic_query.strip() else query
        query_vec = self._encode_query(encode_text)  # shape (384,)

        # --- 4. Compute hybrid scores (pure numpy — no DataFrame mutation) ---
        # Cosine similarity via dot product (both sides are L2-normalised)
        semantic_scores   = filtered_embeddings @ query_vec                      # (n,)
        rating_scores     = filtered_df["rating_score"].to_numpy(dtype=np.float32)
        popularity_scores = filtered_df["popularity_score"].to_numpy(dtype=np.float32)

        # Normalise each component within this pool so every signal competes
        # on a flat 0–1 scale.  Without this, rating_score's built-in floor
        # (~0.65 minimum) and popularity outliers drown out the semantic signal
        # and the same globally popular movies appear regardless of the query.
        sem_norm = self._minmax_normalize(semantic_scores)
        rat_norm = self._minmax_normalize(rating_scores)
        pop_norm = self._minmax_normalize(popularity_scores)

        final_scores = (
            _W_SEMANTIC    * sem_norm
            + _W_RATING    * rat_norm
            + _W_POPULARITY * pop_norm
        )

        # --- 5. Diversity re-ranking (Improvement 3) ---
        top_local_idx, _ = self._rerank_for_diversity(final_scores, filtered_df, top_k)

        # --- 6. Build result DataFrame (no mutation of self._df) ---
        result_rows     = filtered_df.iloc[top_local_idx]
        # Use normalised component values for explanation so dominant-contributor
        # logic reflects the same scale used for ranking.
        sem_vals        = sem_norm[top_local_idx]
        rat_vals        = rat_norm[top_local_idx]
        pop_vals        = pop_norm[top_local_idx]
        avg_rating_vals = result_rows["averageRating"].to_numpy(dtype=np.float32)

        result = result_rows[["title", "genres", "averageRating"]].copy()
        result["final_score"] = np.round(final_scores[top_local_idx], 6)

        # Explanation column (Improvement 4) — loop only over top_k items.
        # Use explain_genre / explain_language (None when fallback is active)
        # so we never claim a movie matches a filter that wasn't actually applied.
        result["why"] = [
            self._build_explanation(s, r, p, a, explain_genre, explain_language)
            for s, r, p, a in zip(sem_vals, rat_vals, pop_vals, avg_rating_vals)
        ]

        result = result.reset_index(drop=True)
        return result


# ---------------------------------------------------------------------------
# Entry point / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    # Resolve paths relative to this file regardless of cwd
    _base_dir        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _csv_path        = os.path.join(_base_dir, "data",   "tier1_clean_movies.csv")
    _embeddings_path = os.path.join(_base_dir, "models", "tier1_movie_embeddings.pkl")

    recommender = MovieRecommender(
        csv_path=_csv_path,
        embeddings_path=_embeddings_path,
    )

    test_queries = [
        "suggest funny movies in english above 8 imdb",
        "romantic hindi movies",
        "scary korean horror films",
        "sad drama with high ratings",
        "exciting science fiction",
    ]

    for q in test_queries:
        print(f"\n{'=' * 70}")
        print(f"Query: {q!r}")
        print("=" * 70)
        try:
            results = recommender.recommend(q, top_k=5)
            print(results.to_string(index=False))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
