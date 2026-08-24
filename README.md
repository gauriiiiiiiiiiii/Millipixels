# Meridian Handbook Q&A

I built a small tool that answers questions about the Meridian support handbook
and backs each answer with a citation. It searches the docs, sends the best
passages to an LLM, and answers only from what it finds. When the handbook
doesn't cover something, I make it say so instead of guessing.

## Setup

I install the dependencies and drop in an API key:

```bash
pip install -r requirements.txt
cp .env.example .env
```

I put a free key in `.env`, either `GROQ_API_KEY` (from console.groq.com) or
`GEMINI_API_KEY` (from aistudio.google.com/apikey). The tool loads `.env` itself
and uses whichever it finds. Without a key it still runs and just quotes the best
matching passage, which I used to sanity-check retrieval.

I default to `openai/gpt-oss-120b`, and `RAG_MODEL` switches it.

## Usage

```bash
python main.py "What is the fuel surcharge for Zone 4?"   # ask one question
python main.py --chunks "..."                             # also show what was retrieved
python run_eval.py                                        # run the 8 sample questions
```

## How it works

I split each markdown file into small chunks in `corpus_loader.py`, index them
with BM25 in `search.py`, and in `qa.py` I send the top matches to the model with
instructions to answer only from them (and refuse otherwise), returning
`{answer, citations, supported}`. `run_eval.py` and `main.py` are the entry
points.

I wrote up the approach, the results, and what didn't work at first in `NOTES.md`.
