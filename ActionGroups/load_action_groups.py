# action_groups.py

import json
import os
from utils.math import Position3

# 列表中填写要加载的 JSON 文件路径
group_list = [
    "111.json",  # 示例文件名，可根据实际情况增删
    # "222.json",
]

# 预加载后的动作组字典，key 为文件名，value 为每步的腿部 Position3 列表
action_groups = {}

for file_name in group_list:
    if not os.path.exists(file_name):
        print(f"[Warning] Action group file not found: {file_name}")
        continue
    with open(file_name, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    steps = []
    for entry in raw_data:
        # 提取每步的 'leg' 坐标并转换为 Position3 实例列表
        leg_coords = entry.get('leg', [])
        leg_positions = [Position3(*coords) for coords in leg_coords]
        steps.append(leg_positions)

    action_groups[file_name] = steps

# 使用示例：
# from action_groups import action_groups
# my_steps = action_groups.get("111.json", [])
# for step in my_steps:
#     # step 是一个包含 6 个 Position3 实例的列表
#     pass
