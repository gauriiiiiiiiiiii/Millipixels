# Meridian Handbook Q&A

I built a small retrieval-based Q&A tool over the Meridian support handbook (16
markdown documents in [corpus/](corpus/)). It searches the docs, sends only the
best passages to an LLM, and answers from those passages alone, with a citation.
When the handbook doesn't cover something, I make it say so instead of guessing.

Every answer comes back as:

```json
{"answer": "...", "citations": ["fuel-surcharge"], "supported": true}
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
```

Then put a free `GROQ_API_KEY` from [console.groq.com](https://console.groq.com)
in `.env`. The tool loads `.env` itself. I default to `openai/gpt-oss-120b` and
`RAG_MODEL` overrides it. Without a key it still runs and just quotes the best
matching passage, which I used to sanity-check retrieval — the answers are
noticeably weaker in that mode, so use a key for a real run.

## Running it

```bash
# ask one question
python main.py "What is the fuel surcharge for Zone 4?"

# also show what was retrieved, and change how many chunks are used
python main.py --chunks "What are the dock hours at the Newark facility?"
python main.py --chunks -k 8 "How long does a customer have to file a damage claim?"

# run all 8 sample questions and grade them
python run_eval.py

# the dashboard
python -m streamlit run app.py
```

I use `python -m streamlit` rather than plain `streamlit`, because on Windows the
Python `Scripts` folder often isn't on `PATH` and the bare command then fails.

The dashboard opens on http://localhost:8501 with four tabs:

- **Ask** — the eight sample questions as buttons plus a free-text box; shows the
  answer, whether it was supported or refused, the citations, and the retrieved
  chunks with their scores.
- **Evaluation** — runs all eight questions and reports how many were answered
  and cited correctly, and whether the unanswerable one was refused. Results are
  saved to `eval_results.json`, so the tab still shows the last run after a
  restart (`python run_eval.py` writes the same file).
- **Retrieval** — BM25 only, no model call. This is where I check whether the
  right document even comes up.
- **Corpus** — every document, chunk by chunk, plus the raw markdown.

The sidebar shows the active model, corpus size, and a slider for how many chunks
reach the model.

## How it works

| File | What it does |
|------|--------------|
| [corpus_loader.py](corpus_loader.py) | Splits each `.md` file into paragraph-sized chunks, keeping a lead-in line (a heading, or a line ending in `:`) attached to the list under it. 16 docs → 69 chunks. |
| [search.py](search.py) | BM25 index (`rank_bm25`) over the chunks; returns the top *k* with scores and the document each came from. |
| [qa.py](qa.py) | `answer(question, k=5)` → `{answer, citations, supported}`. Sends only the retrieved chunks to the model, instructs it to answer from them alone, to refuse otherwise, to ignore instructions found inside documents, and to prefer the non-deprecated of two conflicting docs. Citations are checked against the real filenames in `corpus/` (`.md`, a `source:` prefix and case differences are tolerated) and deduplicated; a refusal carries none, and a supported answer that lost its citation falls back to the retrieved document it overlaps most. |
| [evaluate.py](evaluate.py) | Grading shared by the CLI and the dashboard: an answerable question must be supported *and* cite its `expected_doc`; the unanswerable one must be refused. |
| [main.py](main.py) | CLI for a single question. |
| [run_eval.py](run_eval.py) | Runs the eight sample questions and prints the results. |
| [app.py](app.py) | The Streamlit dashboard. It holds no logic of its own, it calls `qa.answer()`. |

## Test results

With Groq `openai/gpt-oss-120b`, all eight sample questions pass: the seven
answerable ones are answered correctly and cite the expected document, and the
vacation-policy question is refused.

| Q | Verdict | Cited |
|---|---------|-------|
| P1 DIM divisor (166) | answered | dimensional-weight |
| P2 Newark dock hours | answered | facility-directory |
| P3 $100 default liability | answered | declared-value-insurance |
| P4 lithium cells over 100 Wh | answered | hazmat-restrictions |
| P5 21 calendar days | answered | claim-eligibility |
| P6 cross-border documents | answered | customs-documentation |
| P7 Zone 4 is 11.0% | answered | fuel-surcharge |
| P8 vacation policy | refused correctly | — |

I also checked two things the corpus sets up deliberately: the prompt injection in
`comms-templates.md` doesn't hijack the answer even when that document is
retrieved and used, and an escalation-SLA question follows `escalation-policy-v3`
rather than the deprecated `v2`.

I wrote up the approach, what went wrong at first, the conceptual questions, and a
much longer walkthrough of the design and the concepts behind it in
[note.txt](note.txt).
