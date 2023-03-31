import os
import openai
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API client
openai.api_key = api_key

# Define random prompt generator
def random_prompt():
    prompt_length = random.randint(5, 15)
    prompt = ''.join(random.choices(string.ascii_letters + string.digits, k=prompt_length))
    return prompt

# Define function to save prompt to a Markdown file
def save_to_markdown(prompt, content):
    file_name = f"{prompt}.md"
    with open(file_name, "w") as f:
        f.write(f"# {prompt}\n\n")
        f.write(content)

# Generate random prompts and save them to Markdown files
num_prompts = 1
for _ in range(num_prompts):
    prompt = random_prompt()
    response = openai.Completion.create(
        engine='ada',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    content = response.choices[0].text.strip()
    save_to_markdown(prompt, content)