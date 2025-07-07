# Controller.py

from Hexapod import GaitPrg
from config.hexapod_config import HexapodConfig
from utils.thread_init import cmd_queue
from utils.math import Position3, Velocity
from ActionGroups.load_action_groups import action_groups
from typing import List
from queue import Empty
import time, json

# 初始化配置与步态控制器
config   = HexapodConfig()
gait_prg = GaitPrg(config)    # 注入配置

def handle_mode_and_actions(cmd: dict) -> str:
    """
    处理基础模式切换（'auto' 或 'manual'）及可能的 action_group。
    手动模式会将指定组拆成多条 'manual_step' 入队。
    """
    mode = cmd.get('mode')
    group = cmd.get('action_group')
    if mode == 'manual' and group:
        steps = action_groups.get(group, [])
        # 将每一步封装成单独命令入队
        for step in steps:
            cmd_queue.put({
                'mode':      'manual_step',
                'set':       (('gait_prg.default_angles', [p.data.tolist() for p in step]),)
            })
        return 'manual_step'
    return mode

def handle_set_entry(target_path: str, value):
    """
    按路径设置属性，如 'gait_prg.body_pos'。
    支持 Position3/Velocity 传 tuple 解包赋值。
    """
    parts = target_path.split('.')
    obj   = globals()[parts[0]]
    for attr in parts[1:-1]:
        obj = getattr(obj, attr)
    final   = parts[-1]
    existing = getattr(obj, final)

    if isinstance(existing, Position3) and isinstance(value, (list, tuple)):
        existing.data[:] = value
    elif isinstance(existing, Velocity) and isinstance(value, (list, tuple)):
        existing.Vx, existing.Vy, existing.omega = value
    else:
        setattr(obj, final, value)

def run_auto_gait_cycle():
    """
    自动步态生成器。
    每 yield 一次，完成 N_POINTS 中的一步，可被打断。
    """
    while True:
        for _ in range(config.N_POINTS):
            start = time.time()

            # 更新步态轮次索引
            if gait_prg.velocity.omega >= 0:
                config.LegControl_round = (config.LegControl_round + 1) % config.N_POINTS
            else:
                config.LegControl_round = (config.LegControl_round - 1) % config.N_POINTS

            # 计算节奏与轨迹
            gait_prg.CEN_and_pace_cal()
            gait_prg.gait_programing(
                config.LegControl_round,
                config.N_POINTS,
                config.MIN_Z_PACE
            )

            # 执行移动
            round_time = gait_prg.get_pace_time() / config.N_POINTS
            gait_prg.move(round_time, config.LegControl_round)

            # 保证周期精度
            elapsed = time.time() - start
            to_sleep = (round_time/1000 - elapsed) if elapsed < (round_time/1000) else 0.001
            time.sleep(to_sleep)

            yield  # 一步完成，返回给主循环检查中断

def main():
    time.sleep(0.1)
    current_mode = None
    auto_gen     = None

    while True:
        # 阻塞等新命令
        cmd = cmd_queue.get()

        # 1. 模式 & 动作组预处理
        mode = handle_mode_and_actions(cmd)

        # 2. 批量属性赋值
        for entry in cmd.get('set', ()):
            handle_set_entry(*entry)

        # 3. 模式切换处理
        if mode != current_mode:
            # 如果从 auto 切出，先关闭旧生成器
            if current_mode == 'auto' and auto_gen:
                auto_gen.close()
                auto_gen = None
            # 切入 auto 时，新建一个生成器
            if mode == 'auto':
                auto_gen = run_auto_gait_cycle()
            current_mode = mode

        # 4. 根据当前模式执行
        if mode == 'auto':
            try:
                # 非阻塞检查新命令来打断
                next_cmd = cmd_queue.get_nowait()
            except Empty:
                # 正常跑下一步
                next(auto_gen)
            else:
                # 有新命令，放回队列并中断 auto
                cmd_queue.put(next_cmd)

        elif mode in ('manual_step',):
            # 手动单步：default_angles 已被更新，直接跑一轮完整 auto 步态的单步
            next(auto_gen or run_auto_gait_cycle())

        cmd_queue.task_done()

if __name__ == '__main__':
    main()
