import ast
import sys

def extract_function_names(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    tree = ast.parse(content)
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return function_names

def generate_test_file(file_path, function_names):
    test_file_name = f"test_{file_path}"
    with open(test_file_name, "w") as test_file:
        test_file.write("import unittest\n")
        test_file.write(f"from {file_path[:-3]} import *\n\n")
        test_file.write("class TestFunctions(unittest.TestCase):\n")

        for function_name in function_names:
            test_file.write(f"\n    def test_{function_name}(self):\n")
            test_file.write(f"        # TODO: Add test cases for {function_name}\n")
            test_file.write(f"        pass\n\n")

        test_file.write("if __name__ == '__main__':\n")
        test_file.write("    unittest.main()\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_tests.py <python_file>")
        sys.exit(1)

    python_file = sys.argv[1]
    function_names = extract_function_names(python_file)
    generate_test_file(python_file, function_names)