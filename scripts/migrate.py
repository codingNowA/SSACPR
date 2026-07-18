#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 跨平台版本
支持 Linux, macOS, Windows
"""
import subprocess
import sys
import os

# 设置输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def run_command(cmd, shell=False):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_container_running():
    """检查PostgreSQL容器是否运行"""
    code, stdout, _ = run_command(['docker', 'ps'])
    return 'career-postgres' in stdout

def main():
    print("===== Database Migration =====")
    print()

    # 检查容器是否运行
    print("Checking PostgreSQL container...")
    if not check_container_running():
        print("ERROR: PostgreSQL container is not running")
        print("Please run: make up or docker-compose up -d")
        sys.exit(1)

    print("[OK] PostgreSQL container is running")
    print()

    # 复制迁移脚本到容器
    print("Copying migration scripts to container...")
    code, _, err = run_command([
        'docker', 'cp',
        'scripts/migrations',
        'career-postgres:/tmp/migrations'
    ])

    if code != 0:
        print(f"ERROR: Failed to copy migration scripts: {err}")
        sys.exit(1)

    print("[OK] Migration scripts copied")
    print()

    # 执行迁移
    migrations = [
        ('001', 'Add current_version_id field'),
        ('002', 'Fix user password hashes'),
        ('003', 'Create test user'),
    ]

    for num, desc in migrations:
        print(f"Running migration {num}: {desc}...")

        code, stdout, stderr = run_command([
            'docker', 'exec', 'career-postgres',
            'bash', '-c',
            f'psql -U career_user -d career_planning -f /tmp/migrations/{num}_*.sql'
        ])

        # 显示NOTICE信息
        if 'NOTICE' in stdout:
            for line in stdout.split('\n'):
                if 'NOTICE' in line:
                    print(f"  {line.strip()}")

        if code != 0 and 'ERROR' in stderr:
            print(f"  [WARN] {stderr}")
        else:
            print(f"  [OK] Migration {num} completed")

        print()

    # 清理临时文件
    print("Cleaning up temporary files...")
    run_command([
        'docker', 'exec', 'career-postgres',
        'rm', '-rf', '/tmp/migrations'
    ])

    print("[OK] Temporary files cleaned")
    print()
    print("===== Migration Completed =====")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nMigration interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
