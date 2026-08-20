import importlib.util
import pathlib
import unittest


GRADER_PATH = (
    pathlib.Path(__file__).parents[1]
    / "add_on"
    / "anki_llm_grader"
    / "grader.py"
)
SPEC = importlib.util.spec_from_file_location("grader", GRADER_PATH)
grader = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(grader)


class FakeGrader(grader.GroqGrader):
    def __init__(self):
        super().__init__("test-key", min_request_interval=0)
        self.calls = 0

    def _request_with_retries(self, payload):
        self.calls += 1
        return {
            "verdict": "correct",
            "score": 1.0,
            "missing_points": [],
            "feedback_short": "Good answer.",
        }


class GraderTests(unittest.TestCase):
    def test_validate_result(self):
        result = grader.validate_result(
            {
                "verdict": "partial",
                "score": 0.6,
                "missing_points": ["One detail"],
                "feedback_short": "Mostly right.",
            }
        )
        self.assertEqual(result["verdict"], "partial")

    def test_rejects_invalid_verdict(self):
        with self.assertRaises(grader.GraderError):
            grader.validate_result(
                {
                    "verdict": "maybe",
                    "score": 0.5,
                    "missing_points": [],
                    "feedback_short": "No.",
                }
            )

    def test_repeated_payload_uses_cache(self):
        client = FakeGrader()
        payload = {
            "prompt": "Question",
            "answer_key": "Answer",
            "user_answer": "Answer",
            "rubric": "",
        }
        self.assertEqual(client.grade(payload), client.grade(payload))
        self.assertEqual(client.calls, 1)

    def test_requires_user_answer(self):
        with self.assertRaises(grader.GraderError):
            FakeGrader().grade({"answer_key": "Answer", "user_answer": ""})


if __name__ == "__main__":
    unittest.main()
