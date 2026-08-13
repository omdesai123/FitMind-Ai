/* =========================================================
   FitMind AI — Frontend logic (vanilla JS, no frameworks)
   ========================================================= */

// ---- Screen elements ----
const welcomeScreen = document.getElementById("welcome-screen");
const goalScreen = document.getElementById("goal-screen");
const chatScreen = document.getElementById("chat-screen");

// ---- Welcome screen ----
const getStartedBtn = document.getElementById("get-started-btn");

// ---- Goal screen ----
const goalCards = document.querySelectorAll(".goal-card");

// ---- Chat screen ----
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const chatMessages = document.getElementById("chat-messages");
const sidebarGoalValue = document.getElementById("sidebar-goal-value");
const chatHeaderGoal = document.getElementById("chat-header-goal");
const newChatBtn = document.getElementById("new-chat-btn");
const changeGoalBtn = document.getElementById("change-goal-btn");

// ---- App state ----
let selectedGoal = null;

// Welcome message shown once per goal, the first time its chat opens
const WELCOME_MESSAGE =
  "👋 Hey! I'm your FitMind AI Trainer.\n\nI'm ready to help you with your fitness journey.\n\nAsk me anything about workouts, exercises, sets, reps, or training!";

/* ---------------------------------------------------------
   Screen switching helper
   --------------------------------------------------------- */
function showScreen(screen) {
  [welcomeScreen, goalScreen, chatScreen].forEach((s) => s.classList.remove("active"));
  screen.classList.add("active");
}

/* ---------------------------------------------------------
   Welcome -> Goal selection
   --------------------------------------------------------- */
getStartedBtn.addEventListener("click", () => {
  showScreen(goalScreen);
});

/* ---------------------------------------------------------
   Goal selection -> Chat
   --------------------------------------------------------- */
goalCards.forEach((card) => {
  card.addEventListener("click", () => {
    goalCards.forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");

    selectedGoal = card.dataset.goal;
    openChat(selectedGoal);
  });
});

function openChat(goal) {
  sidebarGoalValue.textContent = goal;
  chatHeaderGoal.textContent = goal;

  // Fresh visual chat log each time a goal is opened
  chatMessages.innerHTML = "";
  appendMessage(WELCOME_MESSAGE, "bot");

  showScreen(chatScreen);
  chatInput.focus();
}

/* ---------------------------------------------------------
   New chat / change goal buttons
   --------------------------------------------------------- */
newChatBtn.addEventListener("click", async () => {
  if (!selectedGoal) return;

  try {
    await fetch("/new-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "", goal: selectedGoal }),
    });
  } catch (err) {
    // Even if the reset call fails, still clear the visible chat
    console.error("Failed to reset conversation:", err);
  }

  chatMessages.innerHTML = "";
  appendMessage(WELCOME_MESSAGE, "bot");
});

changeGoalBtn.addEventListener("click", () => {
  showScreen(goalScreen);
});

/* ---------------------------------------------------------
   Sending a chat message
   --------------------------------------------------------- */
chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = chatInput.value.trim();
  if (!text || !selectedGoal) return;

  appendMessage(text, "user");
  chatInput.value = "";
  setSending(true);

  const typingEl = showTypingIndicator();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, goal: selectedGoal }),
    });

    const data = await response.json();

    typingEl.remove();

    if (!response.ok) {
      appendMessage(data.error || "Something went wrong. Please try again.", "error");
    } else {
      appendMessage(data.response, "bot");
    }
  } catch (err) {
    typingEl.remove();
    appendMessage("Network error — could not reach FitMind AI. Please check your connection and try again.", "error");
    console.error(err);
  } finally {
    setSending(false);
    chatInput.focus();
  }
});

/* ---------------------------------------------------------
   Helpers
   --------------------------------------------------------- */
function appendMessage(text, type) {
  const bubble = document.createElement("div");
  bubble.className = `msg ${type}`;
  bubble.textContent = text;
  chatMessages.appendChild(bubble);
  scrollToBottom();
  return bubble;
}

function showTypingIndicator() {
  const indicator = document.createElement("div");
  indicator.className = "typing-indicator";
  indicator.innerHTML = "<span></span><span></span><span></span>";
  chatMessages.appendChild(indicator);
  scrollToBottom();
  return indicator;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  chatInput.disabled = isSending;
}
