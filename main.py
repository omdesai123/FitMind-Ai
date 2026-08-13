"""
FitMind AI - FastAPI Backend
-----------------------------
This backend wraps the existing AI Gym Trainer chatbot logic
(originally written as a command-line script in chatbot.py) and
exposes it as a web API + serves the frontend.

IMPORTANT NOTE ABOUT chatbot.py:
chatbot.py was written as an interactive command-line program.
It calls input() at the very top level of the file (outside any
function) to ask the user to pick a fitness goal and to chat.
Because of that, chatbot.py CANNOT be imported directly into a
web server -- Python would run that input() code the moment the
file is imported, and the server would freeze waiting for
terminal input that will never come.

To respect the requirement "do not modify chatbot.py", we do NOT
touch that file at all. Instead, this file re-creates the exact
same chatbot behaviour (same system prompts, same model, same
LangChain message classes) inside proper functions that a web
server can safely call per request. The logic and wording are
kept 100% identical to chatbot.py.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage

# ---------------------------------------------------------
# Load environment variables (Mistral API key, etc.)
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# Create the FastAPI app
# ---------------------------------------------------------
app = FastAPI(title="FitMind AI")

# Serve the "static" folder (CSS, JS) at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates (for serving index.html)
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------
# Set up the Mistral chat model (same model as chatbot.py)
# ---------------------------------------------------------
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

print("MISTRAL API KEY EXISTS:", bool(MISTRAL_API_KEY))
print(
    "MISTRAL API KEY LENGTH:",
    len(MISTRAL_API_KEY) if MISTRAL_API_KEY else 0
)

model = ChatMistralAI(
    model="mistral-small-latest",
    api_key=MISTRAL_API_KEY
)
# ---------------------------------------------------------
# The three trainer modes (same text as chatbot.py)
# ---------------------------------------------------------
GOAL_PROMPTS = {
    "Muscle Gain": """
    You are an AI Gym Trainer specialized in muscle gain.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice for muscle building.
    Keep your answers simple and beginner-friendly.
    """,
    "Weight Loss": """
    You are an AI Gym Trainer specialized in weight loss.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice for weight management.
    Keep your answers simple and beginner-friendly.
    """,
    "General Fitness": """
    You are an AI Gym Trainer specialized in general fitness.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice.
    Keep your answers simple and beginner-friendly.
    """,
}

# ---------------------------------------------------------
# In-memory conversation storage
# ---------------------------------------------------------
# Since we are not using a database yet, we keep each goal's
# conversation history in a simple dictionary in memory.
# Key   -> the fitness goal (e.g. "Muscle Gain")
# Value -> list of LangChain message objects (SystemMessage,
#          HumanMessage, AIMessage), same as "message" list
#          in chatbot.py
conversations: dict[str, list] = {}


def get_conversation(goal: str) -> list:
    """
    Get (or start) the conversation history for a given goal.
    If this goal has no history yet, start it with the correct
    SystemMessage, exactly like chatbot.py does.
    """
    if goal not in GOAL_PROMPTS:
        # Fall back to General Fitness if an unknown goal is sent
        goal = "General Fitness"

    if goal not in conversations:
        conversations[goal] = [SystemMessage(content=GOAL_PROMPTS[goal])]

    return conversations[goal]


# ---------------------------------------------------------
# Request body model for the /chat endpoint
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    goal: str


# ---------------------------------------------------------
# Route: GET / -> Serve the frontend
# ---------------------------------------------------------
@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
# ---------------------------------------------------------
# Route: POST /chat -> Talk to the AI Gym Trainer
# ---------------------------------------------------------
@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        user_message = chat_request.message.strip()
        goal = chat_request.goal.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty."},
            )

        # Get this goal's conversation history (creates it if new)
        history = get_conversation(goal)

        # Add the user's message to the history
        history.append(HumanMessage(content=user_message))

        # Ask the Mistral model for a response
        response = model.invoke(history)

        # Save the AI's reply into the conversation history
        history.append(AIMessage(content=response.content))

        # Send the AI response back to the frontend as JSON
        return JSONResponse(content={"response": response.content})

    except Exception as error:
        # Handle any errors (bad API key, network issue, etc.)
        return JSONResponse(
            status_code=500,
            content={"error": f"Something went wrong: {str(error)}"},
        )


# ---------------------------------------------------------
# Route: POST /new-chat -> Reset conversation for a goal
# ---------------------------------------------------------
@app.post("/new-chat")
async def new_chat(chat_request: ChatRequest):
    goal = chat_request.goal.strip()
    if goal in conversations:
        del conversations[goal]
    # Recreate a fresh conversation with just the system prompt
    get_conversation(goal)
    return JSONResponse(content={"status": "Conversation reset."})
