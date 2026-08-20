(() => {
  "use strict";

  const PANEL_ID = "llm-grader-panel";
  const FIELD_IDS = {
    prompt: "llm_prompt",
    answerKey: "llm_answer_key",
    rubric: "llm_rubric",
  };

  function fieldText(id) {
    const element = document.getElementById(id);
    return element ? (element.textContent || "").trim() : "";
  }

  function typedAnswer() {
    const element = document.querySelector(
      "#typeans, input[type='text'], textarea, [contenteditable='true']"
    );
    if (!element) {
      return "";
    }
    if ("value" in element) {
      return element.value.trim();
    }
    return (element.textContent || "").trim();
  }

  function captureCard() {
    return {
      prompt: fieldText(FIELD_IDS.prompt),
      answer_key: fieldText(FIELD_IDS.answerKey),
      user_answer: typedAnswer(),
      rubric: fieldText(FIELD_IDS.rubric),
    };
  }

  function row(label, value) {
    const wrapper = document.createElement("div");
    wrapper.className = "llm-grader-capture-row";

    const heading = document.createElement("strong");
    heading.textContent = label;
    const content = document.createElement("span");
    content.textContent = value || "Not found";

    wrapper.append(heading, content);
    return wrapper;
  }

  function showCapture() {
    const capture = captureCard();
    const output = document.getElementById("llm-grader-output");
    output.replaceChildren(
      row("Prompt", capture.prompt),
      row("Answer key", capture.answer_key),
      row("Your answer", capture.user_answer),
      row("Rubric", capture.rubric)
    );
  }

  function mountPanel() {
    if (document.getElementById(PANEL_ID)) {
      return;
    }

    const panel = document.createElement("aside");
    panel.id = PANEL_ID;
    panel.setAttribute("aria-label", "LLM Grader");

    const title = document.createElement("div");
    title.className = "llm-grader-title";
    title.textContent = "LLM Grader";

    const output = document.createElement("div");
    output.id = "llm-grader-output";
    output.setAttribute("role", "status");
    output.setAttribute("aria-live", "polite");
    output.textContent = "Ready to capture this card.";

    const button = document.createElement("button");
    button.id = "llm-grader-grade-button";
    button.type = "button";
    button.textContent = "Grade with AI";
    button.title = "Capture card fields (Ctrl+Enter)";
    button.addEventListener("click", showCapture);

    panel.append(title, output, button);
    document.body.appendChild(panel);
  }

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "Enter") {
      event.preventDefault();
      mountPanel();
      showCapture();
    }
  });

  window.__llmGradeCaptureCard = captureCard;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountPanel, { once: true });
  } else {
    mountPanel();
  }
})();
