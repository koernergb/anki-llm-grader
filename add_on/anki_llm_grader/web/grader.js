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

  function requestGrade() {
    const capture = captureCard();
    const output = document.getElementById("llm-grader-output");
    output.textContent = "Grading…";
    pycmd(`llmgrade:${encodeURIComponent(JSON.stringify(capture))}`);
  }

  function showResult(result) {
    const output = document.getElementById("llm-grader-output");
    if (!output) {
      return;
    }

    if (result.error) {
      output.className = "llm-grader-error";
      output.textContent = result.error;
      return;
    }

    const verdict = String(result.verdict || "unknown").toLowerCase();
    output.className = `llm-grader-result llm-grader-${verdict}`;

    const verdictLine = document.createElement("div");
    verdictLine.className = "llm-grader-verdict";
    verdictLine.textContent = `${verdict.toUpperCase()} · ${Math.round(
      Number(result.score || 0) * 100
    )}%`;

    const feedback = document.createElement("p");
    feedback.textContent = result.feedback_short || "No feedback returned.";

    const missing = document.createElement("ul");
    (result.missing_points || []).forEach((point) => {
      const item = document.createElement("li");
      item.textContent = point;
      missing.appendChild(item);
    });

    output.replaceChildren(verdictLine, feedback, missing);
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
    button.addEventListener("click", requestGrade);

    panel.append(title, output, button);
    document.body.appendChild(panel);
  }

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "Enter") {
      event.preventDefault();
      mountPanel();
      requestGrade();
    }
  });

  window.__llmGradeCaptureCard = captureCard;
  window.__llmGradeShowResult = showResult;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountPanel, { once: true });
  } else {
    mountPanel();
  }
})();
