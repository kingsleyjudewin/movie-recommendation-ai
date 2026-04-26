# CineMind — AI Movie Recommender

A hybrid movie recommendation engine that combines semantic vector search with a Groq LLM to deliver natural-language movie discovery. Ask for "a slow-burn psychological thriller set in Japan" and get ranked, explainable results — not just keyword matches.

---

## How It Works

```
User query
    │
    ├─► Groq LLM (llama-3.1-8b-instant)
    │       └─► Expanded semantic description
    │
    ├─► Filter extraction (language · genre · rating threshold)
    │
    └─► sentence-transformers (all-MiniLM-L6-v2)
            └─► Cosine similarity over 14,737 movie embeddings
                    └─► Hybrid score: 0.45·semantic + 0.35·rating + 0.20·popularity
```

Clicking any result opens an AI-generated story summary and cast list, fetched on demand from Groq and cached per session.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| Backend | FastAPI · Uvicorn |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| LLM | Groq API · `llama-3.1-8b-instant` |
| Dataset | 14,737 curated movies (TMDB + IMDb) |

---

## Project Structure

```
movie-recommendation-ai/
├── api/
│   └── main.py              # FastAPI app — /recommend, /movie/details, /health
├── recommender/
│   └── engine.py            # MovieRecommender — hybrid scoring, filter logic
├── frontend/
│   └── src/
│       ├── pages/           # Index page (search + results)
│       └── components/      # MovieCard, MovieDetailModal, ResultGrid
├── data/
│   └── tier1_clean_movies.csv      # 14,737 movies, 33 columns (gitignored)
├── models/
│   └── tier1_movie_embeddings.pkl  # Pre-computed embeddings, shape (14737, 384) (gitignored)
├── config.py                # Pydantic settings (env-driven)
├── requirements.txt
├── .env.example
└── start.bat                # One-click dev startup (Windows)
```

---

## Quickstart

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys)

### 1. Clone & configure

```bash
git clone https://github.com/kingsleyjudewin/movie-recommendation-ai.git
cd movie-recommendation-ai
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Add data files

The dataset and embeddings are not included in the repository. Place them at:

```
data/tier1_clean_movies.csv
models/tier1_movie_embeddings.pkl
```

### 5. Start development servers

**Windows (one command):**
```bat
start.bat
```

**Manual:**
```bash
# Terminal 1 — backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open [http://localhost:8081](http://localhost:8081).

---

## API Endpoints

### `POST /recommend`

Returns ranked movie recommendations for a natural-language query.

**Request body:**
```json
{
  "query": "mind-bending sci-fi with an unreliable narrator",
  "top_k": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Inception",
      "genres": ["Action", "Adventure", "Sci-Fi"],
      "averageRating": 8.8,
      "finalScore": 0.94,
      "why": "..."
    }
  ],
  "query": "mind-bending sci-fi with an unreliable narrator",
  "enhancedQuery": "A complex, cerebral science-fiction film..."
}
```

### `GET /movie/details?title=Inception`

Returns an AI-generated story summary and cast list. Results are LRU-cached per process.

```json
{
  "title": "Inception",
  "summary": "A thief who steals corporate secrets through dream-sharing technology...",
  "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"]
}
```

### `GET /health`

Liveness probe — confirms model and Groq client status.

---

## Configuration

All settings are read from environment variables or `.env`. See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | LLM model for query expansion and details |
| `HOST` | `127.0.0.1` | Uvicorn bind host |
| `PORT` | `8000` | Uvicorn bind port |
| `ALLOWED_ORIGINS` | localhost dev ports | Comma-separated CORS origins |

The app runs without a Groq key — query expansion and AI-generated details fall back to raw dataset content automatically.

---

## Production Build

```bash
cd frontend && npm run build && cd ..
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

FastAPI serves the compiled React SPA from `frontend/dist/` for all non-API routes.

---

## Dataset & Embeddings

| File | Rows | Notes |
|---|---|---|
| `tier1_clean_movies.csv` | 14,737 | Filtered to rating ≥ 6.5; columns include title, genres, overview, averageRating, popularity_score |
| `tier1_movie_embeddings.pkl` | (14737, 384) float32 | L2-normalised; use dot product for cosine similarity |

Language breakdown: English (8,897) · French (894) · Hindi (606) · Japanese (577) · other (3,959).

---

## License

MIT
