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

def process_directory(directory):
    all_docs = []
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "generate_docs.py":
            path = os.path.join(directory, filename)
            docs = extract_function_docs(path)
            all_docs.extend(docs)
    return all_docs

def save_to_markdown(docs, output_file="docs.md"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 📄 Function Documentation\n\n")
        for doc in docs:
            f.write(doc + "\n")

if __name__ == "__main__":
    directory = "."  # current directory
    docs = process_directory(directory)
    save_to_markdown(docs)
    print("✅ Markdown documentation saved to docs.md")
