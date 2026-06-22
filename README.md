# QueryPilot

QueryPilot lets you ask questions about your data in plain English and get accurate SQL back. It works on real schemas with dozens of tables, handles ambiguous questions, and catches its own mistakes before showing you the result.

**Live demo:** https://querypilot-sage.vercel.app

Built as a portfolio project to demonstrate end-to-end AI engineering: schema-aware RAG, iterative self-correction, a full auth system, and a React frontend.

---

## What it can do

**Query any database in plain English**
Type a question like "show me the top 10 customers by total spend last month" and QueryPilot figures out which tables to join, writes the SQL, runs it, and shows you the result. Works against three built-in datasets or any PostgreSQL database you connect.

**Bring your own data**
Upload a CSV or Excel file and it becomes queryable within seconds. QueryPilot creates a table, infers column types, embeds the schema, and makes it available on the query page automatically.

**Connect your own database**
Paste a PostgreSQL connection string and QueryPilot reads your schema from `information_schema`, embeds it, and lets you query it in plain English. Supports multiple connections at once.

**Self-correcting agent**
If the generated SQL fails or returns suspicious results, the agent re-reads the error, adjusts its approach, and tries again up to three times. Most errors get corrected silently before you see anything.

**Charts from results**
Query results are automatically visualized. Bar chart by default, line chart for time-series data, pie chart for small categorical breakdowns. Powered by Recharts with no configuration needed.

**Export and save**
Download any result set as a CSV. Bookmark questions you run often with the star button and rerun them with one click.

**Feedback loop**
Thumbs up or down on any result. Ratings are stored in the database for future fine-tuning or analysis.

---

## Architecture

```
User question
     |
     v
Schema RAG (pgvector + Gemini embeddings)
  Finds the top-k relevant tables and columns for the question

     |
     v
SQL Agent (Groq / LLaMA-3.3-70B)
  Generates SQL using schema context + few-shot examples

     |
     v
Self-Correction Loop (up to 3 iterations)
  Validates syntax, executes in sandbox, feeds errors back to the model

     |
     v
Semantic Scorer
  Checks that the result actually answers the question (0-10 score)

     |
     v
Result + Chart + Export
```

The schema is embedded once per upload or connection using Gemini's `gemini-embedding-001` model and stored in a pgvector table. At query time, only the relevant schema chunks are injected into the prompt, which keeps latency low and prevents context overload on large schemas.

---

## Tech stack

| Layer | What is used |
|---|---|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL + pgvector on Supabase |
| LLM inference | Groq (LLaMA-3.3-70B) |
| Embeddings | Google Gemini (gemini-embedding-001, 768-dim) |
| SQL validation | sqlglot |
| Frontend | React + TypeScript + Tailwind CSS |
| Charts | Recharts |
| Auth | JWT + bcrypt |
| Deployment | Render (API) + Vercel (frontend) |
| Tests | pytest (87 tests) |

---

## Running locally

**Requirements:** Python 3.11+, Node 18+, a Supabase project with pgvector enabled

```bash
git clone https://github.com/PasadKunal/querypilot.git
cd querypilot

python3 -m venv qpvenv
source qpvenv/bin/activate
pip install -r requirements.txt
```

Copy the env template and fill in your keys:

```bash
cp .env.example .env
```

You need:
- `DATABASE_URL`: your Supabase connection string
- `SANDBOX_DATABASE_URL`: read-only Supabase connection string
- `GEMINI_API_KEY`: Google AI Studio key (free at aistudio.google.com)
- `GROQ_API_KEY`: Groq key (free at console.groq.com)
- `JWT_SECRET_KEY`: any long random string for JWT signing

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Run the database migrations:

```bash
psql $DATABASE_URL -f infra/create_app_tables.sql
```

Start the API:

```bash
uvicorn api.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API health check is at `http://localhost:8000/health`.

---

## Deploying your own instance

**Backend on Render (free, no card required)**

1. Sign up at render.com with your GitHub account
2. New > Web Service > connect this repo
3. Render detects `render.yaml` automatically
4. Add environment variables: `DATABASE_URL`, `SANDBOX_DATABASE_URL`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `JWT_SECRET_KEY`, `ALLOWED_ORIGINS`
5. Deploy

**Frontend on Vercel (free, no card required)**

1. Sign up at vercel.com with your GitHub account
2. New Project > connect this repo > set Root Directory to `frontend`
3. Add environment variable: `VITE_API_URL` = your Render service URL
4. Deploy

Once both are live, update `ALLOWED_ORIGINS` on Render to include your Vercel URL so CORS works correctly.

---

## Project structure

```
querypilot/
  api/              FastAPI app, auth, and route handlers
    routes/         Query, upload, connection, and history endpoints
  schema_rag/       pgvector search and schema context assembly
  sql_agent/        SQL generation, validation, and self-correction
  datasets/         CSV processor and schema seed loaders
  frontend/         React app
    src/pages/      Query, Upload, Connections, History pages
    src/components/ ResultChart and Navbar
  infra/            SQL for creating tables and roles
  tests/            87 pytest tests covering routes, agent, and RAG
```

---

## Running tests

```bash
source qpvenv/bin/activate
pytest tests/ -q
```

All external calls (LLM, database, Gemini) are mocked so the tests run offline and fast.

---

## Key design decisions

**Schema RAG over full-schema injection**
Dumping the entire schema into every prompt is slow and hits context limits fast. QueryPilot embeds each table and column separately, then retrieves only the top-k chunks that are semantically relevant to the question. This makes it practical on schemas with 50+ tables.

**Self-correction loop instead of a single shot**
One-shot SQL generation fails too often on real schemas. The agent sees its own errors and retries, which handles typos in table names, missing JOINs, and type mismatches that the model almost always fixes on a second try.

**Read-only sandbox for all SQL execution**
All queries run as a database user with SELECT-only permissions. This makes it safe to connect production read replicas without worrying about accidental writes or deletes.

**Client-side CSV export**
The export button builds the CSV in the browser from the already-loaded result set. No round-trip to the server needed.
