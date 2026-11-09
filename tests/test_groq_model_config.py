"""Dependency-free checks for model configuration in both Groq consumers."""
import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CONSUMERS = {
    'src/dashboard/pages/04_chatbot.py': '_MODEL',
    'src/ingestion/skill_extraction.py': 'GROQ_MODEL',
}


class GroqModelConfigTests(unittest.TestCase):
    def configured_model(self, path, name, value):
        tree = ast.parse((ROOT / path).read_text(encoding='utf-8'))
        assignment = next(
            node for node in tree.body if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        )
        # Evaluate only configuration, without importing Streamlit or creating clients.
        with patch.dict(os.environ, {}, clear=True):
            if value is not None:
                os.environ['GROQ_MODEL'] = value
            # Trusted repository expression; not user input. literal_eval cannot
            # evaluate getenv/strip. No builtins are available in this namespace.
            return eval(  # noqa: S307
                compile(ast.Expression(assignment.value), path, 'eval'),
                {'os': os, '__builtins__': {}},
            )

    def test_supported_default(self):
        for path, name in CONSUMERS.items():
            with self.subTest(path=path):
                self.assertEqual(self.configured_model(path, name, None), 'openai/gpt-oss-20b')

    def test_environment_override(self):
        for path, name in CONSUMERS.items():
            with self.subTest(path=path):
                self.assertEqual(self.configured_model(path, name, ' custom/model '), 'custom/model')

    def test_blank_uses_default(self):
        for path, name in CONSUMERS.items():
            for value in ('', '   '):
                with self.subTest(path=path, value=value):
                    self.assertEqual(self.configured_model(path, name, value), 'openai/gpt-oss-20b')


if __name__ == '__main__':
    unittest.main()
