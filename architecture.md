# Architecture Note

## What I built and why

This is a Christianity-focused AI assistant that can answer theology questions, look up
and verify Bible verses, generate Christian artwork, and handle tricky or adversarial
inputs gracefully. I built it with Streamlit, GPT-4o, and a free Bible API.

Here's the thinking behind the major decisions.

---

## The most important decision — Bible API instead of RAG

When I saw the assignment mention RAG and vector databases, my first instinct was to
embed the entire Bible and build a semantic search pipeline. But I stepped back and
asked: what problem am I actually trying to solve?

The core grounding problem here is: **don't let the model make up Bible verses.**

A vector database would let me do semantic search — finding verses about forgiveness,
hope, love, etc. That's genuinely useful. But for the primary grounding problem —
detecting hallucinated or fake scripture — a Bible API is actually more reliable.

Here's why: if GPT-4o cites "Hezekiah 4:12" (a book that doesn't exist), the API
returns null. That's a hard signal. A vector search would return the closest match
and a similarity score — which is a soft signal and much harder to act on.

The Bible API also returns exact canonical verse text, so I can show users the actual
scripture and a "verified" badge. No approximation, no drift.

RAG would genuinely add value for one thing: "find me verses about anxiety" — semantic
search across the whole Bible. I've noted this as a future enhancement but it wasn't
worth the setup time for this assignment.

---

## Safety — two layers, not one

I didn't want to rely on the LLM alone for safety because LLMs can be talked out of
their guardrails with clever prompting. So I added a fast first layer.

**Layer 1 — Keyword blocklist**
Before any API call happens, the user's message is checked against a list of known
adversarial phrases like "rewrite bible", "god endorses", "make the bible say". If it
matches, the message never reaches GPT-4o. Free, instant, and can't be jailbroken.

**Layer 2 — LLM-level safety in the system prompt**
The system prompt tells GPT-4o to classify every request, check for manipulation, and
refuse gracefully with a pastoral tone. This catches the subtle stuff — requests that
don't use any blocked phrases but are still trying to weaponize scripture.

The two layers cover different threat surfaces. Layer 1 is blunt and cheap. Layer 2 is
intelligent but can theoretically be bypassed. Together they're much stronger than either
alone.

---

## Prompt engineering — what I actually did and why

The system prompt went through a few iterations. The first version was just a list of
rules, and GPT-4o followed them inconsistently. The final version uses a few techniques
that made a real difference:

**Delimiters** — I wrapped each section in `===` and XML-style tags. This stops the
model from treating the whole prompt as one blob and blurring rules across sections.
It also makes prompt injection harder.

**Step-by-step reasoning** — instead of saying "be safe and accurate", I tell the model
to follow four explicit steps on every response: classify the request, check for safety
issues, verify any scripture claims, then self-check the draft. This is essentially
chain-of-thought prompting applied to safety.

**Self-check checklist** — before responding, the model checks its own draft against a
list of rules: is the verse real? Is the tone right? Is it denomination-appropriate?
This catches errors before they reach the user.

**One-shot examples** — I gave the model three concrete examples with a good response
and a bad response for each. For the "fake verse" case, the "God helps those who help
themselves" example made a noticeable difference in accuracy compared to just describing
the rule.

**Denomination injection** — the denomination the user selects gets dynamically inserted
into the system prompt, so the self-check checklist is literally checking against the
right tradition.

---

## Evaluation — why I used GPT-4o as the judge

My first eval runner used keyword matching. It failed immediately.

The model would say "I'm sorry, I can't assist with that" and the keyword check for
"cannot" would fail because the model used "can't" with an apostrophe. That's a
measurement problem, not a model problem.

I switched to using a second GPT-4o call as the judge. For each test case, the judge
reads the model's response and a plain-English pass criterion, then decides pass or fail
based on intent. This is how OpenAI Evals and LangChain Evals work — it's the standard
approach for evaluating generative AI outputs.

The eval runner has 16 test cases across four categories: hallucination detection,
adversarial prompts, theological edge cases, and image safety.

---

## Code structure

I split the code into three files to avoid duplicating logic between the app and the
eval runner.

```
christian-ai-assistant/
├── utils.py        # everything shared — system prompt, chat(), lookup_verse(), generate_image()
├── app.py          # just the Streamlit UI — imports everything from utils.py
├── eval.py         # eval runner — also imports chat() from utils.py
├── eval_dataset.md # 31 test cases with pass criteria, across 6 categories
├── ARCHITECTURE.md # this file
├── .env            # API keys — not committed to git
└── requirements.txt
```

Both app.py and eval.py import from utils.py, so the eval is testing the exact same
model function that runs in the real app — not a separate reimplementation.

---

## Limitations — and what production would look like

I used Streamlit because it's the fastest way to get a working demo within the time
constraint. It's a prototyping tool and I'm not pretending otherwise.

Here's what would change in a real deployment:

**Conversation history** right now lives in Streamlit session state and disappears on
refresh. In production this would go in a database — PostgreSQL or Redis — so
conversations persist across sessions.

**Streamlit itself** would be replaced with a FastAPI backend and a React frontend.
Streamlit is great for demos but it reruns the whole script on every interaction, which
doesn't scale.

**The Bible API** is a free public API with no SLA. In production I'd either self-host
a Bible database or use a paid provider with rate limit guarantees.

**Semantic verse search** — adding a vector database (Pinecone or ChromaDB) with Bible
embeddings would enable queries like "find verses about forgiveness" that the current
API-based approach can't handle.

**The core decisions** — Bible API for grounding, two-layer safety, structured prompt
engineering, LLM-as-judge evaluation — would all stay the same in production. The
infrastructure around them would change.
