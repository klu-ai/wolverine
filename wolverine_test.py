import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess
import os
import shutil
import json
import difflib
import openai
from wolverine import run_script, send_error_to_gpt4, apply_changes, main


class TestWolverine(unittest.TestCase):

    def setUp(self):
        self.script_name = "wolverine_test.py"
        self.backup_file = self.script_name + ".bak"

    def tearDown(self):
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)

    def test_run_script_success(self):
        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.return_value = b"Success"
            output, returncode = run_script(self.script_name)
            self.assertEqual(output, "Success")
            self.assertEqual(returncode, 0)

    def test_run_script_failure(self):
        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.side_effect = subprocess.CalledProcessError(
                1, "cmd")
            mock_check_output.return_value = b"Error"
            output, returncode = run_script(self.script_name)
            self.assertEqual(output, "Error")
            self.assertEqual(returncode, 1)

    @patch("openai.ChatCompletion.create")
    def test_send_error_to_gpt4(self, mock_chat_completion):
        mock_chat_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Suggested changes"))])
        response = send_error_to_gpt4(
            self.script_name, ["arg1", "arg2"], "Error message")
        self.assertEqual(response, "Suggested changes")

    def test_apply_changes(self):
        changes_json = json.dumps([
            {"operation": "Replace", "line": 1,
                "content": "print('Hello, World!')"},
            {"explanation": "Changed print statement"}
        ])
        with open(self.script_name, "w") as f:
            f.write("print('Hello')")
        apply_changes(self.script_name, changes_json)
        with open(self.script_name, "r") as f:
            content = f.read()
        self.assertEqual(content, "print('Hello, World!')\n")

    @patch("wolverine.run_script")
    @patch("wolverine.send_error_to_gpt4")
    @patch("wolverine.apply_changes")
    def test_main(self, mock_apply_changes, mock_send_error_to_gpt4, mock_run_script):
        mock_run_script.side_effect = [("Error", 1), ("Success", 0)]
        mock_send_error_to_gpt4.return_value = json.dumps([
            {"operation": "Replace", "line": 1,
                "content": "print('Hello, World!')"},
]
)
            {"explanation": "Changed print statement"}
        self.assertTrue(os.path.exists(self.backup_file))

    test_args = ['wolverine.py', self.script_name, 'arg1', 'arg2', '--revert']
    with patch.object(sys, "argv", test_args):
            main()

    self.assertTrue(os.path.exists(self.backup_file))
    mock_apply_changes.assert_called_once()

if __name__ == "__main__":
    unittest.main()