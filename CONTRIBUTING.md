# Contributing to CineMind AI

Thank you for your interest in contributing! Here's how to get started.

---

## Getting Started

1. **Fork** this repository
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/movie-recoomender.git
   cd movie-recoomender
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Groq API key
uvicorn api.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Making Changes

1. Write clean, well-documented code
2. Follow existing code style and conventions
3. Test your changes locally before submitting

## Submitting a Pull Request

1. **Commit** your changes with a clear message:
   ```bash
   git commit -m "feat: add your feature description"
   ```
2. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a **Pull Request** against the `main` branch
4. Describe your changes and link any related issues

## Code Style

- **Python**: Follow PEP 8, use type hints, add docstrings
- **TypeScript/React**: Follow existing ESLint config, use functional components
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) format

## Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include steps to reproduce, expected vs actual behaviour, and your environment

---

Thank you for helping make CineMind better! 🎬
