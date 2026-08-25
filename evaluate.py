import json
from datetime import datetime

from config import QUESTIONS_FILE, RESULTS_FILE
from qa import answer, backend_name


def load_questions():
    return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))


# grade one answer: refused when it should, and cited the document we expected
def grade(q, res):
    if not q["answerable"]:
        if res["supported"]:
            return False, "ANSWERED (should have refused)"
        return True, "refused"

    if not res["supported"]:
        return False, "REFUSED (should have answered)"
    if not res["citations"]:
        return False, "answered with no citation"

    expected_doc = q.get("expected_doc")
    if expected_doc and expected_doc not in res["citations"]:
        return False, f"cited the wrong document (expected {expected_doc})"
    return True, "answered"


# run every question through answer(); on_result is called after each one so a
# caller can show progress
def run(questions=None, k=None, on_result=None):
    rows = []
    for q in questions if questions is not None else load_questions():
        res = answer(q["question"], k) if k else answer(q["question"])
        ok, verdict = grade(q, res)
        row = {
            **q,
            "got": res["answer"],
            "citations": res["citations"],
            "supported": res["supported"],
            "ok": ok,
            "verdict": verdict,
        }
        rows.append(row)
        if on_result:
            on_result(row)
    return rows


def summarize(rows):
    answerable = [r for r in rows if r["answerable"]]
    unanswerable = [r for r in rows if not r["answerable"]]
    return {
        "answerable": len(answerable),
        "answerable_ok": sum(1 for r in answerable if r["ok"]),
        "unanswerable": len(unanswerable),
        "unanswerable_ok": sum(1 for r in unanswerable if r["ok"]),
    }


def save(rows):
    payload = {
        "backend": backend_name(),
        "ran_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": summarize(rows),
        "rows": rows,
    }
    RESULTS_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload


def load():
    if not RESULTS_FILE.exists():
        return None
    try:
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
