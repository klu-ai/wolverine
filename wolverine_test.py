import unittest
import os
import shutil
from unittest.mock import patch
from wolverine import run_script, send_error_to_gpt4, apply_changes, main

class TestWolverine(unittest.TestCase):
    def setUp(self):
        self.script_name = "wolverine_test.py"
        self.backup_file = self.script_name + ".bak"
        self.args = ["arg1", "arg2"]

    def tearDown(self):
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)

    def test_run_script_success(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!')")

        output, returncode = run_script(self.script_name, *self.args)
        self.assertEqual(output.strip(), "Hello, World!")
        self.assertEqual(returncode, 0)

    def test_run_script_failure(self):
        with open(self.script_name, "w") as f:
            f.write("print(1 / 0)")

        output, returncode = run_script(self.script_name, *self.args)
        self.assertIn("ZeroDivisionError", output)
        self.assertNotEqual(returncode, 0)

    @patch("wolverine.openai.ChatCompletion.create")
    def test_send_error_to_gpt4(self, mock_create):
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"operation": "Replace", "line": 1, "content": "print(1 / 1)"}'
                    }
                }
            ]
        }

        with open(self.script_name, "w") as f:
            f.write("print(1 / 0)")

        output, _ = run_script(self.script_name, *self.args)
        changes_json = send_error_to_gpt4(self.script_name, self.args, output)
        self.assertEqual(changes_json, '{"operation": "Replace", "line": 1, "content": "print(1 / 1)"}')

    def test_apply_changes(self):
        with open(self.script_name, "w") as f:
            f.write("print(1 / 0)")

        changes_json = '[{"operation": "Replace", "line": 1, "content": "print(1 / 1)"}]'
        apply_changes(self.script_name, changes_json)

        with open(self.script_name, "r") as f:
            modified_file = f.read()

        self.assertEqual(modified_file.strip(), "print(1 / 1)")

    @patch("wolverine.openai.ChatCompletion.create")
    def test_main(self, mock_create):
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"operation": "Replace", "line": 1, "content": "print(1 / 1)"}'
                    }
                }
            ]
        }

        with open(self.script_name, "w") as f:
            f.write("print(1 / 0)")

        with patch("sys.argv", ["wolverine.py", self.script_name, *self.args]):
            main()

        with open(self.script_name, "r") as f:
            modified_file = f.read()

        self.assertEqual(modified_file.strip(), "print(1 / 1)")

    def test_revert_option(self):
        with open(self.script_name, "w") as f:
            f.write("print('Hello, World!')")
        shutil.copy(self.script_name, self.backup_file)

        with open(self.script_name, "w") as f:
            f.write("print('Modified')")

        with patch("sys.argv", ["wolverine.py", self.script_name, *self.args, "--revert"]):
            main()

        with open(self.script_name, "r") as f:
            reverted_file = f.read()

        self.assertEqual(reverted_file.strip(), "print('Hello, World!')")

if __name__ == "__main__":
    unittest.main()