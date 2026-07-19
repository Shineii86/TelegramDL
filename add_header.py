#!/usr/bin/env python3
"""
TelegramDL - Add Header to Python Files

Usage:
    python3 add_header.py              # Add header to all Python files
    python3 add_header.py --dry-run    # Preview without changes
    python3 add_header.py --file FILE  # Add header to specific file

Author: Shinei Nouzen (Shineii86)
"""

import os
import sys
import argparse

HEADER = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramDL - Advanced Telegram Downloader Bot

Copyright (c) 2024-2026 Shinei Nouzen (Shineii86)
Licensed under the MIT License

Author:    Shinei Nouzen
GitHub:    https://github.com/Shineii86/TelegramDL
Telegram:  https://t.me/Shineii86
Email:     ikx7a@hotmail.com

Description:
    Advanced Telegram Restricted Content Downloader with Premium System,
    yt-dlp Integration, File Splitting, Custom Bots & More.

Framework:  Kurigram (Pyrogram Fork)

Disclaimer:
    This bot is for educational purposes only.
    Use responsibly and respect Telegram's Terms of Service.
"""

'''

SKIP_FILES = ['__init__.py', 'header.py', 'add_header.py', 'gen_session.py']
SKIP_DIRS = ['.git', '__pycache__', 'venv', '.venv', 'node_modules']


def has_header(content: str) -> bool:
    return 'TelegramDL - Advanced Telegram Downloader Bot' in content


def add_header_to_file(filepath: str, dry_run: bool = False) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if has_header(content):
            return False

        if content.startswith('#!/'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:]).lstrip()

        new_content = HEADER + content

        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return True

    except Exception as e:
        print(f'  ❌ Error: {e}')
        return False


def find_python_files(directory: str) -> list:
    files = []
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith('.py') and filename not in SKIP_FILES:
                filepath = os.path.join(root, filename)
                files.append(filepath)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description='Add header to Python files')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
    parser.add_argument('--file', type=str, help='Add header to specific file')
    parser.add_argument('--dir', type=str, default='.', help='Directory to process')
    args = parser.parse_args()

    print('=' * 50)
    print('  TelegramDL - Header Manager')
    print('=' * 50)
    print()

    if args.dry_run:
        print('🔍 DRY RUN - No changes will be made')
        print()

    if args.file:
        if not os.path.exists(args.file):
            print(f'❌ File not found: {args.file}')
            sys.exit(1)

        print(f'📄 Processing: {args.file}')
        if add_header_to_file(args.file, args.dry_run):
            print('  ✅ Header added')
        else:
            print('  ⏭️  Header already exists')
    else:
        files = find_python_files(args.dir)
        print(f'📁 Found {len(files)} Python files')
        print()

        added = 0
        skipped = 0

        for filepath in files:
            print(f'📄 {filepath}')
            if add_header_to_file(filepath, args.dry_run):
                print('  ✅ Header added')
                added += 1
            else:
                print('  ⏭️  Header already exists')
                skipped += 1

        print()
        print('=' * 50)
        print(f'  Results: {added} added, {skipped} skipped')
        print('=' * 50)

    print()
    print('Done! 🎉')


if __name__ == '__main__':
    main()
