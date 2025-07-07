import sys
import os

# 获取当前文件的父目录（假设当前在 project/subdir/path_setup.py）
TODO = os.path.dirname(os.path.abspath(__file__))

# 上一级目录，即项目根目录
ROOT_DIR = os.path.dirname(TODO)

# 添加到 sys.path
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if __name__ == "__main__":
    print("工具目录：", TODO)
    print("当前根目录：", ROOT_DIR)
    print("sys.path：", sys.path)