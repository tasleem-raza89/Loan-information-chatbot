const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const chatArea = document.getElementById("chatArea");
const welcome = document.getElementById("welcome");
const sendButton = form.querySelector("button");
const newChatButton = document.getElementById("newChat");

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "₹";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  // textContent prevents HTML entered by the user from being executed.
  bubble.textContent = text;
  row.append(avatar, bubble);
  chatArea.appendChild(row);
  row.scrollIntoView({ behavior: "smooth", block: "nearest" });
  return row;
}

async function sendMessage(message) {
  const text = message.trim();
  if (!text || sendButton.disabled) return;
  welcome.style.display = "none";
  addMessage("user", text);
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;

  const typing = document.createElement("div");
  typing.className = "typing";
  typing.textContent = "LoanWise is preparing an answer…";
  chatArea.appendChild(typing);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await response.json();
    typing.remove();
    if (!response.ok) throw new Error(data.error || "Request failed.");
    addMessage("assistant", data.answer || "Sorry, no answer was returned.");
  } catch (error) {
    typing.remove();
    addMessage("assistant", `Sorry, I couldn't get an answer. ${error.message} Check that the Python server is running. If you're using local AI, also check that Ollama is running.`);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 130)}px`;
});
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll("[data-question]").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.question));
});
newChatButton.addEventListener("click", () => {
  chatArea.replaceChildren();
  welcome.style.display = "";
  input.value = "";
  input.focus();
});
