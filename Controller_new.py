# Controller.py

from Hexapod import GaitPrg
from config.hexapod_config import HexapodConfig
from ActionGroups.load_action_groups import action_groups  # 预加载的动作组
from utils.thread_init import cmd_queue
from utils.math import Position3, Velocity
from queue import Empty
import time, json

# 初始化配置与步态控制器\config   = HexapodConfig()
config   = HexapodConfig()
gait_prg = GaitPrg(config)    # 注入配置


def handle_set_entry(target_path: str, value):
    """
    按路径设置属性，支持 Position3/Velocity 解包。
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
    自动步态生成器：每 yield 一步。
    """
    while True:
        for _ in range(config.N_POINTS):
            start = time.time()
            if gait_prg.velocity.omega >= 0:
                config.LegControl_round = (config.LegControl_round + 1) % config.N_POINTS
            else:
                config.LegControl_round = (config.LegControl_round - 1) % config.N_POINTS
            gait_prg.CEN_and_pace_cal()
            gait_prg.gait_programing(
                config.LegControl_round,
                config.N_POINTS,
                config.MIN_Z_PACE
            )
            round_time = gait_prg.get_pace_time() / config.N_POINTS
            gait_prg.move(round_time, config.LegControl_round)
            elapsed = time.time() - start
            time.sleep((round_time/1000 - elapsed) if elapsed < (round_time/1000) else 0.001)
            yield


def run_manual_gait_cycle(steps):
    """
    手动步态生成器：每 yield 一步，调用 set_all_legs。
    """
    for step in steps:
        gait_prg.set_all_legs(step)
        yield


class ModeHandler:
    """
    管理当前模式与对应生成器，封装切换与清理逻辑。
    """
    def __init__(self):
        self.current_mode = None
        self.current_gen  = None

    def switch(self, cmd: dict):
        mode = cmd.get('mode')
        if mode != self.current_mode:
            # 关闭旧生成器
            if self.current_gen:
                try:
                    self.current_gen.close()
                except:
                    pass
            # 创建新生成器
            if mode == 'auto':
                self.current_gen = run_auto_gait_cycle()
            elif mode == 'manual':
                group = cmd.get('action_group')
                steps = action_groups.get(group, [])
                self.current_gen = run_manual_gait_cycle(steps)
            else:
                self.current_gen = None
            self.current_mode = mode

    def step(self):
        """
        执行当前模式的一步，如果无新命令则继续，否则由外层决定打断。
        """
        if self.current_gen:
            try:
                next(self.current_gen)
            except StopIteration:
                self.current_gen = None


def main():
    """
    主循环：取命令、批量写入属性、模式切换及步态执行。
    """
    time.sleep(0.1)
    handler = ModeHandler()

    while True:
        cmd = cmd_queue.get()  # 阻塞取命令

        # 1）批量属性写入
        for entry in cmd.get('set', ()): 
            handle_set_entry(*entry)

        # 2）模式切换处理
        handler.switch(cmd)

        # 3）步态执行与中断检测
        try:
            # 非阻塞检查新命令以打断当前步态
            next_cmd = cmd_queue.get_nowait()
        except Empty:
            handler.step()
        else:
            # 如果有新命令，放回并跳过当前 step
            cmd_queue.put(next_cmd)

        cmd_queue.task_done()

if __name__ == '__main__':
    main()
