(() => {
  "use strict";

  const PANEL_ID = "llm-grader-panel";

  function mountStatusPanel() {
    if (document.getElementById(PANEL_ID)) {
      return;
    }

    const panel = document.createElement("aside");
    panel.id = PANEL_ID;
    panel.setAttribute("role", "status");
    panel.setAttribute("aria-live", "polite");
    panel.textContent = "LLM Grader loaded";
    document.body.appendChild(panel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountStatusPanel, { once: true });
  } else {
    mountStatusPanel();
  }
})();
