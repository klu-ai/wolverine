import openai
import sys
import os

# Import additional libraries for colored terminal output
from termcolor import colored

# Retrieve the input file path from the command line arguments
input_file_path = sys.argv[1]

# Set the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Print a status message
print(colored("Reading the input file...", "yellow"))

# Open the input file and read its content
with open(input_file_path, 'r') as file:
    input_file_content = file.read()

    # Create a prompt to summarize the Python code
    prompt = f"Summarize the following Python code:\n\n```python\n{input_file_content}\n```"

    # Print a status message
    print(colored("Requesting a summary from the OpenAI API...", "yellow"))

    # Request a summary from the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Extract the summary from the API response
    summary = response.choices[0].text.strip()
    print(colored(summary, "yellow"))

# Print a status message
print(colored("Generating Python unit tests...", "yellow"))

# Create an output file path for the generated unit tests
output_file_path = os.path.splitext(input_file_path)[0] + "_test.py"

# Create a chat completion request for generating Python unit tests
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert python programming assistant. Return only highly optimized python code."},
        {"role": "user", "content": f"Generate Python unit tests for the following Python file:\n{input_file_content}\n\nWhich contains {summary}\n\nEnsure that the generated tests cover a variety of edge cases and common scenarios.\n\nself.script_name = {output_file_path}"}
    ],
    temperature=0.1,
)

# Extract the generated unit tests code from the API response
unit_tests_code = response.choices[0].message.content.strip()
print(colored(unit_tests_code, "yellow"))

# Print a status message
print(colored("Writing the generated unit tests to the output file...", "yellow"))

# Write the generated unit tests code to the output file
with open(output_file_path, 'w') as output_file:
    output_file.write(unit_tests_code)

# Print the location of the generated unit tests file
print(colored(f"Generated unit tests saved to: {output_file_path}", "green"))