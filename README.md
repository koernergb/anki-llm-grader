# Anki LLM Grader

An Anki add-on that grades typed answers with Groq. The current M3 milestone
performs real grading on a background thread, validates structured results,
retries transient failures, throttles requests, and caches exact repeats.

## M0 installation

1. In Anki, open **Tools → Add-ons → View Files**.
2. Copy or symlink `add_on/anki_llm_grader` into the displayed `addons21`
   directory.
3. Restart Anki and begin reviewing a card.
4. Confirm that **LLM Grader** appears at the lower-right of the reviewer.

## Card template

Add these hidden elements to the front template of a typed-answer card:

```html
<div id="llm_prompt" style="display:none">{{Front}}</div>
<div id="llm_answer_key" style="display:none">{{Back}}</div>
<div id="llm_rubric" style="display:none">{{Rubric}}</div>

{{Front}}
{{type:TypedAnswer}}
```

Omit `llm_rubric` if the note type has no rubric field.

## Groq API key

Set the `GROQ_API_KEY` environment variable before launching Anki, then click
**Grade with AI** or press **Ctrl+Enter**. M4 will add Anki-native configuration
so an environment variable is no longer required.
