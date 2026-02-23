# GEO Genie

A full-stack diagnostic tool for **Generative Engine Optimization (GEO)** — analyzes web pages and scores their visibility to AI search engines like ChatGPT, Perplexity, and Claude.

Built as a Masters AI project exploring how content can be optimized for AI-powered search and retrieval systems.

## Project Structure

```
GeoGenie/
├── frontend/          React 19 + Vite UI
│   ├── src/
│   │   ├── components/   Genie, SearchBar, SpeechBubble, Results
│   │   └── pages/        Citations
│   ├── package.json
│   └── vite.config.js
├── backend/           FastAPI analysis engine
│   ├── analyzers/        11 scoring modules
│   ├── services/         Scraper, scorer, recommender
│   ├── main.py           API endpoints
│   ├── config.py         Settings & scoring weights
│   ├── models.py         SQLAlchemy models
│   └── requirements.txt
├── .env.example       Environment variable template
└── README.md
```

## Features

- URL analysis with real-time scoring (0-100) and letter grade (A-F)
- 11 scoring categories: statistics, citations, quotations, structure, schema, freshness, FAQ, readability, tone, robots, and crawlability
- Actionable recommendations with before/after examples
- Scoring weights derived from peer-reviewed research (Aggarwal et al., KDD 2024)
- Animated genie character with expression states
- Database caching to avoid redundant analysis
- Citations page listing academic references

## Tech Stack

- **Frontend:** React 19, Vite, React Router
- **Backend:** FastAPI, SQLAlchemy, BeautifulSoup4, Playwright
- **Database:** PostgreSQL
- **Styling:** Vanilla CSS with CSS custom properties

## Running Locally

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.11+)
- [PostgreSQL](https://www.postgresql.org/) running locally (or a remote connection string)
- [Playwright browsers](https://playwright.dev/python/docs/intro) (installed in step 3 below)

### 1. Clone and configure

```bash
git clone <repo-url>
cd GeoGenie
cp .env.example .env
```

Edit `.env` with your database connection string and any other overrides.

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can verify with `http://localhost:8000/health`.

### 3. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

### 4. Use the app

Open `http://localhost:5173` in your browser, enter a URL, and the genie will analyze it.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL (frontend) | `http://localhost:8000` |
| `DATABASE_URL` | PostgreSQL connection string (backend) | `postgresql+psycopg2://localhost/neondb` |
| `CACHE_TTL_HOURS` | Hours before re-analyzing the same URL | `24` |
| `REQUEST_TIMEOUT` | Page fetch timeout in seconds | `15` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173,...` |

## Scripts

### Frontend (`cd frontend`)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

### Backend (`cd backend`)

| Command | Description |
|---------|-------------|
| `uvicorn main:app --reload` | Start dev server with auto-reload |
| `uvicorn main:app --host 0.0.0.0` | Start for network access |

## License

Copyright (c) 2025 Grant Finn and Niara Patterson. All Rights Reserved.

This project is source-available for viewing and educational reference only. No permission is granted to copy, modify, distribute, or use this software without prior written consent. See [LICENSE](LICENSE) for details.
