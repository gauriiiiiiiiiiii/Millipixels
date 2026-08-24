import re

from config import CORPUS_DIR


def _is_leadin(text):
    # a heading line or a line ending in ":" introduces the block after it
    return text.endswith(":") or (text.startswith("#") and "\n" not in text)


# split every markdown file into chunks, keeping a lead-in line with its list
def load_chunks():
    chunks = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        doc = path.stem
        text = path.read_text(encoding="utf-8")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

        merged = []
        for block in blocks:
            if merged and _is_leadin(merged[-1]):
                merged[-1] = merged[-1] + "\n" + block
            else:
                merged.append(block)

        for block in merged:
            chunks.append({"doc": doc, "text": block})
    return chunks
