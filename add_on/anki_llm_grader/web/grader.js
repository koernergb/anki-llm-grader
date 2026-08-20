(() => {
  "use strict";

  const PANEL_ID = "llm-grader-panel";
  const FIELD_IDS = {
    prompt: "llm_prompt",
    answerKey: "llm_answer_key",
    rubric: "llm_rubric",
  };
  let latestRequestId = 0;

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
    const button = document.getElementById("llm-grader-grade-button");
    if (!output || !button || button.disabled) {
      return;
    }
    capture.request_id = ++latestRequestId;
    output.className = "";
    output.textContent = "Grading…";
    button.disabled = true;
    pycmd(`llmgrade:${encodeURIComponent(JSON.stringify(capture))}`);
  }

  function showResult(result) {
    const output = document.getElementById("llm-grader-output");
    if (!output) {
      return;
    }
    if (result.request_id !== latestRequestId) {
      return;
    }

    const button = document.getElementById("llm-grader-grade-button");
    button.disabled = false;

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

    const overrideLabel = document.createElement("div");
    overrideLabel.className = "llm-grader-override-label";
    overrideLabel.textContent = "Override display (does not affect scheduling):";

    const overrides = document.createElement("div");
    overrides.className = "llm-grader-overrides";
    ["correct", "partial", "incorrect"].forEach((choice) => {
      const override = document.createElement("button");
      override.type = "button";
      override.textContent = choice[0].toUpperCase() + choice.slice(1);
      override.setAttribute("aria-pressed", String(choice === verdict));
      override.addEventListener("click", () => {
        output.className = `llm-grader-result llm-grader-${choice}`;
        verdictLine.textContent = `${choice.toUpperCase()} · manual override`;
        overrides.querySelectorAll("button").forEach((candidate) => {
          candidate.setAttribute("aria-pressed", String(candidate === override));
        });
      });
      overrides.appendChild(override);
    });

    output.replaceChildren(
      verdictLine,
      feedback,
      missing,
      overrideLabel,
      overrides
    );
  }

  function resetPanel() {
    latestRequestId += 1;
    const output = document.getElementById("llm-grader-output");
    const button = document.getElementById("llm-grader-grade-button");
    if (output) {
      output.className = "";
      output.textContent = "Ready to grade this card.";
    }
    if (button) {
      button.disabled = false;
    }
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
  window.__llmGradeRequest = requestGrade;
  window.__llmGradeReset = resetPanel;
  window.__llmGradeShowResult = showResult;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountPanel, { once: true });
  } else {
    mountPanel();
  }
})();
