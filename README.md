# Christian AI Assistant

A Christianity-focused AI assistant that answers theology questions, verifies Bible
verses in real time, generates Christian artwork, and handles adversarial or
hallucinated inputs gracefully.

Built with GPT-4o, Streamlit, and bible-api.com as part of a take-home assignment.

---

## What it does

- **Theology chat** — ask anything about Christianity and get a warm, pastoral response
- **Scripture grounding** — every Bible verse is verified against a real Bible API before
  being shown with a "verified" badge
- **Image generation** — describe a Christian scene and gpt-image-1 generates the artwork
- **Hallucination detection** — fake or wrong Bible references are caught and corrected
- **Safety moderation** — adversarial prompts (rewriting scripture, hateful content) are
  blocked at two layers
- **Denomination awareness** — switch between General Christian, Catholic, Protestant,
  Eastern Orthodox, and Evangelical — the assistant adjusts its responses accordingly

---

## Project structure

```
christian-ai-assistant/
├── utils.py        # shared logic — system prompt, chat(), lookup_verse(), generate_image()
├── app.py          # Streamlit chat interface
├── eval.py         # automated evaluation runner
├── eval_dataset.md # 31 test cases across 6 categories
├── ARCHITECTURE.md # decisions, tradeoffs, and production path
├── .env            # your API keys (don't commit this)
└── requirements.txt
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/christian-ai-assistant.git
cd christian-ai-assistant
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file in the root folder:
```
OPENAI_API_KEY=sk-your-openai-key-here
```

**5. Run the app**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Running the eval suite

```bash
streamlit run eval.py
```

Click **"Run all tests"** — it runs 16 test cases automatically and shows pass/fail
with explanations. Uses GPT-4o as the judge instead of keyword matching, so it
evaluates intent rather than exact wording.

---

## Requirements

```
streamlit
openai
requests
Pillow
python-dotenv
```

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a full breakdown of decisions — why Bible
API over RAG, how the two-layer safety works, prompt engineering techniques used, and
what would change in a production deployment.
