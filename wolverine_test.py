import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import shutil
import json
from termcolor import cprint
import wolverine

class TestWolverine(unittest.TestCase):

    def setUp(self):
        self.script_name = "test_script.py"
        self.backup_file = self.script_name + ".bak"
        self.args = ["arg1", "arg2"]

    def tearDown(self):
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)

    def test_run_script_success(self):
        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.return_value = b"Script output"
            output, returncode = wolverine.run_script(self.script_name, *self.args)
            self.assertEqual(output, "Script output")
            self.assertEqual(returncode, 0)

    def test_run_script_failure(self):
        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.side_effect = subprocess.CalledProcessError(1, "cmd", output=b"Error message")
            output, returncode = wolverine.run_script(self.script_name, *self.args)
            self.assertEqual(output, "Error message")
            self.assertEqual(returncode, 1)

    def test_send_error_to_gpt4(self):
        with patch("openai.ChatCompletion.create") as mock_chat_completion:
            mock_choice = MagicMock()
            mock_choice.message.content.strip.return_value = "Suggested changes"
            mock_chat_completion.return_value.choices = [mock_choice]
            response = wolverine.send_error_to_gpt4(self.script_name, self.args, "Error message")
            self.assertEqual(response, "Suggested changes")

    def test_apply_changes(self):
        changes_json = json.dumps([
            {"operation": "Replace", "line": 2, "content": "new_line"},
            {"operation": "Delete", "line": 3},
            {"operation": "InsertAfter", "line": 4, "content": "inserted_line"},
            {"explanation": "Explanation 1"}
        ])

        with open(self.script_name, "w") as f:
            f.write("line1\nline2\nline3\nline4\n")

        shutil.copy(self.script_name, self.backup_file)

        with patch("difflib.unified_diff") as mock_unified_diff:
            mock_unified_diff.return_value = iter(["line1", "line2", "line3", "line4"])
            wolverine.apply_changes(self.script_name, changes_json)

        with open(self.script_name, "r") as f:
            new_content = f.read()

        self.assertEqual(new_content, "line1\nnew_line\nline4\ninserted_line\n")

    def test_main_revert(self):
        sys.argv = ["wolverine.py", self.script_name, "--revert"]
        with patch("shutil.copy") as mock_copy, patch("sys.exit") as mock_exit:
            wolverine.main()
            mock_copy.assert_called_once_with(self.backup_file, self.script_name)
            mock_exit.assert_called_once_with(0)

    def test_main_no_backup_file(self):
        sys.argv = ["wolverine.py", self.script_name, "--revert"]
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)
        with patch("sys.exit") as mock_exit:
            wolverine.main()
            mock_exit.assert_called_once_with(1)

    def test_main_success(self):
        sys.argv = ["wolverine.py", self.script_name, *self.args]
        with patch("wolverine.run_script") as mock_run_script, patch("wolverine.send_error_to_gpt4") as mock_send_error_to_gpt4, patch("wolverine.apply_changes") as mock_apply_changes:
            mock_run_script.side_effect = [("Script output", 0)]
            wolverine.main()
            mock_run_script.assert_called_once_with(self.script_name, *self.args)
            mock_send_error_to_gpt4.assert_not_called()
            mock_apply_changes.assert_not_called()

    def test_main_failure_and_fix(self):
        sys.argv = ["wolverine.py", self.script_name, *self.args]
        with patch("wolverine.run_script") as mock_run_script, patch("wolverine.send_error_to_gpt4") as mock_send_error_to_gpt4, patch("wolverine.apply_changes") as mock_apply_changes:
            mock_run_script.side_effect = [("Error message", 1), ("Script output", 0)]
            mock_send_error_to_gpt4.return_value = json.dumps([
                {"operation": "Replace", "line": 2, "content": "new_line"},
                {"explanation": "Explanation 1"}
            ])
            wolverine.main()
            self.assertEqual(mock_run_script.call_count, 2)
            mock_send_error_to_gpt4.assert_called_once_with(self.script_name, self.args, "Error message")
            mock_apply_changes.assert_called_once()

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
