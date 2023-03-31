import os
import unittest
from unittest.mock import MagicMock, patch
import openai
import random
import string
from dotenv import load_dotenv
import tests.bugs2 as script

class TestRandomPrompt(unittest.TestCase):
    def test_random_prompt_length(self):
        prompt = script.random_prompt()
        self.assertTrue(5 <= len(prompt) <= 15)

    def test_random_prompt_characters(self):
        prompt = script.random_prompt()
        for char in prompt:
            self.assertIn(char, string.ascii_letters + string.digits)

class TestSaveToMarkdown(unittest.TestCase):
    @patch("builtins.open", new_callable=MagicMock)
    def test_save_to_markdown(self, mock_open):
        prompt = "test_prompt"
        content = "test_content"
        script.save_to_markdown(prompt, content)
        mock_open.assert_called_once_with(f"{prompt}.md", "w")
        mock_open.return_value.write.assert_called_with(f'# {prompt}\n\n{content}')
        mock_open.return_value.write.assert_any_call(content)

class TestMainFunctionality(unittest.TestCase):
    @patch('script.random_prompt')
    @patch('script.save_to_markdown')
    @patch('openai.Completion.create')
    def test_main_functionality(self, mock_create, mock_save_to_markdown, mock_random_prompt):
        mock_random_prompt.return_value = "test_prompt"
        mock_create.return_value = MagicMock(choices=[MagicMock(text=" test_content ")])

        script.num_prompts = 1
        for _ in range(script.num_prompts):
            prompt = script.random_prompt()
            response = openai.Completion.create(
                engine='ada',
                prompt=prompt,
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.5,
            )
            content = response.choices[0].text.strip()
            script.save_to_markdown(prompt, content)

        mock_random_prompt.assert_called_once()
        mock_create.assert_called_once_with(
            engine='ada',
            prompt="test_prompt",
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        mock_save_to_markdown.assert_called_once_with("test_prompt", "test_content")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'])

