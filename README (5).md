# 🏋️ FitMind AI — Your Personal AI Gym Trainer

A full web app built around an existing chatbot script: FastAPI backend +
vanilla HTML/CSS/JS frontend, styled as a modern dark-themed AI SaaS product.

**Live app:** https://fitmind-ai-p4od.onrender.com

> Hosted on Render's free tier — if it's been idle for a while, the first
> load can take 30–60 seconds while the server wakes up.

## Project structure

```
fitmind-ai/
│
├── chatbot.py          # original CLI chatbot — untouched, unused by the server directly
├── main.py              # FastAPI backend (re-implements the same logic for the web)
├── requirements.txt
├── .env                 # local only — put your MISTRAL_API_KEY here (not committed)
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

## A note on `chatbot.py`

`chatbot.py` was left **completely unchanged**. It's a command-line script —
importing it directly would run its top-level `input()` calls and freeze a
web server. So `main.py` doesn't import it. Instead, `main.py` re-implements
the same trainer logic (same system prompts, same `ChatMistralAI` model,
same LangChain message classes) inside proper functions FastAPI can call
per-request.

## Run locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Mistral API key to `.env`:
   ```
   MISTRAL_API_KEY=your_actual_key_here
   ```

4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

5. Open **http://127.0.0.1:8000**.

## Deployment (Render)

This app is deployed on [Render](https://render.com) as a Web Service:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment variable:** `MISTRAL_API_KEY` set in the Render dashboard
  (the `.env` file is git-ignored and never deployed)

Pushing to the connected GitHub branch triggers an automatic redeploy.

## How it works

1. Welcome screen → click **Get Started**.
2. Pick a goal: Muscle Gain, Weight Loss, or General Fitness.
3. Chat opens with a welcome message from the trainer.
4. Each message is sent to `POST /chat` with your text and goal.
5. The backend keeps a running conversation history per goal in memory
   (no database yet) and returns the AI's reply as JSON.
6. **New Chat** resets the conversation history for the current goal.

## Known limitations

- Conversation history is stored **in memory only** — it resets whenever the
  server restarts or redeploys, and isn't shared across multiple server
  instances.
- No authentication or database yet — by design, for this stage of the
  project.
- Free-tier Render services spin down after 15 minutes of inactivity.
