# Anki LLM Grader

An Anki add-on that will grade typed answers with an LLM. The current M2
milestone captures card content and sends it through Anki's JavaScript-to-Python
bridge, then renders a structured mock result in the reviewer.

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
AI** or press **Ctrl+Enter** to request a grade. M2 returns a mock result to
exercise the complete UI bridge; the Groq API integration arrives in M3.
