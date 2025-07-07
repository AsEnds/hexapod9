# load_action_groups.py

import sys
import os
import json
from utils.math import Position3
from utils.logger_tools import logger

# 获取本脚本所在目录：ActionGroups/
CFG_DIR = os.path.dirname(os.path.abspath(__file__))

group_list = [
    "A02.json",
]

action_groups = {}
for file_name in group_list:
    file_path = os.path.join(CFG_DIR, file_name)
    if not os.path.exists(file_path):
        logger.warning(f"Action group file not found: {file_path}")
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    steps = []
    for entry in raw_data:
        coords = entry.get('leg', [])
        leg_positions = [Position3(*c) for c in coords]
        steps.append(leg_positions)

    action_groups[file_name] = steps
