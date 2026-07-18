import os, re

backend = r'D:\test\backend'
frontend = r'D:\test\frontend'

SEP = '=' * 60

# ===== 1. Interview pages structure =====
print(SEP)
print('1. INTERVIEW - Current Structure')
print(SEP)
# Check router
router_path = os.path.join(frontend, 'src', 'router', 'index.tsx')
if os.path.exists(router_path):
    with open(router_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Find interview routes
    for i, line in enumerate(content.split('\n'), 1):
        if 'interview' in line.lower() or 'Interview' in line or 'exam' in line.lower() or 'Exam' in line:
            print(f'  router L{i}: {line.strip()[:100]}')

# Check MainLayout menu
layout_path = os.path.join(frontend, 'src', 'components', 'layout', 'MainLayout.tsx')
if os.path.exists(layout_path):
    with open(layout_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    for i, line in enumerate(content.split('\n'), 1):
        if any(kw in line for kw in ['interview', 'Interview', 'exam', 'Exam', '面试', 'mock', 'Mock']):
            print(f'  MainLayout L{i}: {line.strip()[:100]}')

# List Interview directory
interview_dir = os.path.join(frontend, 'src', 'pages', 'Interview')
if os.path.exists(interview_dir):
    for f in os.listdir(interview_dir):
        print(f'  Interview/{f}')

# ===== 2. Login/Auth logic =====
print(f'\n{SEP}')
print('2. LOGIN/AUTH - Current Logic')
print(SEP)

# Backend auth
auth_path = os.path.join(backend, 'app', 'api', 'v1', 'auth.py')
if os.path.exists(auth_path):
    with open(auth_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  auth.py ({len(lines)} lines):')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if any(kw in s for kw in ['def ', 'class ', 'login', 'register', 'token', 'session', 'device', 'jwt', 'JWT', 'verify', 'hash', 'password']):
            print(f'    L{i}: {s[:100]}')

# Frontend login
login_path = os.path.join(frontend, 'src', 'pages', 'Login', 'index.tsx')
if os.path.exists(login_path):
    with open(login_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  Login/index.tsx ({len(lines)} lines):')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if any(kw in s for kw in ['login', 'Login', 'token', 'Token', 'store', 'dispatch', 'localStorage', 'sessionStorage', 'device']):
            print(f'    L{i}: {s[:100]}')

# Frontend auth service
auth_service = os.path.join(frontend, 'src', 'services', 'auth.ts')
if os.path.exists(auth_service):
    with open(auth_service, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  services/auth.ts ({len(lines)} lines):')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s and not s.startswith('//') and not s.startswith('import'):
            print(f'    L{i}: {s[:100]}')

# ===== 3. Admin pages =====
print(f'\n{SEP}')
print('3. ADMIN - Current Pages')
print(SEP)
admin_dir = os.path.join(frontend, 'src', 'pages', 'Admin')
if os.path.exists(admin_dir):
    for f in os.listdir(admin_dir):
        fpath = os.path.join(admin_dir, f)
        if os.path.isfile(fpath):
            with open(fpath, 'r', encoding='utf-8-sig') as fh:
                lines = fh.readlines()
            print(f'  Admin/{f} ({len(lines)} lines)')
        else:
            print(f'  Admin/{f}/ (dir)')

# ===== 4. User Profile =====
print(f'\n{SEP}')
print('4. USER PROFILE - Current Implementation')
print(SEP)
profile_path = os.path.join(frontend, 'src', 'pages', 'User', 'Profile.tsx')
if os.path.exists(profile_path):
    with open(profile_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  Profile.tsx ({len(lines)} lines):')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if any(kw in s for kw in ['useState', 'useEffect', 'return', 'interface', 'type ', 'async', 'await', 'Card', 'Statistic', 'Descriptions']):
            print(f'    L{i}: {s[:100]}')

# ===== 5. Backend user service =====
print(f'\n{SEP}')
print('5. BACKEND - User Service')
print(SEP)
user_svc = os.path.join(backend, 'app', 'services', 'user_service.py')
if os.path.exists(user_svc):
    with open(user_svc, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  user_service.py ({len(lines)} lines):')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if any(kw in s for kw in ['def ', 'class ', 'async ']):
            print(f'    L{i}: {s[:100]}')

# ===== 6. DB schema for users =====
print(f'\n{SEP}')
print('6. DATABASE - Users Table Schema')
print(SEP)
sql_path = os.path.join(backend, 'init_db.sql')
if os.path.exists(sql_path):
    with open(sql_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Find users table definition
    in_users = False
    for line in content.split('\n'):
        if re.search(r'CREATE\s+TABLE.*users', line, re.IGNORECASE):
            in_users = True
        if in_users:
            print(f'  {line}')
            if ';' in line and not line.strip().startswith('--'):
                in_users = False