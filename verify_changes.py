import os

frontend = r'D:\test\frontend'
backend = r'D:\test\backend'
SEP = '=' * 60

# Check 1: Interview QuestionBank exists
print(SEP)
print('1. Interview QuestionBank page')
qb = os.path.join(frontend, 'src', 'pages', 'Interview', 'QuestionBank.tsx')
print(f'  Exists: {os.path.exists(qb)}')
if os.path.exists(qb):
    with open(qb, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f'  Lines: {len(lines)}')

# Check 2: Router has questions route
print(f'\n{SEP}')
print('2. Router - interview/questions route')
router = os.path.join(frontend, 'src', 'router', 'index.tsx')
with open(router, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'QuestionBank' in content:
    print('  QuestionBank import: OK')
else:
    print('  QuestionBank import: MISSING!')
if "path: 'questions'" in content:
    print('  questions route: OK')
else:
    print('  questions route: MISSING!')

# Check 3: MainLayout interview submenu
print(f'\n{SEP}')
print('3. MainLayout - interview submenu')
layout = os.path.join(frontend, 'src', 'components', 'layout', 'MainLayout.tsx')
with open(layout, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'BookOutlined' in content:
    print('  BookOutlined import: OK')
else:
    print('  BookOutlined import: MISSING!')
if 'interview/questions' in content:
    print('  questions menu item: OK')
else:
    print('  questions menu item: MISSING!')

# Check 4: JobAdmin upload
print(f'\n{SEP}')
print('4. JobAdmin - batch import upload')
ja = os.path.join(frontend, 'src', 'pages', 'Admin', 'JobAdmin.tsx')
with open(ja, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'UploadOutlined' in content:
    print('  UploadOutlined import: OK')
else:
    print('  UploadOutlined import: MISSING!')
if 'handleBatchImportJobs' in content:
    print('  handler: OK')
else:
    print('  handler: MISSING!')
if 'batch-import' in content:
    print('  API call: OK')
else:
    print('  API call: MISSING!')

# Check 5: QuestionAdmin upload
print(f'\n{SEP}')
print('5. QuestionAdmin - batch import upload')
qa = os.path.join(frontend, 'src', 'pages', 'Admin', 'QuestionAdmin.tsx')
with open(qa, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'UploadOutlined' in content:
    print('  UploadOutlined import: OK')
else:
    print('  UploadOutlined import: MISSING!')
if 'handleBatchImportQuestions' in content:
    print('  handler: OK')
else:
    print('  handler: MISSING!')
if 'batch-import' in content:
    print('  API call: OK')
else:
    print('  API call: MISSING!')

# Check 6: Backend auth stats endpoint
print(f'\n{SEP}')
print('6. Backend - auth stats endpoint')
auth = os.path.join(backend, 'app', 'api', 'v1', 'auth.py')
with open(auth, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'UserStatsResponse' in content:
    print('  UserStatsResponse model: OK')
else:
    print('  UserStatsResponse model: MISSING!')
if '/stats' in content:
    print('  stats endpoint: OK')
else:
    print('  stats endpoint: MISSING!')
if 'resume_count' in content:
    print('  resume_count query: OK')
else:
    print('  resume_count query: MISSING!')

# Check 7: Profile uses auth/stats
print(f'\n{SEP}')
print('7. Profile.tsx - uses auth/stats API')
prof = os.path.join(frontend, 'src', 'pages', 'User', 'Profile.tsx')
with open(prof, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'auth/stats' in content:
    print('  auth/stats API: OK')
else:
    print('  auth/stats API: MISSING!')
if 'useAppStore' in content:
    print('  useAppStore import: OK')
else:
    print('  useAppStore import: MISSING!')
if 'user?.userId' in content:
    print('  user?.userId access: OK')
else:
    print('  user?.userId access: check needed')

# Check 8: BOM check on modified files
print(f'\n{SEP}')
print('8. BOM check on modified files')
bom_files = []
for fp in [auth, prof, qa, ja, layout, router, qb]:
    with open(fp, 'rb') as f:
        if f.read(3) == b'\xef\xbb\xbf':
            bom_files.append(os.path.basename(fp))
if bom_files:
    print(f'  BOM found in: {bom_files}')
else:
    print('  No BOM in any modified file')

print(f'\n{SEP}')
print('ALL CHECKS COMPLETE')
