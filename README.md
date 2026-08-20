# Anki LLM Grader

An Anki desktop add-on that grades typed answers with Groq and displays a
Correct, Partial, or Incorrect verdict with concise feedback and missing points.
It never changes Anki's scheduling decisions.

## Features

- Manual grading button and `Ctrl+Enter` shortcut
- Optional grading when the answer is revealed
- Structured Groq output with validation and understandable errors
- Background requests that do not freeze Anki
- Retry, request throttling, and an in-memory exact-match cache
- Configurable model, strictness, HTML stripping, and field size limit
- Local display-only verdict overrides

## Install

1. In Anki Desktop, open **Tools → Add-ons → View Files**.
2. Copy or symlink `add_on/anki_llm_grader` into the displayed `addons21`
   directory.
3. Restart Anki.
4. Open **Tools → Add-ons**, select **Anki LLM Grader**, and click **Config**.
5. Paste your Groq API key into `groq_api_key`, then restart Anki again.

The key is stored as plaintext in Anki's local add-on configuration. To avoid
storing it there, leave the setting empty and launch Anki with a
`GROQ_API_KEY` environment variable.

## Card template

Add hidden elements to the front template of each supported typed-answer card:

```html
<div id="llm_prompt" style="display:none">{{Front}}</div>
<div id="llm_answer_key" style="display:none">{{Back}}</div>
<div id="llm_rubric" style="display:none">{{Rubric}}</div>

{{Front}}
{{type:TypedAnswer}}
```

Replace the field names with those from your note type. Omit `llm_rubric` when
there is no rubric field. The IDs themselves must remain unchanged.

## Use

During review, type an answer and click **Grade with AI** or press
`Ctrl+Enter`. The panel shows the verdict, score, missing points, and feedback.
Override buttons alter only the displayed verdict; they do not answer the card
or modify its interval.

Available settings are documented beside Anki's Config editor. Automatic
grading is off by default because it can increase latency and API usage.

## Privacy and scope

Each grading request sends the prompt, canonical answer, typed answer, and
optional rubric to Groq. HTML is stripped and every field is limited to 8,000
characters by default. Review card content before enabling the add-on for
sensitive material.

The add-on supports Anki Desktop only. It does not sync grading history,
modify the scheduler, or support AnkiMobile/AnkiDroid.

## Development

Run the dependency-free unit suite with:

```sh
python3 -m unittest discover -s tests -v
```
