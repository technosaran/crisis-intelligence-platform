import os, re

dirs_to_skip = ['node_modules', 'venv', '.venv', 'dist', 'build', '.git', '__pycache__', '.next']
with open('todos.txt', 'w', encoding='utf-8') as f:
    for root, dirs, files in os.walk('.'):
        if any(skip in root.replace('\\\\', '/').split('/') for skip in dirs_to_skip):
            continue
        for file in files:
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                        for i, line in enumerate(infile):
                            if re.search(r'\b(TODO|FIXME|pass)\b', line):
                                f.write(f'{filepath}:{i+1} {line.strip()}\n')
                except Exception as e:
                    pass
