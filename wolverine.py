# Import necessary libraries
import difflib
import json
import os
import shutil
import subprocess
import sys
import openai
from termcolor import cprint

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to run a script and return its output and return code
def run_script(script_name, *args):
    try:
        # Run the script and capture its output
        result = subprocess.check_output([sys.executable, script_name, *args], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # If an error occurs, return the error output and return code
        return e.output.decode("utf-8"), e.returncode
    # If the script runs successfully, return the output and a return code of 0
    return result.decode("utf-8"), 0

# Function to send the error to GPT-4 and receive suggested changes
def send_error_to_gpt4(file_path, args, error_message):
    # Read the file and create a list of lines with line numbers
    with open(file_path, "r") as f:
        file_lines = f.readlines()
    file_with_lines = [f"{i + 1}: {line}" for i, line in enumerate(file_lines)]

    # Read the initial prompt text
    with open("prompt.txt") as f:
        initial_prompt_text = f.read()

    # Create the prompt for GPT-4
    prompt = f"{initial_prompt_text}\n\nHere is the script that needs fixing:\n\n{''.join(file_with_lines)}\n\nHere are the arguments it was provided:\n\n{args}\n\nHere is the error message:\n\n{error_message}\nPlease provide your suggested changes, and remember to stick to the exact format as described above."

    # Send the prompt to GPT-4 and get the response
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.3)
    return response.choices[0].message.content.strip()

# Function to apply the changes suggested by GPT-4
def apply_changes(file_path, changes_json):
    # Read the original file
    with open(file_path, "r") as f:
        original_file_lines = f.readlines()

    # Parse the JSON changes
    changes = json.loads(changes_json)
    operation_changes = [change for change in changes if "operation" in change]
    explanations = [change["explanation"] for change in changes if "explanation" in change]

    # Sort the operation changes in reverse order by line number
    operation_changes.sort(key=lambda x: x["line"], reverse=True)

    # Apply the changes to the file
    file_lines = original_file_lines.copy()
    for change in operation_changes:
        operation, line, content = change["operation"], change["line"], change["content"]
        if operation == "Replace":
            file_lines[line - 1] = content + "\n"
        elif operation == "Delete":
            del file_lines[line - 1]
        elif operation == "InsertAfter":
            file_lines.insert(line, content + "\n")

    # Write the modified file
    with open(file_path, "w") as f:
        f.writelines(file_lines)

    # Print the explanations and changes
    cprint("Explanations:", "blue")
    for explanation in explanations:
        cprint(f"- {explanation}", "blue")
    print("\nChanges:")
    diff = difflib.unified_diff(original_file_lines, file_lines, lineterm="")
    for line in diff:
        if line.startswith("+"):
            cprint(line, "green", end="")
        elif line.startswith("-"):
            cprint(line, "red", end="")
        else:
            print(line, end="")

# Main function
def main():
    # Check for correct usage
    if len(sys.argv) < 3:
        print("Usage: wolverine.py <script_name> <arg1> <arg2> ... [--revert]")
        sys.exit(1)

    # Get the script name and arguments
    script_name, args = sys.argv[1], sys.argv[2:]

    # Check for the revert option
    if "--revert" in args:
        backup_file = script_name + ".bak"
        if os.path.exists(backup_file):
            shutil.copy(backup_file, script_name)
            print(f"Reverted changes to {script_name}")
            sys.exit(0)
        else:
            print(f"No backup file found for {script_name}")
            sys.exit(1)

    # Create a backup of the original file
    shutil.copy(script_name, script_name + ".bak")

    # Main loop to run the script, fix errors, and rerun
    while True:
        # Run the script and get the output and return code
        output, returncode = run_script(script_name, *args)
        # If the script runs successfully, print the output and exit the loop
        if returncode == 0:
            cprint("Script ran successfully.", "blue")
            print("Output:", output)
            break
        else:
            # If the script crashes, try to fix it using GPT-4
            cprint("Script crashed. Trying to fix...", "blue")
            print("Output:", output)
            # Send the error to GPT-4 and get the suggested changes
            json_response = send_error_to_gpt4(script_name, args, output)
            # Uncomment the following line to print the JSON response
            # print("JSON Response:", json_response)  # Add this line to print the JSON 
            # Apply the changes suggested by GPT-4
            apply_changes(script_name, json_response)
            # Rerun the script with the applied changes
            cprint("Changes applied. Rerunning...", "blue")

if __name__ == "__main__":
    main()