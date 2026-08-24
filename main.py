import argparse
import json
import sys

from corpus_loader import load_chunks
from qa import answer
from search import Index

sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Ask the Meridian handbook a question")
    parser.add_argument("question", help="the question to answer")
    parser.add_argument(
        "--chunks", action="store_true", help="show retrieved chunks and scores"
    )
    args = parser.parse_args()

    if args.chunks:
        index = Index(load_chunks())
        print("Retrieved chunks:")
        for h in index.search(args.question):
            preview = h["text"].replace("\n", " ")
            if len(preview) > 90:
                preview = preview[:90] + "..."
            print(f"  {h['score']:6.2f}  {h['doc']:<24} {preview}")
        print()

    print(json.dumps(answer(args.question), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
