# Anki LLM Grader

An Anki add-on that grades typed answers with Groq. The current M4 milestone
adds native Anki configuration for the API key, model, and grading strictness.

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

## Configuration

In Anki, open **Tools → Add-ons**, select **Anki LLM Grader**, and click
**Config**. Add your Groq API key to `groq_api_key`; optionally change `model`
or set `strictness` from `0` (lenient) through `2` (strict). Restart Anki after
editing the configuration.

You may leave `groq_api_key` empty and set the `GROQ_API_KEY` environment
variable instead. Click **Grade with AI** or press **Ctrl+Enter** to grade.
