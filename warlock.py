import openai
import os
import sys
import subprocess
from termcolor import colored

def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(colored("Welcome to Warlock, the Python Script Generator that self heals errors!", "cyan"))

    # Step 1: Take user input
    print(colored("Enter your instructions for your desired script:", "yellow"))
    user_input = input()

    # Step 2: Generate a dynamic filename based on the user_input
    filename = generate_filename(user_input)

    # Step 3: Generate Python script using GPT-4 chat completion
    print(colored(f"Generating {filename} using GPT-4...", "cyan"))
    generated_script = generate_script(user_input)

    # Step 4: Save the script to a file
    with open(filename, "w") as f:
        f.write(generated_script)
    print(colored(f"Script saved to {filename}", "green"))

    # Step 5: Call "python wolverine.py {filename} {main}"
    print(colored("Improving the code using wolverine.py...", "cyan"))
    result = subprocess.run(["python", "wolverine.py", filename, "main"], capture_output=True, text=True)

    if "Script ran successfully." in result.stdout:
        print(colored("Script ran successfully.", "green"))
        sys.exit(0)
    else:
        print(colored("An error occurred while running the script.", "red"))
        print(colored(result.stderr, "red"))

def generate_script(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert python programming assistant. Return optimized code that runs. DO NOT RETURN PROSE. Ouput the python code block for: "},
            {"role": "user", "content": user_input}
        ],
        temperature=0.123,
    )

    generated_script = response.choices[0].message.content.strip()
    return extract_code(generated_script) #[3:-3]


def extract_code(response):
    code = []
    in_code_block = False

    for line in response.split('\n'):
        if line.strip() == '```python':
            in_code_block = True
            continue
        elif line.strip() == '```':
            in_code_block = False

        if in_code_block:
            code.append(line)

    return in_code_block

def generate_filename(user_input):
    prompt = f"Summarize the following Python code into a short filename without the extension (action_object) :\n\n```python\n{user_input}\n```"

    print(colored("Requesting a summary from the OpenAI API...", "yellow"))

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.1,
    )

    summary = response.choices[0].text.strip()
    filename = summary.replace(" ", "_").lower() + ".py"

    return filename

if __name__ == "__main__":
    main()