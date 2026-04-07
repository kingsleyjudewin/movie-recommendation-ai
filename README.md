<div align="center">

# 🎬 CineMind AI

### _Intelligent Movie Recommendations Powered by Hybrid AI_

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br/>

> _"I'm bored. Suggest funny movies in English above 8 IMDb."_  
> **CineMind understands your mood, not just keywords.**

<br/>

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [🏗️ Architecture](#%EF%B8%8F-architecture) · [📡 API Reference](#-api-reference) · [🐳 Docker](#-docker-deployment) · [🤝 Contributing](#-contributing)

</div>

---

## 🧠 The Problem We Solve

Traditional movie recommendation systems rely on **collaborative filtering** (_"users who liked X also liked Y"_) or **content-based filtering** (_matching genres/tags_). While effective at surface level, they suffer from critical limitations:

| ❌ Traditional Systems | ✅ CineMind AI |
|---|---|
| Require explicit ratings or watch history | Works from a **single natural-language sentence** |
| Keyword-match searches miss intent | **Semantic search** understands mood, tone, and themes |
| Cold-start problem for new users | Zero history needed — describe what you _feel_ like watching |
| Same popular movies dominate results | **Diversity re-ranking** ensures variety in every result set |
| No explanation for recommendations | Every result includes a **human-readable "why"** explanation |
| Can't understand "I'm feeling sad" | **Mood-to-genre mapping** translates emotions to film genres |

### 💡 How CineMind is Different

CineMind takes a **hybrid AI approach** — combining the contextual understanding of a **Large Language Model (Groq's Llama 3.1)** with the precision of **sentence-transformer semantic search** and the reliability of **metadata-based scoring**. The result? Movie recommendations that _actually understand_ what you're looking for.

```
💬 "I'm feeling sad, suggest something heartwarming in Korean above 7 IMDb"

   CineMind understands:
   ├── 😢 Mood: Sad → Genre: Drama
   ├── 🇰🇷 Language: Korean → Filter: ko
   ├── ⭐ Rating: Above 7 → Threshold: 7.0
   └── 🔍 Semantic: "heartwarming" → Deep embedding search across 14,737 movies
```

---

## 🏭 Industry Use Cases

CineMind's hybrid recommendation architecture has applications far beyond personal movie discovery:

### 🎥 Streaming Platforms (Netflix, Hulu, Disney+)
Replace rigid category browsing with **conversational movie discovery**. Users describe their mood in natural language, and the engine returns contextually relevant suggestions — no browsing fatigue, higher engagement.

### 📱 OTT & Mobile Entertainment Apps
Integrate CineMind's API as a **microservice** to power "What should I watch?" features. The lightweight FastAPI backend handles 100+ concurrent requests with sub-second latency.

### 🏢 Media & Entertainment Analytics
Use the hybrid scoring engine to **quantify content similarity** across catalogs — useful for content acquisition teams deciding which films to license based on existing library gaps.

### 🎓 Educational & Research Use
CineMind serves as a **production-grade reference implementation** for:
- Sentence-transformer based semantic search
- LLM integration with traditional ML pipelines
- Hybrid scoring with explainability
- Diversity-aware re-ranking algorithms

### 🛒 E-Commerce & Content Discovery
The architecture (semantic search + metadata filtering + diversity re-ranking) is directly transferable to **product recommendations**, **music discovery**, **book suggestions**, and any domain where natural-language intent matters.

---

## ✨ Features

### 🔍 Intelligent Search
- **Natural Language Understanding** — Describe your mood, preferences, and constraints in plain English
- **LLM Query Expansion** — Groq's Llama 3.1 enriches your query into a detailed semantic description for better matching
- **Multi-signal Filtering** — Automatically extracts language, genre, mood, and rating constraints from your query

### 🤖 Hybrid AI Engine
- **Semantic Search** — `all-MiniLM-L6-v2` sentence-transformer encodes queries against 14,737 precomputed movie embeddings
- **Hybrid Scoring** — `0.45 × semantic + 0.35 × rating + 0.20 × popularity` (all min-max normalised per pool)
- **Diversity Re-ranking** — Greedy genre-diversity algorithm prevents same-genre domination in results
- **Explainability** — Every recommendation includes a "why" explanation identifying the dominant score contributor

### 🎭 Rich Movie Details
- **AI-Generated Summaries** — Click any movie for a spoiler-free, engaging story description
- **Cast Information** — Groq LLM generates accurate cast lists for each film
- **Genre Tags & IMDb Ratings** — Instant visual context for every recommendation

### 🎨 Premium Frontend Experience
- **Three.js Interactive Background** — Immersive 3D animated canvas
- **Framer Motion Animations** — Smooth transitions, card hover effects, and modal animations
- **Custom Cursor** — Unique cursor interactions that follow card movements
- **Dark Theme** — Elegant, cinema-inspired dark design with glassmorphism panels
- **Fully Responsive** — Seamless experience across desktop, tablet, and mobile

### 🏗️ Production-Ready Infrastructure
- **Docker Multi-Stage Build** — Optimised container with frontend pre-built into static assets
- **Docker Compose** — One-command local deployment
- **Cloud-Ready** — Procfile for Heroku, Render, Railway, and Fly.io
- **Health Checks** — Built-in `/health` endpoint for monitoring and orchestration
- **CORS Configuration** — Flexible origin controls for multi-domain deployments

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CineMind AI                              │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │   React +    │    │   FastAPI    │    │  Recommendation   │  │
│  │   Vite SPA   │◄──►│   Backend    │◄──►│     Engine        │  │
│  │              │    │              │    │                   │  │
│  │  • Three.js  │    │  • REST API  │    │ • Sentence-BERT   │  │
│  │  • Framer    │    │  • Groq LLM  │    │ • Hybrid Scoring  │  │
│  │  • Tailwind  │    │  • CORS      │    │ • Diversity Rank  │  │
│  │  • shadcn/ui │    │  • Pydantic  │    │ • Explainability  │  │
│  └──────────────┘    └──────────────┘    └───────────────────┘  │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │  Groq Cloud  │    │  Movie CSV   │    │  Precomputed      │  │
│  │  (Llama 3.1) │    │  (14,737     │    │  Embeddings       │  │
│  │              │    │   movies)    │    │  (384-dim, L2     │  │
│  │  • Query     │    │              │    │   normalised)     │  │
│  │    Expansion │    │  • Titles    │    │                   │  │
│  │  • Movie     │    │  • Genres    │    │  Cosine sim via   │  │
│  │    Details   │    │  • Ratings   │    │  dot product      │  │
│  └──────────────┘    └──────────────┘    └───────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Recommendation Pipeline

```
User Query: "I'm bored, suggest funny movies in English above 8 IMDb"
    │
    ▼
┌─── Step 1: LLM Query Expansion (Groq) ───────────────────────┐
│                                                                │
│  Original: "I'm bored, suggest funny movies..."               │
│  Expanded: "Light-hearted comedies with witty dialogue,        │
│            slapstick humor, and feel-good stories that lift     │
│            the spirits with laughter and entertainment..."     │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── Step 2: Filter Extraction (Rule-based parser) ─────────────┐
│                                                                │
│  Language: English → "en"                                      │
│  Genre:    "bored" → Comedy (mood mapping)                     │
│  Rating:   "above 8" → threshold ≥ 8.0                        │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── Step 3: Semantic Scoring ──────────────────────────────────┐
│                                                                │
│  Expanded query → all-MiniLM-L6-v2 → 384-dim vector           │
│  Dot product against 14,737 precomputed movie embeddings       │
│  (L2-normalised → dot product = cosine similarity)             │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── Step 4: Hybrid Scoring (per-pool normalised) ──────────────┐
│                                                                │
│  final_score = 0.45 × norm(semantic_similarity)                │
│              + 0.35 × norm(imdb_rating_score)                  │
│              + 0.20 × norm(popularity_score)                   │
│                                                                │
│  Min-max normalisation within the filtered pool ensures each   │
│  signal uses its full 0–1 range regardless of absolute scale.  │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── Step 5: Diversity Re-ranking ──────────────────────────────┐
│                                                                │
│  Greedy selection from top 3×k candidates.                     │
│  Each repeat of a primary genre incurs a −0.05 penalty.        │
│  Final set re-sorted by adjusted score.                        │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─── Step 6: Explainability ────────────────────────────────────┐
│                                                                │
│  Each result annotated with dominant contributor:              │
│  • "Strong match to your query · Comedy genre · English film"  │
│  • "Highly rated · 8.7/10 on IMDb · Comedy genre"             │
└────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
cinemind-ai/
├── 🐍 api/
│   ├── __init__.py
│   └── main.py                     # FastAPI backend — endpoints, Groq integration
├── 🤖 recommender/
│   ├── __init__.py
│   └── engine.py                   # 656-line hybrid recommendation engine
├── ⚙️ config.py                    # Centralised Pydantic settings + .env loader
├── 📊 data/
│   └── tier1_clean_movies.csv      # 14,737 curated movies (~18 MB)
├── 🧠 models/
│   └── tier1_movie_embeddings.pkl  # Precomputed 384-d embeddings (~22 MB)
├── 🎨 frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Index.tsx           # Main page — query + results + modal
│   │   ├── components/
│   │   │   ├── HeroSection.tsx     # Title + subtitle hero
│   │   │   ├── QueryBox.tsx        # Natural-language search input
│   │   │   ├── MovieCard.tsx       # Animated movie result card
│   │   │   ├── MovieDetailModal.tsx# AI-generated story + cast modal
│   │   │   ├── ResultGrid.tsx      # Responsive results grid
│   │   │   ├── ThreeBackground.tsx # Interactive 3D canvas
│   │   │   ├── CustomCursor.tsx    # Custom cursor effects
│   │   │   └── ui/                 # shadcn/ui component library
│   │   └── ...
│   ├── package.json
│   ├── vite.config.ts              # Vite config with API proxy
│   └── tailwind.config.ts
├── 🐳 Dockerfile                   # Multi-stage build (Node + Python)
├── 🐳 docker-compose.yml           # One-command container orchestration
├── ☁️ Procfile                     # Cloud platform deployment (Heroku/Render)
├── 🔧 .env.example                 # Environment template
├── 📋 requirements.txt             # Python dependencies
├── 🪟 start.bat                    # Windows dev startup script
├── 🐧 start.sh                    # Linux/macOS dev startup script
├── 📄 CONTRIBUTING.md              # Contribution guidelines
└── 📄 LICENSE                      # MIT License
```

---

## 🚀 Quick Start

### Prerequisites

| Tool       | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+   | Backend engine + API server |
| **Node.js**| 18+     | Frontend build toolchain |
| **npm**    | 9+      | Package management |

### 1️⃣ Clone & Configure

```bash
git clone https://github.com/KINGHACKERjudewin/movie-recoomender.git
cd movie-recoomender

# Create your environment file
copy .env.example .env    # Windows
cp .env.example .env      # macOS / Linux
```

### 2️⃣ Get Your Free Groq API Key

1. Visit **[console.groq.com/keys](https://console.groq.com/keys)** (free account)
2. Click **"Create API Key"**
3. Add it to your `.env` file:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

> ⚠️ **Important**: Without a valid Groq API key, the LLM-powered features (query expansion, movie summaries, and cast lists) will fall back to basic local inference.

### 3️⃣ Install Dependencies

```bash
# Python backend
pip install -r requirements.txt

# React frontend
cd frontend && npm install && cd ..
```

### 4️⃣ Launch! 🚀

**Option A — One Command (Windows):**
```bat
start.bat
```

**Option B — One Command (macOS/Linux):**
```bash
bash start.sh
```

**Option C — Manual (two terminals):**

| Terminal | Command | URL |
|----------|---------|-----|
| Backend  | `uvicorn api.main:app --reload --port 8000` | `http://localhost:8000` |
| Frontend | `cd frontend && npm run dev` | `http://localhost:8081` |

🎬 Open **http://localhost:8081** and start discovering movies!

---

## 📡 API Reference

### `GET /health`
Liveness probe for monitoring and orchestration.

```json
{
  "status": "ok",
  "model_loaded": true,
  "groq_ready": true
}
```

---

### `POST /recommend`
Get top-N movie recommendations from a natural-language query.

**Request:**
```json
{
  "query": "funny English movies about friendship above 8 IMDb",
  "top_k": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "The Grand Budapest Hotel",
      "genres": ["Comedy", "Drama"],
      "averageRating": 8.1,
      "finalScore": 0.8742,
      "why": "Strong match to your query · Comedy genre · English film"
    }
  ],
  "query": "funny English movies about friendship above 8 IMDb",
  "enhancedQuery": "Light-hearted comedies centered around deep bonds of friendship..."
}
```

---

### `GET /movie/details?title=...`
AI-generated story summary and cast list for a specific movie.

**Request:**
```
GET /movie/details?title=Forrest%20Gump
```

**Response:**
```json
{
  "title": "Forrest Gump",
  "summary": "A man with a remarkably low IQ achieves extraordinary things in life...",
  "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"]
}
```

> 💡 Results are **LRU-cached** per process — clicking the same movie twice doesn't re-hit the Groq API.

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
docker compose up --build
```

Visit **http://localhost:8000** — frontend and API served from a single process.

### Manual Docker Build

```bash
docker build -t cinemind .

docker run -p 8000:8000 \
    --env-file .env \
    -v ./data:/app/data:ro \
    -v ./models:/app/models:ro \
    cinemind
```

### Production Build (No Docker)

```bash
# 1. Build the React frontend into static assets
cd frontend && npm run build && cd ..

# 2. Start — FastAPI auto-detects frontend/dist and serves the SPA
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Update `ALLOWED_ORIGINS` in `.env` for your production domain:
```env
ALLOWED_ORIGINS=https://cinemind.yourdomain.com
```

---

## 🔑 Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `GROQ_API_KEY` | — | ✅ Yes | Groq API key for LLM features ([free tier available](https://console.groq.com/keys)) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | No | LLM model identifier for Groq inference |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | No | Groq-compatible OpenAI base URL |
| `HOST` | `127.0.0.1` | No | Uvicorn bind address |
| `PORT` | `8000` | No | Uvicorn bind port |
| `ALLOWED_ORIGINS` | `localhost:8080,8081,4173` | No | Comma-separated CORS origins |

---

## 📊 Data & Model Files

The dataset and precomputed embeddings are **not included in this repository** due to size (~40 MB total).

| File | Location | Size | Description |
|------|----------|------|-------------|
| `tier1_clean_movies.csv` | `data/` | ~18 MB | 14,737 curated movies with titles, genres, ratings, overviews |
| `tier1_movie_embeddings.pkl` | `models/` | ~22 MB | Precomputed `all-MiniLM-L6-v2` 384-d L2-normalised embeddings |

> 📝 These files must be present before starting the server. Contact the project maintainer or generate them using the preprocessing pipeline.

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance async Python API framework |
| [Sentence-Transformers](https://www.sbert.net/) | `all-MiniLM-L6-v2` for semantic movie embeddings |
| [Groq](https://groq.com/) | Ultra-fast LLM inference (Llama 3.1, free tier) |
| [Pydantic Settings](https://docs.pydantic.dev/) | Typed config management with `.env` support |
| [NumPy](https://numpy.org/) | Vectorised cosine similarity via dot product |
| [Pandas](https://pandas.pydata.org/) | Dataset loading, filtering, and result construction |
| [PyTorch](https://pytorch.org/) | Sentence-transformer model runtime |

### Frontend
| Technology | Purpose |
|---|---|
| [React 18](https://react.dev/) | Component-based UI framework |
| [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript |
| [Vite](https://vitejs.dev/) | Lightning-fast dev server + build tool |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first CSS framework |
| [shadcn/ui](https://ui.shadcn.com/) | Accessible, customisable component library |
| [Framer Motion](https://www.framer.com/motion/) | Production-grade animations |
| [Three.js](https://threejs.org/) | 3D interactive WebGL background |
| [Lucide React](https://lucide.dev/) | Beautiful SVG icon library |

### Infrastructure
| Technology | Purpose |
|---|---|
| [Docker](https://www.docker.com/) | Multi-stage containerised deployment |
| [Docker Compose](https://docs.docker.com/compose/) | Single-command orchestration |
| Procfile | Cloud platform deployment (Heroku / Render / Railway) |

---

## 🔬 Technical Deep Dive

### Why Hybrid Scoring?

Pure semantic search struggles with popularity bias — a highly relevant but obscure film can outscore a blockbuster. Pure rating-based systems ignore user intent. CineMind's **weighted hybrid** with **per-pool normalisation** ensures:

- **Semantic relevance** always has the highest weight (45%)
- **Quality signal** from IMDb ratings prevents low-quality matches (35%)
- **Cultural awareness** via popularity catches universally loved films (20%)
- **Per-pool normalisation** prevents any single signal from dominating regardless of its absolute scale

### Why Diversity Re-ranking?

Without diversity control, a query like "suggest action movies" returns 10 action films from the same franchise style. CineMind's **greedy genre-diversity algorithm**:

1. Takes the top `3 × k` candidates by score
2. Greedily selects movies, penalising repeated primary genres (−0.05 per repeat)
3. Re-sorts the final set by adjusted score

This ensures the top-10 results span multiple sub-genres and styles while still prioritising quality.

### Why LLM Query Expansion?

A user query like _"I'm bored"_ contains almost no semantic information for an embedding model. CineMind's Groq-powered query expansion transforms it into a rich 2-3 sentence description that captures themes, mood, pacing, and genre intent — dramatically improving recall quality.

---

## 🧪 Testing

```bash
# Run frontend unit tests
cd frontend && npm test

# Smoke test the recommendation engine
python -m recommender.engine
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)** — free to use, modify, and distribute.

---

<div align="center">

### Built with ❤️ by [KINGHACKERjudewin](https://github.com/KINGHACKERjudewin)

⭐ **Star this repo** if CineMind helped you discover your next favourite movie!

</div>
