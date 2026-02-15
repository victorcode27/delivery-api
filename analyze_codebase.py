import os
import ast
import re

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    imports = set()
    paths = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return imports, paths

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                if re.search(r'[\\/]', node.value) and len(node.value) < 100:
                    # heuristic for paths
                    if not re.match(r'^[a-zA-Z0-9_]+$', node.value): # skip simple words
                         paths.append(node.value)

    return imports, paths

def main():
    root_dir = "."
    all_imports = set()
    suspicious_paths = []

    for dirpath, _, filenames in os.walk(root_dir):
        if "venv" in dirpath or "env" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                imports, paths = analyze_file(filepath)
                all_imports.update(imports)
                if paths:
                    suspicious_paths.append((filename, paths))

    print("Detected Imports:")
    for imp in sorted(all_imports):
        print(f"  {imp}")

    print("\nSuspicious Paths (Potential Hardcoded):")
    for filename, paths in suspicious_paths:
        for p in paths:
             # filter somewhat
             if " " in p or "\\" in p or "/" in p:
                if not p.startswith("http") and not p.startswith("%") and not p.startswith("SELECT") and not p.startswith("INSERT") and len(p) > 3:
                     print(f"  {filename}: {p}")

if __name__ == "__main__":
    main()
