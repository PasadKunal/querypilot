# QueryPilot

A production NL-to-SQL agent with schema-aware RAG, iterative self-correction, fine-tuning on collected user feedback, and a deployable multi-turn analytics interface.

> This project is actively under development. Benchmark results and demo will be added as each phase completes.

## What it does

QueryPilot lets non-technical users ask questions in plain English and get reliable SQL back. It is built to work on real schemas (47+ tables, multiple databases) where most NL2SQL tools break.

Core capabilities being built:

- Schema-aware RAG using pgvector so only the relevant tables get injected into the prompt
- A 3-iteration self-correction loop (syntax validation, sandboxed execution, error feedback re-generation)
- Fine-tuned Qwen2.5-Coder-7B on DPO pairs from real user feedback via QLoRA
- Complexity-based model routing to cut inference costs by ~70%
- Multi-turn conversation with schema context persistence
- Business glossary injection for domain-specific accuracy

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL + pgvector (Supabase) |
| Primary LLMs | GPT-4o, Claude 3.5 Sonnet |
| Low-latency inference | Groq (LLaMA-3.1-70B) |
| SQL validation | sqlglot |
| FK graph | NetworkX |
| Fine-tuning | Unsloth + QLoRA (Qwen2.5-Coder-7B) |
| Complexity router | DistilBERT |
| Frontend | React + TypeScript + Monaco Editor |
| Cache | Redis (Upstash) |
| Deployment | Render (API) + Vercel (Frontend) |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/PasadKunal/querypilot.git
cd querypilot

# Create and activate virtual environment
python3 -m venv qpvenv
source qpvenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy the env template and fill in your keys
cp .env.example .env

# Run the API
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`. Check `http://localhost:8000/health` to verify it is running. Interactive docs are at `http://localhost:8000/docs`.

## Project Structure

```
querypilot/
  schema_rag/       Schema embedding, pgvector search, FK graph, prompt assembly
  sql_agent/        SQL generation, validation, execution, self-correction
  fine_tuning/      DPO collection, QLoRA training, complexity classifier, model router
  evaluation/       Spider benchmark runner, MLflow logging, baseline comparisons
  api/              FastAPI app, auth, routes, conversation manager, glossary
  frontend/         React + Monaco Editor UI
  datasets/         Schema SQL files and seed data loaders
  infra/            Dockerfile, docker-compose, postgres roles, CI config
  tests/            Pytest test suite
```

## Benchmark Results

Coming in Phase 5. Target: 81% exact-match on Spider dev set.

| Model | Exact Match | Execution Accuracy |
|---|---|---|
| GPT-4o zero-shot (baseline) | 67% | 74% |
| GPT-4o + static few-shot | 75% | 81% |
| QueryPilot (schema RAG + dynamic few-shot) | TBD | TBD |
| Fine-tuned Qwen2.5-Coder-7B (simple queries) | TBD | TBD |
