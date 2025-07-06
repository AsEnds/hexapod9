from Hexapod import GaitPrg
from config.HexapodConfig import HexapodConfig
from utils.thread_init import cmd_queue, controller_lock
from utils.math import Position3, Velocity
from ActionGroups.load_action_groups import action_groups
from typing import List
import time, json

config = HexapodConfig()
gait_prg = GaitPrg(config)    # 注入配置

def handle_mode_and_actions(cmd: dict) -> str:
    """处理 mode 与 action_group"""
    mode = cmd.get('mode')
    return mode


def handle_set_entry(target_path: str, value):
    """
    根据路径设置属性，如 'gait_prg.body_pos'。
    支持 Position3/Velocity 的自动处理。
    """
    parts = target_path.split('.')
    # 从 globals 中取出 gait_prg 对象
    obj = globals().get(parts[0])
    # 遍历中间属性
    for attr in parts[1:-1]:
        obj = getattr(obj, attr)
    final = parts[-1]
    existing = getattr(obj, final)

    # 如果是 Position3 并传入 tuple，则更新 data
    if isinstance(existing, Position3) and isinstance(value, (list, tuple)):
        existing.data[:] = value
    # 如果是 Velocity 并传入 tuple，则拆解赋值
    elif isinstance(existing, Velocity) and isinstance(value, (list, tuple)):
        existing.Vx, existing.Vy, existing.omega = value
    else:
        setattr(obj, final, value)

def run_auto_gait_cycle():
    """
    执行一次自动步态完整周期：
    - 更新 LegControl_round
    - 计算 CEN 与步态程序
    - 调用 move 发送脉冲
    - 保证周期时长
    """
    for _ in range(config.N_POINTS):
        start = time.time()

        # 按 omega 方向更新回合索引
        if gait_prg.velocity.omega >= 0:
            config.LegControl_round = (config.LegControl_round + 1) % config.N_POINTS
        else:
            config.LegControl_round = (config.LegControl_round - 1) % config.N_POINTS

        # 步态控制: 计算节奏与轨迹
        gait_prg.CEN_and_pace_cal()
        gait_prg.gait_programing(
            config.LegControl_round,
            config.N_POINTS,
            config.MIN_Z_PACE
        )

        # 执行移动
        round_time = gait_prg.get_pace_time() / config.N_POINTS
        gait_prg.move(round_time, config.LegControl_round)

        # 时间补偿，保证精确周期
        elapsed = time.time() - start
        delay = (round_time / 1000 - elapsed) if elapsed < (round_time / 1000) else 0.001
        time.sleep(delay)

def run_manual_gait_cycle(actions : List):
    for action in actions:
        gait_prg.set_all_legs(action)
        yield

def main():
    time.sleep(0.1)
    while True:
        cmd = cmd_queue.get()                # 阻塞等命令
        mode = handle_mode_and_actions(cmd)  # 切换模式 & 动作组


        if mode == 'auto':
            for entry in cmd.get('set', ()):
                handle_set_entry(*entry)         # 批量属性赋值
            run_auto_gait_cycle()            # 自动步态

        elif mode == 'manual':
            run_manual_gait_cycle(cmd.get('set'))

        cmd_queue.task_done()

if __name__ == '__main__':
    main()
