"""Anki LLM Grader add-on entry point."""

import json
import os
from typing import Any
from urllib.parse import unquote

from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from .grader import DEFAULT_MODEL, GraderError, GroqGrader


ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
GRADER = GroqGrader(
    api_key=os.environ.get("GROQ_API_KEY", ""),
    model=DEFAULT_MODEL,
)

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


def _handle_js_message(
    handled: tuple[bool, Any], message: str, context: object
) -> tuple[bool, Any]:
    """Receive grader requests and run Groq outside Anki's UI thread."""
    prefix = "llmgrade:"
    if not message.startswith(prefix) or not isinstance(context, Reviewer):
        return handled

    try:
        payload = json.loads(unquote(message[len(prefix) :]))
        if not isinstance(payload, dict):
            raise ValueError("grading payload must be an object")
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        context.web.eval(
            "window.__llmGradeShowResult("
            + json.dumps({"error": f"Could not read grading request: {error}"})
            + ");"
        )
        return (True, None)

    def grade_in_background() -> dict[str, Any]:
        try:
            return GRADER.grade(payload)
        except GraderError as error:
            return {"error": str(error)}
        except Exception:
            return {"error": "Unexpected grading error. Check Anki's console for details."}

    def show_result(future: Any) -> None:
        result = future.result()
        context.web.eval(
            f"window.__llmGradeShowResult({json.dumps(result)});"
        )

    mw.taskman.run_in_background(grade_in_background, show_result)
    return (True, None)


gui_hooks.webview_will_set_content.append(_add_reviewer_assets)
gui_hooks.webview_did_receive_js_message.append(_handle_js_message)
