import os, sys, json, re

backend = r'D:\test\backend'
frontend = r'D:\test\frontend'
SEP = '=' * 60

# ========== 1. Backend Import Check ==========
print(SEP)
print('1. BACKEND - Python Import Check')
print(SEP)
issues = []
for root, dirs, files in os.walk(backend):
    # skip __pycache__ and tests
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for fn in files:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        try:
            with open(fp, 'r', encoding='utf-8-sig') as f:
                for i, line in enumerate(f, 1):
                    s = line.strip()
                    if s.startswith('from app.') and not s.startswith('#'):
                        mod = s.split('import')[0].replace('from ','').strip()
                        parts = mod.split('.')
                        pkg_path = os.path.join(backend, *parts, '__init__.py')
                        mod_path = os.path.join(backend, *parts[:-1], parts[-1] + '.py')
                        if not os.path.exists(pkg_path) and not os.path.exists(mod_path):
                            rel = os.path.relpath(fp, backend)
                            issues.append(f'  MISSING: {rel} L{i}: {s}')
        except Exception as e:
            issues.append(f'  ERROR reading {fp}: {e}')
if issues:
    print('\n'.join(issues))
else:
    print('  All imports OK')

# ========== 2. BOM Check ==========
print(f'\n{SEP}')
print('2. BACKEND - BOM & 4-Quote Check')
print(SEP)
bom_files = []
quote_files = []
for root, dirs, files in os.walk(backend):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for fn in files:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'rb') as f:
            head = f.read(3)
        if head == b'\xef\xbb\xbf':
            bom_files.append(os.path.relpath(fp, backend))
        with open(fp, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                if '""""' in line:
                    quote_files.append(f'{os.path.relpath(fp, backend)} L{i}')
if bom_files:
    print(f'  BOM found in: {bom_files}')
else:
    print('  No BOM files')
if quote_files:
    print(f'  4-quote found in: {quote_files}')
else:
    print('  No 4-quote docstrings')

# ========== 3. Backend .env ==========
print(f'\n{SEP}')
print('3. BACKEND - .env Configuration')
print(SEP)
env_path = os.path.join(backend, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith('#'):
                # mask secrets
                key = s.split('=')[0]
                val = s.split('=',1)[1] if '=' in s else ''
                if any(kw in key.upper() for kw in ['KEY','SECRET','PASSWORD','TOKEN']):
                    print(f'  {key}=***masked***')
                else:
                    print(f'  {key}={val}')
else:
    print('  .env NOT FOUND!')

# ========== 4. Backend main.py & CORS ==========
print(f'\n{SEP}')
print('4. BACKEND - CORS & App Config')
print(SEP)
main_path = os.path.join(backend, 'main.py')
if os.path.exists(main_path):
    with open(main_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Find CORS origins
    for m in re.finditer(r'allow_origins\s*=\s*(\[[^\]]+\])', content):
        print(f'  CORS origins: {m.group(1)}')
    for m in re.finditer(r'allow_credentials\s*=\s*(\w+)', content):
        print(f'  CORS credentials: {m.group(1)}')
else:
    print('  main.py NOT FOUND!')

# ========== 5. Frontend API Config ==========
print(f'\n{SEP}')
print('5. FRONTEND - API Configuration')
print(SEP)
# Check api.ts or similar
for candidate in [
    os.path.join(frontend, 'src', 'services', 'api.ts'),
    os.path.join(frontend, 'src', 'api', 'api.ts'),
    os.path.join(frontend, 'src', 'utils', 'request.ts'),
]:
    if os.path.exists(candidate):
        with open(candidate, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                s = line.strip()
                if 'VITE_API_BASE_URL' in s or 'baseURL' in s or 'localhost:8000' in s or '127.0.0.1:8000' in s:
                    print(f'  {os.path.relpath(candidate, frontend)} L{i}: {s}')

# Check .env files
for env_name in ['.env', '.env.development', '.env.local']:
    env_path = os.path.join(frontend, env_name)
    if os.path.exists(env_path):
        print(f'  {env_name}:')
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith('#'):
                    print(f'    {s}')

# ========== 6. Frontend - Key Pages Check ==========
print(f'\n{SEP}')
print('6. FRONTEND - Page/Component Inventory')
print(SEP)
pages_dir = os.path.join(frontend, 'src', 'pages')
if os.path.exists(pages_dir):
    for root, dirs, files in os.walk(pages_dir):
        level = root.replace(pages_dir, '').count(os.sep)
        indent = '  ' * (level + 1)
        dirname = os.path.basename(root)
        py_files = [f for f in files if f.endswith(('.tsx','.ts','.jsx','.js'))]
        if py_files:
            print(f'{indent}{dirname}/: {len(py_files)} files')

# ========== 7. Database Connection (check docker-compose) ==========
print(f'\n{SEP}')
print('7. DOCKER - docker-compose.yml Database Config')
print(SEP)
compose_path = os.path.join(r'D:\test', 'docker-compose.yml')
if os.path.exists(compose_path):
    with open(compose_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Extract key service configs
    for service in ['postgres', 'redis', 'opensearch', 'backend']:
        pattern = rf'{service}:(.*?)(?=\n  \w+:|\Z)'
        m = re.search(pattern, content, re.DOTALL)
        if m:
            block = m.group(0)
            # Extract ports
            ports = re.findall(r'- ["\']?(\d+:\d+)["\']?', block)
            if ports:
                print(f'  {service} ports: {ports}')
            # Extract env_file
            env_files = re.findall(r'env_file:\s*(.+)', block)
            if env_files:
                print(f'  {service} env_file: {env_files}')
            # Extract depends_on
            deps = re.findall(r'depends_on:\s*\[(.+?)\]', block)
            if deps:
                print(f'  {service} depends_on: {deps}')
            else:
                deps2 = re.findall(r'- (\w+)', block[re.search(r'depends_on:', block).start():] if 'depends_on:' in block else '')
                if deps2:
                    print(f'  {service} depends_on: {deps2[:5]}')
else:
    print('  docker-compose.yml NOT FOUND!')

# ========== 8. Database init SQL ==========
print(f'\n{SEP}')
print('8. DATABASE - init_db.sql Table Check')
print(SEP)
sql_path = os.path.join(backend, 'init_db.sql')
if os.path.exists(sql_path):
    with open(sql_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    tables = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', content, re.IGNORECASE)
    print(f'  Tables defined: {tables}')
else:
    print('  init_db.sql NOT FOUND')

# ========== 9. Backend DB connection string ==========
print(f'\n{SEP}')
print('9. BACKEND - Database Module')
print(SEP)
db_path = os.path.join(backend, 'app', 'db.py')
if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if any(kw in s for kw in ['DATABASE_URL','postgres','asyncpg','create_pool','get_db']):
                print(f'  L{i}: {s}')
else:
    print('  app/db.py NOT FOUND!')

# ========== 10. Frontend store/auth ==========
print(f'\n{SEP}')
print('10. FRONTEND - Auth & Store')
print(SEP)
store_path = os.path.join(frontend, 'src', 'store', 'index.ts')
if os.path.exists(store_path):
    with open(store_path, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if any(kw in s for kw in ['userId','token','login','auth','localStorage']):
                print(f'  store/index.ts L{i}: {s}')

print(f'\n{SEP}')
print('CHECK COMPLETE')
print(SEP)