import sys

import evaluate
from qa import backend_name

sys.stdout.reconfigure(encoding="utf-8")


def show(row):
    print(f"{row['id']}: {row['question']}")
    print(f"   expected : {row['expected_answer']}")
    print(f"   got      : {row['got']}")
    print(
        f"   cite     : {row['citations']}  supported={row['supported']}"
        f"  [{row['verdict']}]"
    )
    print()


def main():
    print("Answering with:", backend_name())
    print()

    rows = evaluate.run(on_result=show)
    s = evaluate.summarize(rows)

    print("-" * 60)
    print(
        f"Right document cited on {s['answerable_ok']}/{s['answerable']} "
        "answerable questions"
    )
    print(
        f"Unanswerable questions refused correctly: "
        f"{s['unanswerable_ok']}/{s['unanswerable']}"
    )

    payload = evaluate.save(rows)
    print(f"Saved results for the dashboard to eval_results.json ({payload['ran_at']})")


if __name__ == "__main__":
    main()
