from queue import Empty
import time
from Hexapod import GaitPrg
from config.hexapod_config import HexapodConfig
from ActionGroups.load_action_groups import action_groups
from utils.thread_init import cmd_queue
from utils.math import Position3, Velocity
from utils.logger_tools import logger

class Mode:
    """所有模式的基类，需实现 __next__。"""
    def __init__(self, controller):
        self.controller = controller

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError

    def close(self):
        """需要清理资源时可重写"""
        pass


class AutoMode(Mode):
    def __next__(self):
        cfg = self.controller.config
        gp = self.controller.gait_prg
        start = time.time()

        # 更新索引
        if gp.velocity.omega >= 0:
            cfg.LegControl_round = (cfg.LegControl_round + 1) % cfg.N_POINTS
        else:
            cfg.LegControl_round = (cfg.LegControl_round - 1) % cfg.N_POINTS
        logger.info(f"\nat AutoMode, cfg.LegControl_round= {cfg.LegControl_round}\n\n")
        # 计算步态与移动
        gp.CEN_and_pace_cal()
        gp.gait_programing(cfg.LegControl_round, cfg.N_POINTS, cfg.MIN_Z_PACE)
        round_time = gp.get_pace_time() / cfg.N_POINTS
        gp.move(round_time, cfg.LegControl_round)

        elapsed = time.time() - start
        time.sleep(max(round_time/1000 - elapsed, 0.001))


class ManualMode(Mode):
    def __init__(self, controller, group):
        super().__init__(controller)
        self.steps = action_groups.get(group, [])
        self.idx = 0

    def __next__(self):
        if self.idx >= len(self.steps):
            raise StopIteration
        self.controller.gait_prg.set_all_legs(self.steps[self.idx])
        self.idx += 1


class VisualMode(Mode):
    """示例视觉模式，实际视觉逻辑需自行实现"""
    def __init__(self, controller, camera):
        super().__init__(controller)
        self.camera = camera

    def close(self):
        self.camera.release()

    def __next__(self):
        frame = self.camera.read()
        # TODO: 根据视觉结果更新速度或步态
        # 这里只是简单调用自动步态，实际应根据 frame 计算
        AutoMode(self.controller).__next__()


class ModeHandler:
    def __init__(self, controller):
        self.controller = controller
        self.current_mode = None
        self.mode_name = None

    def switch(self, cmd):
        mode = cmd.get("mode")
        # 仅在模式实际变化时切换
        if mode != self.mode_name:
            # 关闭旧模式资源
            if isinstance(self.current_mode, VisualMode):
                self.current_mode.close()
            # 创建并设置新模式
            if mode == "auto":
                self.current_mode = AutoMode(self.controller)
            elif mode == "manual":
                group = cmd.get("action_group")
                self.current_mode = ManualMode(self.controller, group)
            elif mode == "visual":
                camera = cmd.get("camera")
                self.current_mode = VisualMode(self.controller, camera)
            else:
                self.current_mode = None
            self.mode_name = mode

    def step(self):
        if self.current_mode is not None:
            try:
                next(self.current_mode)
            except StopIteration:
                self.current_mode = None
                self.mode_name = None


class Controller:
    def __init__(self):
        self.config = HexapodConfig()
        self.gait_prg = GaitPrg(self.config)
        self.handler = ModeHandler(self)

    def handle_set_entry(self, target_path, value):
        """
        按路径设置属性，支持 Position3/Velocity 解包及普通属性赋值。
        """
        obj = self
        parts = target_path.split(".")
        # 逐级获取对象
        for attr in parts[:-1]:
            obj = getattr(obj, attr)
        final = parts[-1]
        existing = getattr(obj, final)

        if isinstance(existing, Position3) and isinstance(value, (list, tuple)):
            existing.data[:] = value
        elif isinstance(existing, Velocity) and isinstance(value, (list, tuple)):
            existing.Vx, existing.Vy, existing.omega = value
        else:
            setattr(obj, final, value)
            
                
        logger.debug(f"at handle_set_entry, {self.gait_prg.config}")
#     def run(self):
#         time.sleep(0.1)
#         while True:
#             cmd = cmd_queue.get(timeout=0.001)
#             # 批量属性写入
#             for entry in cmd.get("set", ()):  
#                 self.handle_set_entry(*entry)
#             # 模式切换
#             self.handler.switch(cmd)
#             # 步态执行与中断检测
#             try:
#                 next_cmd = cmd_queue.get_nowait()
#             except Empty:
#                 self.handler.step()
#             else:
#                 cmd_queue.put(next_cmd)
#             cmd_queue.task_done()

    def run(self):
        time.sleep(0.1)  # 启动延迟
        while True:
            try:
                # 尝试获取命令，等待 1ms
                cmd = cmd_queue.get(timeout=0.001)
            except Empty:
                # 队列为空：执行自动步态
                self.handler.step()
                continue  # 回到循环，继续尝试获取或执行步态

            # 若获取到 cmd，则按原逻辑处理
#             for entry in cmd.get("set", ()):
#                 self.handle_set_entry(*entry)
            for entry in cmd.get("set", ()):  # each entry should be (path, value)
                if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                    logger.warning(f"Invalid set entry: {entry}")
                    continue
                self.handle_set_entry(entry[0], entry[1])

            self.handler.switch(cmd)
            cmd_queue.task_done()

if __name__ == "__main__":
    Controller().run()
