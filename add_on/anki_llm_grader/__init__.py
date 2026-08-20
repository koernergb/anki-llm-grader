"""Anki LLM Grader add-on entry point."""

from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer
from aqt.webview import WebContent


ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)

# Make the bundled reviewer assets available below /_addons/<package>/web/.
mw.addonManager.setWebExports(__name__, r"web/.*\.(css|js)")


def _add_reviewer_assets(web_content: WebContent, context: object) -> None:
    """Load the M0 status panel only in Anki's reviewer webview."""
    if not isinstance(context, Reviewer):
        return

    web_content.css.append(
        f"/_addons/{ADDON_PACKAGE}/web/grader.css"
    )
    web_content.js.append(
        f"/_addons/{ADDON_PACKAGE}/web/grader.js"
    )


gui_hooks.webview_will_set_content.append(_add_reviewer_assets)
