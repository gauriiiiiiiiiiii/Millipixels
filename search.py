import re

from rank_bm25 import BM25Okapi

from config import TOP_K


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


# bm25 index over the chunks
class Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    def search(self, question, k=TOP_K):
        scores = self.bm25.get_scores(tokenize(question))
        ranked = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)
        hits = []
        for i in ranked[:k]:
            hit = dict(self.chunks[i])
            hit["score"] = float(scores[i])
            hits.append(hit)
        return hits
