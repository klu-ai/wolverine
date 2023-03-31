import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil

import wolverine

class TestWolverine(unittest.TestCase):

    def setUp(self):
        self.script_name = "wolverine_test.py"
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_run_script(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!')")

        output, returncode = wolverine.run_script(self.script_name)
        self.assertEqual(output.strip(), "Hello, World!")
        self.assertEqual(returncode, 0)

    def test_run_script_with_error(self):
        with open(self.script_name, "w") as f:
            f.write("print(1/0)")

        output, returncode = wolverine.run_script(self.script_name)
        self.assertIn("ZeroDivisionError", output)
        self.assertNotEqual(returncode, 0)

    @patch("wolverine.openai.ChatCompletion.create")
    def test_send_error_to_gpt4(self, mock_chat_completion):
        mock_chat_completion.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='{"operation": "Replace", "line": 1, "content": "print(1)"}'))])

        file_path = "test_file.py"
        args = ["arg1", "arg2"]
        error_message = "ZeroDivisionError: division by zero"

        with open(file_path, "w") as f:
            f.write("print(1/0)")

        response = wolverine.send_error_to_gpt4(file_path, args, error_message)
        self.assertEqual(response, '{"operation": "Replace", "line": 1, "content": "print(1)"}')

    def test_apply_changes(self):
        file_path = "test_file.py"
        changes_json = '[{"operation": "Replace", "line": 1, "content": "print(1)"}]'

        with open(file_path, "w") as f:
            f.write("print(1/0)")

        wolverine.apply_changes(file_path, changes_json)

        with open(file_path, "r") as f:
            modified_file = f.read()

        self.assertEqual(modified_file, "print(1)\n")

    @patch("wolverine.run_script")
    @patch("wolverine.send_error_to_gpt4")
    @patch("wolverine.apply_changes")
    def test_main(self, mock_apply_changes, mock_send_error_to_gpt4, mock_run_script):
        mock_run_script.side_effect = [("ZeroDivisionError: division by zero", 1), ("Hello, World!", 0)]
        mock_send_error_to_gpt4.return_value = '[{"operation": "Replace", "line": 1, "content": "print(1)"}]'

        with open(self.script_name, "w") as f:
            f.write("print(1/0)")

        sys.argv = ["wolverine.py", self.script_name]
        wolverine.main()

        mock_run_script.assert_called()
        mock_send_error_to_gpt4.assert_called()
        mock_apply_changes.assert_called()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)    