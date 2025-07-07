import os
import sys

def import_board_module():
    """
    自动切换导入 Board 或 utils.test_board，并返回 (Board模块, 是否为debug环境)
    """
    # 1. 将项目根目录（hexapod9）加入搜索路径
    this_dir = os.path.dirname(os.path.abspath(__file__))       # .../hexapod9/utils
    project_root = os.path.dirname(this_dir)                     # .../hexapod9
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 2. 尝试导入真实硬件驱动 Board
    try:
        import Board  # 如果你已在项目根或site-packages下安装了 Board.py
        is_debug_mode = False
        return Board, is_debug_mode
    except ImportError:
        # 3. 失败时导入测试替身（utils/test_board.py）
        from . import test_board
        Board = test_board
        is_debug_mode = True
        return Board, is_debug_mode


if __name__ == "__main__":
    Board, is_debug_mode = import_board_module()
    print("使用模块：", Board, "调试模式：", is_debug_mode)