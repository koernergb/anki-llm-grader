# Anki LLM Grader configuration

- `groq_api_key`: Your Groq API key. It is stored locally in Anki's add-on
  configuration as plaintext. Leave it empty to use the `GROQ_API_KEY`
  environment variable instead.
- `model`: A Groq model ID that supports structured JSON output. The default is
  the production model `openai/gpt-oss-20b`.
- `strictness`: An integer from `0` (lenient) through `2` (strict).

Restart Anki after changing these values.
