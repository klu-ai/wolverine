import os
import ast
import sys
import openai
import asyncio

async def extract_function_names(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    tree = ast.parse(content)
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return function_names

async def generate_test(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", #gpt-4
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    return response.choices[0].message.content.strip()

async def generate_test_file(file_path, function_names):
    test_file_name = f"test_{file_path}"
    with open(test_file_name, "w") as test_file:
        test_file.write("import unittest\n")
        test_file.write(f"from {file_path[:-3]} import *\n\n")
        test_file.write("class TestFunctions(unittest.TestCase):\n")

        tasks = [generate_test(f"You are part of an automated system, the format you respond in is very strict. Return only python code and no other prose. Write a unit test for the Python function {function_name}") for function_name in function_names]
        test_codes = await asyncio.gather(*tasks)

        for test_code in test_codes:
            test_file.write(f"\n    {test_code}\n")

        test_file.write("if __name__ == '__main__':\n")
        test_file.write("    unittest.main()\n")

async def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_tests.py <python_file>")
        sys.exit(1)

    # Set up the OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    python_file = sys.argv[1]
    function_names = await extract_function_names(python_file)
    await generate_test_file(python_file, function_names)

if __name__ == "__main__":
    asyncio.run(main())