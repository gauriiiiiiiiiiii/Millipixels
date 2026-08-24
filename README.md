# Meridian Handbook Q&A

A small retrieval-based question answering tool over the Meridian support
handbook. You ask a question, it searches the handbook, sends the most relevant
passages to an LLM, and answers with a citation. If the handbook doesn't cover
the question, it says so instead of making something up.

## Setup

```bash
pip install -r requirements.txt
```

The answer step uses a free LLM through an OpenAI-compatible API (Groq or Google
Gemini, both free, no card needed). Copy the example env file and add one key:

```bash
cp .env.example .env
```

Then edit `.env` and set either `GROQ_API_KEY` (from https://console.groq.com) or
`GEMINI_API_KEY` (from https://aistudio.google.com/apikey). The tool loads `.env`
automatically and detects which key is present.

If no key is set the tool still runs, but it falls back to quoting the best
matching passage instead of calling a model (handy for checking retrieval without
a key). Override the model with `RAG_MODEL` if you want, e.g.
`RAG_MODEL=llama-3.1-8b-instant`.

## Usage

Ask one question:

```bash
python main.py "What is the fuel surcharge for Zone 4?"
```

Add `--chunks` to also see what the search pulled up and the scores, which is
useful when an answer looks off:

```bash
python main.py --chunks "What are the dock hours at the Newark facility?"
```

Run the eight sample questions and check them against the expected answers:

```bash
python run_eval.py
```

## How it works

- `corpus_loader.py` reads the markdown files and splits each into small chunks
  (one per paragraph / table / list), remembering which file each came from.
- `search.py` builds a BM25 index over those chunks and returns the top matches
  for a question.
- `qa.py` takes the top chunks, hands them to the model with instructions to
  answer only from that text (and to refuse if the answer isn't there), and
  returns `{"answer", "citations", "supported"}`.
- `run_eval.py` runs the sample questions; `main.py` is the command line entry
  point.

The `answer()` function in `qa.py` is the thing to call from code:

```python
from qa import answer
answer("How long does a customer have to file a damage claim?")
# {'answer': '...', 'citations': ['claim-eligibility'], 'supported': True}
```

There's a short write-up of the approach, the test results and a few notes on
what didn't work in `NOTES.md`.
