# Anki LLM Grader configuration

- `groq_api_key`: Your Groq API key. It is stored locally in Anki's add-on
  configuration as plaintext. Leave it empty to use the `GROQ_API_KEY`
  environment variable instead.
- `model`: A Groq model ID that supports structured JSON output. The default is
  the production model `openai/gpt-oss-20b`.
- `strictness`: An integer from `0` (lenient) through `2` (strict).
- `strip_html`: Remove HTML markup before sending card text to Groq.
- `max_field_chars`: Maximum number of characters sent from each card field.
  Values are clamped between 100 and 50,000.
- `auto_grade_on_answer`: Grade when the answer is revealed. It is disabled by
  default to avoid unexpected API usage.

Restart Anki after changing these values.
