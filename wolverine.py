import difflib
import json
import os
import shutil
import subprocess
import sys
import openai
from termcolor import cprint

openai.api_key = os.getenv("OPENAI_API_KEY")

def run_script(script_name, *args):
    try:
        result = subprocess.check_output([sys.executable, script_name, *args], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), e.returncode
    return result.decode("utf-8"), 0

def send_error_to_gpt4(file_path, args, error_message):
    with open(file_path, "r") as f: file_lines = f.readlines()
    file_with_lines = [f"{i + 1}: {line}" for i, line in enumerate(file_lines)]
    with open("prompt.txt") as f: initial_prompt_text = f.read()
    prompt = f"{initial_prompt_text}\n\nHere is the script that needs fixing:\n\n{''.join(file_with_lines)}\n\nHere are the arguments it was provided:\n\n{args}\n\nHere is the error message:\n\n{error_message}\nPlease provide your suggested changes, and remember to stick to the exact format as described above."
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=1.0)
    return response.choices[0].message.content.strip()

def apply_changes(file_path, changes_json):
    with open(file_path, "r") as f: original_file_lines = f.readlines()
    changes = json.loads(changes_json)
    operation_changes = [change for change in changes if "operation" in change]
    explanations = [change["explanation"] for change in changes if "explanation" in change]
    operation_changes.sort(key=lambda x: x["line"], reverse=True)
    file_lines = original_file_lines.copy()
    for change in operation_changes:
        operation, line, content = change["operation"], change["line"], change["content"]
        if operation == "Replace": file_lines[line - 1] = content + "\n"
        elif operation == "Delete": del file_lines[line - 1]
        elif operation == "InsertAfter": file_lines.insert(line, content + "\n")
    with open(file_path, "w") as f: f.writelines(file_lines)
    cprint("Explanations:", "blue")
    for explanation in explanations: cprint(f"- {explanation}", "blue")
    print("\nChanges:")
    diff = difflib.unified_diff(original_file_lines, file_lines, lineterm="")
    for line in diff:
        if line.startswith("+"): cprint(line, "green", end="")
        elif line.startswith("-"): cprint(line, "red", end="")
        else: print(line, end="")

def main():
    if len(sys.argv) < 3:
        print("Usage: wolverine.py <script_name> <arg1> <arg2> ... [--revert]")
        sys.exit(1)

    script_name, args = sys.argv[1], sys.argv[2:]
    if "--revert" in args:
        backup_file = script_name + ".bak"
        if os.path.exists(backup_file): shutil.copy(backup_file, script_name); print(f"Reverted changes to {script_name}"); sys.exit(0)
        else: print(f"No backup file found for {script_name}"); sys.exit(1)
    shutil.copy(script_name, script_name + ".bak")

    while True:
        output, returncode = run_script(script_name, *args)
        if returncode == 0:
            cprint("Script ran successfully.", "blue")
            print("Output:", output)
            break
        else:
            cprint("Script crashed. Trying to fix...", "blue")
            print("Output:", output)
            json_response = send_error_to_gpt4(script_name, args, output)
            # print("JSON Response:", json_response)  # Add this line to print the JSON 
            apply_changes(script_name, json_response)
            cprint("Changes applied. Rerunning...", "blue")

if __name__ == "__main__":
    main()