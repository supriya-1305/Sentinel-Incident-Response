import unittest

from app.llm import build_system_prompt


class LLMPromptTests(unittest.TestCase):
    def test_prompt_requires_three_step_plan_and_explicit_citations(self):
        prompt = build_system_prompt()
        self.assertIn("3-step Incident Response Plan", prompt)
        self.assertIn("Triage", prompt)
        self.assertIn("Containment", prompt)
        self.assertIn("Eradication", prompt)
        self.assertIn("citations", prompt.lower())


if __name__ == "__main__":
    unittest.main()
