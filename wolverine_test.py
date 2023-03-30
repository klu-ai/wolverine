import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from wolverine import run_script, send_error_to_gpt4, apply_changes, main

class TestWolverine(unittest.TestCase):
    def setUp(self):
        self.script_name = "wolverine_test.py"
        self.backup_file = self.script_name + ".bak"

    def tearDown(self):
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)

    def test_run_script_success(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!')")

        output, returncode = run_script(self.script_name)
        self.assertEqual(output.strip(), "Hello, World!")
        self.assertEqual(returncode, 0)

    def test_run_script_failure(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!'\n")

        output, returncode = run_script(self.script_name)
        self.assertNotEqual(returncode, 0)

    @patch("wolverine.openai.ChatCompletion.create")
    def test_send_error_to_gpt4(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='{"operation": "Replace", "line": 1, "content": "print(\\"Hello, World!\\")"}'))])

        file_path = self.script_name
        args = []
        error_message = "SyntaxError: EOL while scanning string literal"

        with open(file_path, "w") as f:
            f.write("print('Hello, World!'\n")

        changes_json = send_error_to_gpt4(file_path, args, error_message)
        self.assertEqual(changes_json, '{"operation": "Replace", "line": 1, "content": "print(\\"Hello, World!\\")"}')

    def test_apply_changes(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!'\n")

        changes_json = '[{"operation": "Replace", "line": 1, "content": "print(\\"Hello, World!\\")"}]'
        apply_changes(self.script_name, changes_json)

        with open(self.script_name, "r") as f:
            content = f.read()

        self.assertEqual(content.strip(), 'print("Hello, World!")')

    @patch("wolverine.run_script")
    @patch("wolverine.send_error_to_gpt4")
    @patch("wolverine.apply_changes")
    def test_main(self, mock_apply_changes, mock_send_error_to_gpt4, mock_run_script):
        mock_run_script.side_effect = [("SyntaxError: EOL while scanning string literal", 1), ("Hello, World!", 0)]
        mock_send_error_to_gpt4.return_value = '[{"operation": "Replace", "line": 1, "content": "print(\\"Hello, World!\\")"}]'

    def test_main_revert(self):
        main()
f.write("print('Hello, World!')")

shutil.copy(self.script_name, self.backup_file)

    with open(self.script_name, "w") as f:
            f.write("print('Hello, World!'\n")

        with patch("sys.argv", ["wolverine.py", self.script_name, "--revert"]):
            main()

        with open(self.script_name, "r") as f:
            content = f.read()

        self.assertEqual(content.strip(), "print('Hello, World!')")

if __name__ == "__main__":
    unittest.main()