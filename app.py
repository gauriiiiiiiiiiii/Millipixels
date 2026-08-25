import streamlit as st

import evaluate
from config import CORPUS_DIR, TOP_K
from qa import answer, backend_name, get_index

st.set_page_config(page_title="Meridian Handbook Q&A", page_icon="📦", layout="wide")


# the index is built once and reused across reruns
@st.cache_resource
def index():
    return get_index()


@st.cache_data
def questions():
    return evaluate.load_questions()


@st.cache_data
def raw_doc(doc):
    return (CORPUS_DIR / f"{doc}.md").read_text(encoding="utf-8")


chunks = index().chunks
docs = sorted({c["doc"] for c in chunks})

with st.sidebar:
    st.subheader("Setup")
    st.write("**Answering with**")
    st.code(backend_name(), language=None)
    a, b = st.columns(2)
    a.metric("Documents", len(docs))
    b.metric("Chunks", len(chunks))
    k = st.slider("Chunks sent to the model", 1, 10, TOP_K)
    st.caption(
        "Without an API key the tool quotes the best matching chunk instead of "
        "composing an answer, so results are weaker than the numbers in note.txt."
    )

st.title("Meridian Handbook Q&A")
st.caption("Answers come only from the handbook, with a citation. Otherwise it refuses.")

ask_tab, eval_tab, retrieval_tab, corpus_tab = st.tabs(
    ["Ask", "Evaluation", "Retrieval", "Corpus"]
)


def show_answer(res):
    if res["supported"]:
        st.success(res["answer"])
    else:
        st.warning(res["answer"] or "I couldn't find this in the handbook.")

    if res["citations"]:
        st.write("**Cited**  " + "  ".join(f"`{c}`" for c in res["citations"]))
    else:
        st.caption("No citation — nothing in the handbook supported an answer.")


def show_hits(hits):
    for h in hits:
        st.markdown(f"**{h['doc']}** &nbsp; score {h['score']:.2f}")
        st.text(h["text"])
        st.divider()


with ask_tab:
    # clicking a sample question fills the box below
    st.write("**Sample questions**")
    cols = st.columns(4)
    for i, q in enumerate(questions()):
        label = q["id"] if q["answerable"] else f"{q['id']} (unanswerable)"
        if cols[i % 4].button(label, help=q["question"], width="stretch"):
            st.session_state["question"] = q["question"]

    question = st.text_input(
        "Question", key="question", placeholder="What is the fuel surcharge for Zone 4?"
    )

    if question:
        with st.spinner("Searching the handbook..."):
            res = answer(question, k)
        show_answer(res)
        hits = index().search(question, k)
        with st.expander(f"Retrieved chunks ({len(hits)})"):
            show_hits(hits)

with eval_tab:
    st.write(
        "Runs all eight sample questions through `answer()` and checks each one: "
        "answerable questions must be supported and cite the expected document, "
        "the unanswerable one must be refused."
    )

    if st.button("Run evaluation", type="primary"):
        bar = st.progress(0.0, text="Starting...")
        total = len(questions())
        done = []

        def tick(row):
            done.append(row)
            bar.progress(len(done) / total, text=f"{row['id']} — {row['verdict']}")

        rows = evaluate.run(k=k, on_result=tick)
        bar.empty()
        st.session_state["eval"] = evaluate.save(rows)

    results = st.session_state.get("eval") or evaluate.load()

    if not results:
        st.info("No results yet. Click **Run evaluation**, or run `python run_eval.py`.")
    else:
        s = results["summary"]
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Answered and cited correctly", f"{s['answerable_ok']}/{s['answerable']}"
        )
        c2.metric(
            "Refused correctly", f"{s['unanswerable_ok']}/{s['unanswerable']}"
        )
        c3.metric("Model", results["backend"])
        st.caption(f"Last run {results['ran_at']}")

        st.dataframe(
            [
                {
                    "id": r["id"],
                    "ok": r["ok"],
                    "question": r["question"],
                    "cited": ", ".join(r["citations"]) or "—",
                    "expected doc": r.get("expected_doc") or "—",
                    "verdict": r["verdict"],
                }
                for r in results["rows"]
            ],
            hide_index=True,
            width="stretch",
        )

        for r in results["rows"]:
            icon = "✅" if r["ok"] else "❌"
            with st.expander(f"{icon} {r['id']} — {r['question']}"):
                st.write("**Expected**")
                st.write(r["expected_answer"])
                st.write("**Got**")
                st.write(r["got"])
                st.caption(
                    f"cited {r['citations'] or 'nothing'} · "
                    f"supported={r['supported']} · {r['verdict']}"
                )

with retrieval_tab:
    st.write("BM25 only, no model call — useful for checking whether the right document comes up at all.")
    rq = st.text_input(
        "Question", key="retrieval_q", placeholder="What are the dock hours in Newark?"
    )

    if rq:
        hits = index().search(rq, k)
        st.dataframe(
            [
                {
                    "rank": i + 1,
                    "score": round(h["score"], 2),
                    "document": h["doc"],
                    "chunk": h["text"].replace("\n", " ")[:110],
                }
                for i, h in enumerate(hits)
            ],
            hide_index=True,
            width="stretch",
        )
        with st.expander("Full chunk text"):
            show_hits(hits)

with corpus_tab:
    st.info(
        "Two things to know about this corpus: `escalation-policy-v2` is deprecated "
        "and contradicts `v3`, and `comms-templates` contains a prompt injection. "
        "Both are handled in the system prompt, not by editing the documents."
    )

    doc = st.selectbox("Document", docs)
    doc_chunks = [c for c in chunks if c["doc"] == doc]
    st.caption(f"{len(doc_chunks)} chunks")

    for i, c in enumerate(doc_chunks, 1):
        with st.expander(f"Chunk {i} — {c['text'].splitlines()[0][:70]}"):
            st.text(c["text"])

    with st.expander("Raw markdown"):
        st.code(raw_doc(doc), language="markdown")
