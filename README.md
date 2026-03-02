# 🎬 CineMind AI — Intelligent Movie Recommendations

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A hybrid movie recommendation engine that combines **sentence-transformer semantic search** with **Groq LLM query understanding** to suggest films based on natural-language mood queries.

---

## ✨ How It Works

```
User query
    │
    ├─► Groq LLM (llama-3.1-8b-instant)
    │       └─► Expands query into rich semantic description
    │
    ├─► Rule-based parser
    │       └─► Extracts language / genre / rating filters
    │
    └─► Sentence-Transformer (all-MiniLM-L6-v2)
            └─► Encodes expanded query → cosine similarity against 14,737 movies
                    │
                    └─► Hybrid score = 0.45·semantic + 0.35·rating + 0.20·popularity
                                        (all min-max normalised within filtered pool)
```

Clicking any result card fetches a **Groq-generated story summary** and **cast list**.

---

## 📁 Project Structure

```
movie-recoomender/
├── api/
│   ├── __init__.py
│   └── main.py                  # FastAPI backend (recommend + movie details)
├── recommender/
│   ├── __init__.py
│   └── engine.py                # Hybrid recommendation engine
├── config.py                    # Centralised Pydantic settings
├── data/
│   └── tier1_clean_movies.csv   # 14,737 curated movies (not in repo — see below)
├── models/
│   └── tier1_movie_embeddings.pkl  # Pre-computed embeddings (not in repo)
├── frontend/                    # React + Vite + Tailwind frontend
│   ├── src/
│   │   ├── pages/Index.tsx
│   │   ├── components/
│   │   │   ├── MovieCard.tsx
│   │   │   ├── MovieDetailModal.tsx
│   │   │   ├── QueryBox.tsx
│   │   │   ├── ResultGrid.tsx
│   │   │   └── ThreeBackground.tsx
│   │   └── ...
│   └── ...
├── .env.example                 # Environment template — copy to .env
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Docker Compose for local dev
├── Procfile                     # Cloud platform deployment
└── start.bat / start.sh         # One-command dev startup
```

---

## ⚙️ Prerequisites

| Tool       | Version |
|------------|---------|
| Python     | 3.10+   |
| Node.js    | 18+     |
| npm        | 9+      |

---

## 📦 Data & Model Files

The dataset and precomputed embeddings are **not included in this repository** due to their size (~40 MB total). You need to obtain them separately:

| File | Location | Size |
|------|----------|------|
| `tier1_clean_movies.csv` | `data/` | ~18 MB |
| `tier1_movie_embeddings.pkl` | `models/` | ~22 MB |

> **Note**: These files must be present before starting the server. Contact the project maintainer or generate them using the preprocessing pipeline.

---

## 🚀 Setup

### 1. Clone and configure

```bash
git clone https://github.com/KINGHACKERjudewin/movie-recoomender.git
cd movie-recoomender

# Create your environment file
copy .env.example .env    # Windows
cp .env.example .env      # macOS / Linux
```

Edit `.env` and set your **free** Groq API key (get one at [console.groq.com/keys](https://console.groq.com/keys)):

```
GROQ_API_KEY=gsk_...
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

---

## 🖥️ Running in Development

### Option A — One command (Windows)

```bat
start.bat
```

### Option B — One command (macOS / Linux)

```bash
bash start.sh
```

### Option C — Manual (two terminals)

**Terminal 1 — Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **[http://localhost:8081](http://localhost:8081)** in your browser.

---

## 🐳 Docker

### Quick Start

```bash
# Build and run with Docker Compose
docker compose up --build
```

Make sure `data/` and `models/` directories contain the required files — they are mounted as volumes.

### Manual Docker Build

```bash
docker build -t cinemind .
docker run -p 8000:8000 \
    --env-file .env \
    -v ./data:/app/data:ro \
    -v ./models:/app/models:ro \
    cinemind
```

Visit **http://localhost:8000** — frontend and API served from a single process.

---

## 🏭 Production Build

Build the frontend once and serve everything from a single FastAPI process:

```bash
# 1. Build the React app
cd frontend && npm run build && cd ..

# 2. Start the backend (it auto-detects frontend/dist and serves it)
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

For production, update `ALLOWED_ORIGINS` in `.env` to your actual domain:

```
ALLOWED_ORIGINS=https://cinemind.yourdomain.com
```

---

## 📡 API Reference

| Method | Endpoint              | Description                              |
|--------|-----------------------|------------------------------------------|
| `GET`  | `/health`             | Liveness check — returns model + Groq status |
| `POST` | `/recommend`          | Get top-N movie recommendations          |
| `GET`  | `/movie/details?title=...` | AI-generated summary and cast       |

### POST /recommend

```json
{
  "query": "funny English movies about friendship above 8 IMDb",
  "top_k": 10
}
```

Response includes `results[]`, `query`, and `enhancedQuery` (LLM-expanded version).

---

## 🔑 Environment Variables

| Variable          | Default              | Description                                      |
|-------------------|----------------------|--------------------------------------------------|
| `GROQ_API_KEY`    | —                    | **Required** for LLM features (free at console.groq.com) |
| `HOST`            | `127.0.0.1`          | Bind address for uvicorn                         |
| `PORT`            | `8000`               | Bind port for uvicorn                            |
| `ALLOWED_ORIGINS` | localhost dev ports   | Comma-separated CORS origins                     |

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async Python API framework
- [Sentence-Transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2` for semantic embeddings
- [Groq](https://groq.com/) — LLM inference (llama-3.1-8b-instant, free tier)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — typed config management
- NumPy — cosine similarity via dot product on pre-normalised embeddings

**Frontend**
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui components
- Framer Motion — animations
- Three.js — interactive background

**Infrastructure**
- Docker (multi-stage build)
- Docker Compose
- Procfile (Heroku / Render / Railway ready)

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
