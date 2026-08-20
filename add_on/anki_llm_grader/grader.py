"""Groq-backed grading logic with no Anki dependencies."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"

RESULT_SCHEMA = {
    "name": "grading_result",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "verdict": {
                "type": "string",
                "enum": ["correct", "partial", "incorrect"],
            },
            "score": {"type": "number", "minimum": 0, "maximum": 1},
            "missing_points": {
                "type": "array",
                "items": {"type": "string"},
            },
            "feedback_short": {"type": "string"},
        },
        "required": ["verdict", "score", "missing_points", "feedback_short"],
    },
}


class GraderError(Exception):
    """An error that can be displayed safely in the reviewer."""


def validate_result(value: Any) -> dict[str, Any]:
    """Validate and normalize the model's grading response."""
    if not isinstance(value, dict):
        raise GraderError("Groq returned a result that was not a JSON object.")

    verdict = value.get("verdict")
    if verdict not in {"correct", "partial", "incorrect"}:
        raise GraderError("Groq returned an invalid verdict.")

    score = value.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise GraderError("Groq returned an invalid score.")

    missing = value.get("missing_points")
    if not isinstance(missing, list) or not all(
        isinstance(point, str) for point in missing
    ):
        raise GraderError("Groq returned invalid missing points.")

    feedback = value.get("feedback_short")
    if not isinstance(feedback, str):
        raise GraderError("Groq returned invalid feedback.")

    return {
        "verdict": verdict,
        "score": max(0.0, min(1.0, float(score))),
        "missing_points": missing,
        "feedback_short": feedback,
    }


class GroqGrader:
    """Small synchronous Groq client intended to run on a worker thread."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        strictness: int = 1,
        timeout_seconds: float = 20,
        min_request_interval: float = 2,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model
        self.strictness = max(0, min(2, int(strictness)))
        self.timeout_seconds = timeout_seconds
        self.min_request_interval = min_request_interval
        self.max_retries = max_retries
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        self._rate_lock = threading.Lock()
        self._last_request_at = 0.0

    def grade(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Grade a payload, using an in-memory cache for exact repeats."""
        if not self.api_key:
            raise GraderError(
                "Missing Groq API key. Open Tools → Add-ons → Anki LLM Grader "
                "→ Config, add your key, and restart Anki."
            )

        normalized = {
            key: str(payload.get(key, ""))
            for key in ("prompt", "answer_key", "user_answer", "rubric")
        }
        if not normalized["user_answer"].strip():
            raise GraderError("Enter an answer before requesting a grade.")
        if not normalized["answer_key"].strip():
            raise GraderError("The card template is missing #llm_answer_key.")

        cache_key = hashlib.sha256(
            json.dumps(normalized, sort_keys=True).encode("utf-8")
        ).hexdigest()
        with self._cache_lock:
            cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        result = self._request_with_retries(normalized)
        with self._cache_lock:
            self._cache[cache_key] = dict(result)
        return result

    def _request_with_retries(self, payload: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                self._apply_rate_limit()
                return self._request(payload)
            except HTTPError as error:
                last_error = error
                if error.code not in {408, 429, 500, 502, 503, 504}:
                    raise self._http_error(error) from error
            except URLError as error:
                last_error = error

            if attempt < self.max_retries:
                time.sleep(0.5 * (2**attempt))

        if isinstance(last_error, HTTPError):
            raise self._http_error(last_error) from last_error
        raise GraderError(f"Could not reach Groq: {last_error}") from last_error

    def _apply_rate_limit(self) -> None:
        with self._rate_lock:
            remaining = self.min_request_interval - (
                time.monotonic() - self._last_request_at
            )
            if remaining > 0:
                time.sleep(remaining)
            self._last_request_at = time.monotonic()

    def _request(self, payload: dict[str, str]) -> dict[str, Any]:
        body = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Grade the user's answer against the answer key. "
                        "Judge meaning, not exact wording. Follow the rubric when present. "
                        f"Strictness is {self.strictness}/2. Return only the requested JSON."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": RESULT_SCHEMA,
            },
        }
        request = Request(
            GROQ_CHAT_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            envelope = json.loads(response.read().decode("utf-8"))

        try:
            content = envelope["choices"][0]["message"]["content"]
            return validate_result(json.loads(content))
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise GraderError("Groq returned an unreadable response. Please retry.") from error

    @staticmethod
    def _http_error(error: HTTPError) -> GraderError:
        if error.code == 401:
            return GraderError("Groq rejected the API key.")
        if error.code == 429:
            return GraderError("Groq rate limit reached. Wait a moment and retry.")
        return GraderError(f"Groq request failed with HTTP {error.code}.")
