import argparse
import json
import sys

from config import TOP_K
from qa import answer, get_index

sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Ask the Meridian handbook a question")
    parser.add_argument("question", help="the question to answer")
    parser.add_argument(
        "--chunks", action="store_true", help="show retrieved chunks and scores"
    )
    parser.add_argument(
        "-k", type=int, default=TOP_K, help=f"chunks to retrieve (default {TOP_K})"
    )
    args = parser.parse_args()

    if args.chunks:
        print("Retrieved chunks:")
        for h in get_index().search(args.question, args.k):
            preview = h["text"].replace("\n", " ")
            if len(preview) > 90:
                preview = preview[:90] + "..."
            print(f"  {h['score']:6.2f}  {h['doc']:<24} {preview}")
        print()

    print(json.dumps(answer(args.question, args.k), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
