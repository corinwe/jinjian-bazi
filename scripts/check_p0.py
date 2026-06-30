#!/usr/bin/env python3
"""检查金鉴真人TASK_BOARD中的P0任务状态"""
import re
from datetime import datetime

TASK_BOARD = "/root/jinjian/docs/TASK_BOARD.md"

try:
    with open(TASK_BOARD) as f:
        content = f.read()
except FileNotFoundError:
    print("TASK_BOARD.md not found")
    exit(1)

# Find P0 tasks
p0_section = re.search(r'## P0.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
if p0_section:
    pending = re.findall(r'\| (P0-\d+) \|.*\| 🔴 pending', p0_section.group(1))
    in_progress = re.findall(r'\| (P0-\d+) \|.*\| 🟡 in_progress', p0_section.group(1))
    
    if pending or in_progress:
        print(f"[{datetime.now().strftime('%m-%d %H:%M')}] P0未完成:")
        for t in pending:
            print(f"  🔴 {t} — PENDING")
        for t in in_progress:
            print(f"  🟡 {t} — IN_PROGRESS")
    else:
        print("[OK] 所有P0任务已完成")
else:
    print("[INFO] 无P0任务")
