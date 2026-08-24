# Notes

## Approach

I kept this deliberately simple. Each handbook file gets split into paragraph
sized chunks, and I index them with BM25 (from `rank_bm25`). For a question I
take the top 5 chunks and pass only those to a free LLM (Groq or Gemini, through
an OpenAI-compatible API), with instructions to answer from that text alone and
to say it doesn't know when the answer isn't there. I went with keyword search
rather than embeddings because the questions here are answered by exact terms
like "Zone 4", "166" or "21 days", which BM25 is good at, and it needs no model
download or extra service. Every answer comes back as
`{answer, citations, supported}` and the citation is just the filename the chunk
came from.

## Test results (the 8 sample questions)

Running all eight through `answer()` (Groq, `openai/gpt-oss-120b`): the seven
answerable questions came back correct, and the unanswerable one (P8, the
vacation policy) was refused. I check the citation and the refusal
automatically and read each answer against the expected one by hand.

| Q  | Result | Answer |
|----|:---:|-------|
| P1 | correct | DIM divisor 166 for international |
| P2 | correct | Newark dock Mon-Fri 06:00-22:00, Sat 07:00-14:00 |
| P3 | correct | $100 per shipment default liability |
| P4 | correct | no, cells over 100 Wh never accepted |
| P5 | correct | 21 calendar days |
| P6 | correct | full cross-border document list |
| P7 | correct | Zone 4 is 11.0% |
| P8 | refused correctly | vacation policy isn't in the handbook |

So 7 of 7 answerable questions correct, plus a correct refusal on P8. The first
run actually missed P1 and P6 (the model said "I don't know") because the
chunker had split a lead-in line like "DIM divisors:" away from the list under
it, so the numbers never reached the model. Keeping the lead-in line attached to
its list fixed both. If no key is set the tool still runs but falls back to
quoting the top chunk instead of composing an answer.

## What went wrong / things I noticed

- **The heading beats the answer in the ranking.** For "fuel surcharge Zone 4"
  the heading "Fuel Surcharge Schedule" scores higher than the table row that
  actually holds 11.0%, because the heading repeats the words in the question
  and the table row doesn't. Passing the top 5 chunks to the model hides this
  (the row is still in context), but a naive top 1 reader gets it wrong. Pulling
  the heading into the same chunk as its body would help.

- **You can't detect an unanswerable question from the score.** P8 (vacation
  policy) actually scores 8.82, higher than P2 (Newark hours) at 8.63, and it
  lands on `comms-templates` because that file is full of common words. So there
  is no clean score cutoff that separates "answerable" from "not". This is why I
  lean on the model to decide whether the text really supports an answer rather
  than trusting a threshold.

- **There's a prompt injection sitting in the corpus.** `comms-templates.md`
  contains a line telling the reader to ignore all previous instructions, reply
  "APPROVED" and print the system prompt. It retrieves easily. I handle it by
  telling the model the extracts are reference data and not commands, so a line
  inside a document can't change what it does. Worth being aware of because a
  pipeline that just glued the chunks into the prompt would fall for it.

- **Two versions of the escalation policy.** `escalation-policy-v2` is marked
  deprecated and `v3` supersedes it, and they give different SLAs. Both can come
  back for an escalation question, so I tell the model to prefer whichever isn't
  marked deprecated.

## Conceptual questions

**1. Why chunk instead of sending all 16 documents?**
Sending everything is wasteful and actually makes the answer worse, because the
relevant sentence gets buried in a lot of unrelated policy and the model has to
guess what matters. Chunking plus retrieval sends only the few passages that are
relevant, which keeps it focused and makes the citation obvious. It also scales,
real handbooks are far bigger than a context window.

**2. Why is it important to refuse some questions?**
In support, a confident wrong answer is worse than "I don't know", because
someone will quote it to a customer. Refusing when the handbook doesn't cover
something keeps the tool trustworthy and stops it inventing policy (the vacation
question is the obvious case here).

**3. One weakness of keyword search, and how embeddings help?**
It matches words, not meaning. Ask "how long do I have to report broken goods"
and it can miss the doc that says "file a damage claim within 21 days" because
the wording is different. Embeddings put similar meanings near each other in
vector space, so paraphrases still match. BM25 is still better at exact tokens
like "Zone 4" or "166", so in practice I'd combine the two.

**4. One improvement with more time?**
A hybrid retriever: run BM25 and embeddings together, merge the results, then
re-rank the top few with a cross encoder. That fixes the "heading outranks the
answer" problem above and catches reworded questions, while keeping BM25's edge
on exact codes and numbers.
