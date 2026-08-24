# Meridian Handbook Q&A

Ask a question about the Meridian support handbook and get an answer with a
citation. It searches the docs, sends the best passages to an LLM, and answers
only from what it finds. If the handbook doesn't cover something, it says so
instead of guessing.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Put a free API key in `.env`, either `GROQ_API_KEY` (from console.groq.com) or
`GEMINI_API_KEY` (from aistudio.google.com/apikey). The tool loads `.env` on its
own and uses whichever it finds. With no key it still runs and just quotes the
best matching passage, which is handy for checking retrieval.

Default model is `openai/gpt-oss-120b`; set `RAG_MODEL` to switch it.

## Usage

```bash
python main.py "What is the fuel surcharge for Zone 4?"   # ask one question
python main.py --chunks "..."                             # show what was retrieved too
python run_eval.py                                        # run the 8 sample questions
```

## How it works

`corpus_loader.py` splits each markdown file into small chunks. `search.py`
indexes them with BM25 and returns the top matches. `qa.py` sends those to the
model with instructions to answer only from them (and refuse otherwise), and
returns `{answer, citations, supported}`. `run_eval.py` and `main.py` are the
entry points.

See `NOTES.md` for the approach, the test results, and what didn't work at first.
