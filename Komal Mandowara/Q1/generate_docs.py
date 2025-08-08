import ast
import os

def extract_function_docs(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)

    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    docs = []

    for func in functions:
        func_name = func.name
        args = [arg.arg for arg in func.args.args]
        docstring = ast.get_docstring(func) or "No docstring provided."

        doc = f"""### Function: `{func_name}`

**Arguments:** `{', '.join(args)}`

**Description:**  
{docstring}

---
"""
        docs.append(doc)

    return docs

def save_to_markdown(docs, output_file="docs.md"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 📄 Function Documentation\n\n")
        for doc in docs:
            f.write(doc + "\n")

def list_python_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".py")]

if __name__ == "__main__":
    directory = "."  # current directory
    py_files = list_python_files(directory)

    if not py_files:
        print("❌ No Python files found in the current directory.")
    else:
        print("📂 Available Python files:")
        for idx, file in enumerate(py_files):
            print(f"{idx + 1}. {file}")

        try:
            choice = int(input("\n🔢 Enter the number of the file to document: ")) - 1
            if 0 <= choice < len(py_files):
                selected_file = py_files[choice]
                file_path = os.path.join(directory, selected_file)
                docs = extract_function_docs(file_path)
                save_to_markdown(docs)
                print(f"✅ Markdown documentation saved to docs.md for {selected_file}")
            else:
                print("⚠️ Invalid selection.")
        except ValueError:
            print("⚠️ Please enter a valid number.")
