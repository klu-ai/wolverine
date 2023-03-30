# Wolverine

Fork from bio-bootloader/wolverine
## About

Give your python scripts regenerative healing abilities!

Run your scripts with Wolverine and when they crash, GPT-4 edits them and explains what went wrong. Even if you have many bugs it will repeatedly rerun until it's fixed.

## Setup

    python3 -m venv venv
    pip install -r requirements.txt
    source venv/bin/activate

Add your OpenAI API key to your system environment variables as `OPENAI_API_KEY`. 

## Example Usage

    python wolverine.py buggy_script.py "subtract" 20 3
