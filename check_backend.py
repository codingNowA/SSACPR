import os
backend = r'D:\test\backend'
issues = []

# Check all from app.* imports for module existence
for root, dirs, files in os.walk(backend):
    for fn in files:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                s = line.strip()
                if s.startswith('from app.') and not s.startswith('#'):
                    mod = s.split('import')[0].replace('from ','').strip()
                    parts = mod.split('.')
                    pkg_path = os.path.join(backend, *parts, '__init__.py')
                    mod_path = os.path.join(backend, *parts[:-1], parts[-1] + '.py')
                    if not os.path.exists(pkg_path) and not os.path.exists(mod_path):
                        issues.append(f'MISSING IMPORT: {fp} L{i}: {s}')

# Check for BOM
for root, dirs, files in os.walk(backend):
    for fn in files:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'rb') as f:
            if f.read(3) == b'\xef\xbb\xbf':
                issues.append(f'BOM: {fp}')

# Check for 4-quote docstrings
for root, dirs, files in os.walk(backend):
    for fn in files:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                if '""""' in line:
                    issues.append(f'4QUOTE: {fp} L{i}: {line.strip()}')

for iss in sorted(issues):
    print(iss)
if not issues:
    print('All checks passed - no issues found')