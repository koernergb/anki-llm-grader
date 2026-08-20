# Anki LLM Grader

An Anki add-on that will grade typed answers with an LLM. The current M1
milestone adds a reviewer panel that captures the card prompt, answer key,
typed response, and optional rubric.

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

Omit `llm_rubric` if the note type has no rubric field. Click **Grade with
AI** or press **Ctrl+Enter** to inspect the captured values. M1 does not contact
an LLM yet.
