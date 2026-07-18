import os, re

backend = r'D:\test\backend'
frontend = r'D:\test\frontend'

def find_files(base, ext, pattern):
    results = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != '__pycache__' and d != 'node_modules' and d != '.git']
        for fn in files:
            if fn.endswith(ext):
                fp = os.path.join(root, fn)
                try:
                    with open(fp, 'r', encoding='utf-8-sig') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f'{os.path.relpath(fp, base)} L{i}: {line.strip()[:80]}')
                                break
                except:
                    pass
    return results

def grep_files(base, ext, pattern, max_lines=5):
    results = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != '__pycache__' and d != 'node_modules' and d != '.git']
        for fn in files:
            if fn.endswith(ext):
                fp = os.path.join(root, fn)
                try:
                    with open(fp, 'r', encoding='utf-8-sig') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f'{os.path.relpath(fp, base)} L{i}: {line.strip()[:100]}')
                                if len(results) >= max_lines:
                                    return results
                except:
                    pass
    return results

SEP = '=' * 60

# ===== Feature 1: Word简历修改 + 历史版本再次上传 =====
print(SEP)
print('Feature 1: Word简历修改界面 + 历史版本再次上传')
print(SEP)

# Check frontend for resume re-upload / version page
print('  Frontend - resume re-upload:')
hits = grep_files(frontend, '.tsx', r're.?upload|ReUpload|再次上传|重新上传', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Frontend - Versions page (history):')
hits = grep_files(frontend, '.tsx', r'Version|History|历史版本', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Backend - resume version endpoints:')
hits = grep_files(backend, '.py', r'version|resume_version', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

# ===== Feature 2: 岗位难度 + 按难度排列 =====
print(f'\n{SEP}')
print('Feature 2: 岗位难度显示 + 按难度排列')
print(SEP)

print('  Backend - difficulty:')
hits = grep_files(backend, '.py', r'difficulty|难度', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Frontend - difficulty sort/display:')
hits = grep_files(frontend, '.tsx', r'difficulty|难度', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

# ===== Feature 3: 模拟面试功能 =====
print(f'\n{SEP}')
print('Feature 3: 模拟面试功能 (10题考试, 评分, 总结建议)')
print(SEP)

print('  Backend - interview/mock:')
hits = grep_files(backend, '.py', r'interview|mock_interview|模拟面试', 15)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Frontend - interview page:')
hits = grep_files(frontend, '.tsx', r'interview|mock|面试|Exam', 15)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

# ===== Feature 4: 管理员上传题库/岗位库 =====
print(f'\n{SEP}')
print('Feature 4: 管理员上传题库/岗位库 (Excel批量导入)')
print(SEP)

print('  Backend - batch import:')
hits = grep_files(backend, '.py', r'batch_import|import_from_excel', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Frontend - admin upload:')
hits = grep_files(frontend, '.tsx', r'batch.?import|import.?excel|上传题库|上传岗位|AdminUpload', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

# ===== Feature 5: 用户信息界面 =====
print(f'\n{SEP}')
print('Feature 5: 用户信息界面 (ID, 名字, 使用次数, 保存版本)')
print(SEP)

print('  Backend - user profile/stats:')
hits = grep_files(backend, '.py', r'user_profile|user_info|usage_count|使用次数', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print('  Frontend - user profile page:')
hits = grep_files(frontend, '.tsx', r'UserProfile|UserInfo|用户信息|Profile', 10)
if hits:
    for h in hits: print(f'    {h}')
else:
    print('    NOT FOUND')

print(f'\n{SEP}')
print('CHECK COMPLETE')