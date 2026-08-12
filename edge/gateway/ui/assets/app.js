const help = document.querySelector("#help");
const helpButton = document.querySelector(".help-button");
const form = document.querySelector("#message-form");
const message = document.querySelector("#message");
const messages = document.querySelector("#messages");
const notice = document.querySelector("#notice");

helpButton.addEventListener("click", () => {
  help.showModal();
  helpButton.setAttribute("aria-expanded", "true");
});
document.querySelector("[data-close-help]").addEventListener("click", () => help.close());
help.addEventListener("close", () => {
  helpButton.setAttribute("aria-expanded", "false");
  helpButton.focus();
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = message.value.trim();
  if (!text) return;
  const bubble = document.createElement("p");
  bubble.className = "customer-message";
  bubble.textContent = text;
  messages.append(bubble);
  message.value = "";
  notice.textContent = "Thanks — your message is ready for the assistant. You can change any detail later.";
  notice.hidden = false;
  window.setTimeout(() => { notice.hidden = true; }, 5000);
  message.focus();
});
