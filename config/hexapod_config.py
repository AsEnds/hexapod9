# HexapodConfig.py
from dataclasses import dataclass, field
import numpy as np
import json
import os

@dataclass
class HexapodConfig:
    # —— 常量参数 —— 
    # PSTEP: int = 16
    # PI: float = np.pi
    N_POINTS: int = 4

    LEG_LEN1: float = 57.0
    LEG_LEN2: float = 120.0
    LEG_LEN3: float = 186.0

    CHASSIS_LEN: float = 255.0
    CHASSIS_WIDTH: float = 177.0
    CHASSIS_FRONT_WIDTH: float = 132.0
    
    THETA_STAND_2: float = 60.0 / 180.0 * np.pi
    THETA_STAND_3: float = -140.0 / 180.0 * np.pi

    RATIO = 2 # 改变抬腿，z方向上的高度倍率

    K_CEN: float = 500.0
    KR_2: float = 1.0

    MAX_R_PACE: float = 150.0
    MAX_SPEED: float = 0.5 * 660

    MIN_Z_PACE: float = 100
    MAX_Z_PACE: float = 200

    MIN_JOINT2_RAD: float = -0.5 * np.pi
    MAX_JOINT2_RAD: float = np.pi / 2
    MIN_JOINT3_RAD: float = -(18.0 / 19.0) * np.pi
    MAX_JOINT3_RAD: float = np.pi / 2

    K_W: float = 1.0 / 56.56854
    SMOOTH_BETA: float = 0.3
    # leg_num: int = 6

    # —— 从 JSON 加载的配置 —— 
    config_file: str = "conf_pkg\leg_conf.json"
    dir_offsets: list = field(default_factory=list)
    legs: list        = field(default_factory=list)
    angle_offsets: list = field(default_factory=list)

    # —— 动态状态 —— 
    LegControl_round: int = 0
    # move_flag: bool = False

    def __post_init__(self):
        # 读取 JSON，覆盖默认配置
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            # JSON 缺失时的默认值
            data = {
                "legs":      [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
                "dir_offsets": [[1,1,1]]*6,
                "angle_offsets": [[0,0,0]]*6
            }
        self.dir_offsets    = data["dir_offsets"]
        self.legs           = data["legs"]
        self.angle_offsets  = data["angle_offsets"]
