"""Anki LLM Grader add-on entry point."""

import json
from typing import Any
from urllib.parse import unquote

from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer
from aqt.webview import WebContent


ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)

# Make the bundled reviewer assets available below /_addons/<package>/web/.
mw.addonManager.setWebExports(__name__, r"web/.*\.(css|js)")


def _add_reviewer_assets(web_content: WebContent, context: object) -> None:
    """Load the grader panel only in Anki's reviewer webview."""
    if not isinstance(context, Reviewer):
        return

    web_content.css.append(
        f"/_addons/{ADDON_PACKAGE}/web/grader.css"
    )
    web_content.js.append(
        f"/_addons/{ADDON_PACKAGE}/web/grader.js"
    )


def _mock_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic bridge-test result until M3 adds Groq."""
    has_answer = bool(str(payload.get("user_answer", "")).strip())
    return {
        "verdict": "partial" if has_answer else "incorrect",
        "score": 0.5 if has_answer else 0.0,
        "missing_points": ["M2 uses a mock result; model grading arrives in M3."],
        "feedback_short": (
            "The JavaScript-to-Python bridge is working."
            if has_answer
            else "Enter an answer before requesting a grade."
        ),
    }


def _handle_js_message(
    handled: tuple[bool, Any], message: str, context: object
) -> tuple[bool, Any]:
    """Receive grader requests and send the mock response to the reviewer."""
    prefix = "llmgrade:"
    if not message.startswith(prefix) or not isinstance(context, Reviewer):
        return handled

    try:
        payload = json.loads(unquote(message[len(prefix) :]))
        if not isinstance(payload, dict):
            raise ValueError("grading payload must be an object")
        result = _mock_result(payload)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        result = {
            "error": f"Could not read grading request: {error}",
        }

    context.web.eval(
        f"window.__llmGradeShowResult({json.dumps(result)});"
    )
    return (True, None)


gui_hooks.webview_will_set_content.append(_add_reviewer_assets)
gui_hooks.webview_did_receive_js_message.append(_handle_js_message)
