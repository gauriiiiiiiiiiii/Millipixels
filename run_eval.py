import json
import sys

from config import QUESTIONS_FILE
from qa import answer, backend_name

sys.stdout.reconfigure(encoding="utf-8")


def main():
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))

    print("Answering with:", backend_name())
    print()

    cited_right = 0
    refused_right = None

    for q in questions:
        res = answer(q["question"])

        if q["answerable"]:
            ok = res["supported"] and len(res["citations"]) > 0
            cited_right += 1 if ok else 0
            tag = "answered" if res["supported"] else "REFUSED (should have answered)"
        else:
            refused_right = not res["supported"]
            tag = "refused" if refused_right else "ANSWERED (should have refused)"

        print(f"{q['id']}: {q['question']}")
        print(f"   expected : {q['expected_answer']}")
        print(f"   got      : {res['answer']}")
        print(
            f"   cite     : {res['citations']}  supported={res['supported']}  [{tag}]"
        )
        print()

    answerable = sum(1 for q in questions if q["answerable"])
    print("-" * 60)
    print(f"Right document cited on {cited_right}/{answerable} answerable questions")
    if refused_right is not None:
        print(f"Unanswerable question refused correctly: {refused_right}")


if __name__ == "__main__":
    main()
