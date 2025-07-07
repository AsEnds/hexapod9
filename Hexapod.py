# Hexapod.py
import numpy as np
import time
import sys
import os
import json

from typing import List
from config.hexapod_config import HexapodConfig



from utils.math import Position3, Velocity, Thetas


from utils.base_func import *
Board, is_debug_mode = import_board_module()

# PSTEP = 16
PI = np.pi
# N_POINTS = 4

# LEG_LEN1 = 57.0
# LEG_LEN2 = 120.0
# LEG_LEN3 = 186.0

# CHASSIS_LEN = 255.0
# CHASSIS_WIDTH = 177.0
# CHASSIS_FRONT_WIDTH = 132.0

# THETA_STAND_2 = 60.0 / 180.0 * PI
# THETA_STAND_3 = -140 / 180.0 * PI

# K_CEN = 500.0
# KR_2 = 1.0

# MAX_R_PACE = 150.0
# MAX_SPEED = 0.5 * 660

# MIN_Z_PACE = 100
# MAX_Z_PACE = 200

# MIN_JOINT2_RAD = -0.5 * PI
# MAX_JOINT2_RAD = PI / 2.0
# MIN_JOINT3_RAD = -(18.0 / 19.0) * PI
# MAX_JOINT3_RAD = PI / 2

# K_W = 1.0 / 56.56854

# SMOOTH_BETA = 0.3  # IK 角度低通滤波系数

# LegControl_round = 0

# def limits_ok(thetas, margin=0.01):
#     """Return True if (θ1,θ2,θ3) are within physical limits.
#     By default θ1 is allowed full rotation; modify as needed.
#     """
#     theta1, theta2, theta3 = thetas

#     # θ2, θ3 limits
#     if not (MIN_JOINT2_RAD + margin <= theta2 <= MAX_JOINT2_RAD - margin): 
#         return False
#     if not (MIN_JOINT3_RAD + margin <= theta3 <= MAX_JOINT3_RAD - margin): 
#         return False

#     # Optional θ1 check: uncomment if hardware restricts yaw
#     # if not (MIN_JOINT1_RAD - margin <= theta1 <= MAX_JOINT1_RAD + margin):
#     #     return False

#     return True

# import json
# import os

# data = None
# config_file = "leg_conf.json"
# try:
#     if not os.path.exists(config_file):
#         raise FileNotFoundError(f"文件不存在: {config_file}")
#     with open(config_file, "r", encoding="utf-8") as f:
#         data = json.load(f)
# except FileNotFoundError:
#     print(f"[警告] 配置文件未找到：{config_file}，将采用默认配置。")
#     # 可选：这里可设置data = {...}为你期望的默认配置
#     data = {
#         "legs": [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
#         "dir_offsets": [[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
#         "angle_offsets": [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
#     }
# except json.JSONDecodeError as e:
#     print(f"[错误] 配置文件内容格式损坏：{config_file}，错误信息：{e}")
#     # 同样建议设data为默认值或弹窗警告
#     data = {
#         "legs": [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
#         "dir_offsets": [[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
#         "angle_offsets": [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
#     }
# except Exception as e:
#     print(f"[错误] 读取配置文件时发生未知异常：{e}")
#     # 这里也可以设data为默认
#     data = {
#         "legs": [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
#         "dir_offsets": [[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
#         "angle_offsets": [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
#     }

# dir_offsets = data["dir_offsets"]
# print(f"dir_offsets={dir_offsets}")

# legs = data["legs"]
# print(f"legs={legs}")

# angle_offsets = data["angle_offsets"]
# print(f"angle_offsets={angle_offsets}")




# leg_num = 6

# default_angles = [
#     [PI / 4, THETA_STAND_2, THETA_STAND_3],
#     [0, THETA_STAND_2, THETA_STAND_3],
#     [-PI / 4, THETA_STAND_2, THETA_STAND_3],
#     [3 * PI / 4, THETA_STAND_2, THETA_STAND_3],
#     [PI, THETA_STAND_2, THETA_STAND_3],
#     [5 * PI / 4, THETA_STAND_2, THETA_STAND_3],
# ]

# dir_offsets = [
#     [1, 0, 1],
#     [1, 0, 1],
#     [1, 0, 1],
#     [1, 1, 0],
#     [1, 1, 0],
#     [1, 1, 0],
# ]
# angle_offsets = [
#     [-0.785398163397448, -0.031415926535898, 1.099557428756428],
#     [-0.062831853071796, -0.062831853071796, 0.376991118430775],
#     [1.005309649148734, 0.345575191894877, 0.157079632679490],
#     [-1.853539665617978, -0.062831853071796, 1.005309649148734],
#     [-3.078760800517997, -0.031415926535898, 1.036725575684632],
#     [-5*PI/4, 0.000000000000000, 0.251327412287183],
# ]

# legs = [
#             [1,   2,    3],
#             [4,   5,    6],
#             [7,   8,    9],
#             [10,  11,  12],
#             [13,  14,  15],
#             [16,  17,  18]
# ]
class GaitPrg:
    def __init__(self, config: HexapodConfig = None):

        self.config = config or HexapodConfig()
        
        self.prev_thetas = None
        self.last_pulses = {}
        
        self.step_mode = 0
        # self.leg_num = leg_num
        self.pace_time = 1000
        self.actions = np.zeros((self.config.N_POINTS, 6, 3))  # 存储六条腿的步态点，N_POINTS 是每条腿的点数
        self.points = np.zeros((self.config.N_POINTS, 6, 3))
        self.default_angles = self.config.default_angles

        self.Pws = [self.fkine(self.config.default_angles[0][0], self.config.default_angles[0][1], self.config.default_angles[0][2]),
                    self.fkine(self.config.default_angles[1][0], self.config.default_angles[1][1], self.config.default_angles[1][2]),
                    self.fkine(self.config.default_angles[2][0], self.config.default_angles[2][1], self.config.default_angles[2][2]),
                    self.fkine(self.config.default_angles[3][0], self.config.default_angles[3][1], self.config.default_angles[3][2]),
                    self.fkine(self.config.default_angles[4][0], self.config.default_angles[4][1], self.config.default_angles[4][2]),
                    self.fkine(self.config.default_angles[5][0], self.config.default_angles[5][1], self.config.default_angles[5][2])]

        self.Pws_default = np.copy(self.Pws)

        self.P_legs = [
            Position3(self.config.CHASSIS_FRONT_WIDTH / 2, self.config.CHASSIS_LEN / 2, 0),
            Position3(self.config.CHASSIS_WIDTH / 2, 0, 0),
            Position3(self.config.CHASSIS_FRONT_WIDTH / 2, -self.config.CHASSIS_LEN / 2, 0),
            Position3(-self.config.CHASSIS_FRONT_WIDTH / 2, self.config.CHASSIS_LEN / 2, 0),
            Position3(-self.config.CHASSIS_WIDTH / 2, 0, 0),
            Position3(-self.config.CHASSIS_FRONT_WIDTH / 2, -self.config.CHASSIS_LEN / 2, 0)
        ]

        self.dir_offsets = self.config.dir_offsets

        self.angle_offsets = self.config.angle_offsets

        self.legs = self.config.legs

        self.CEN = Position3()
        self.R_pace = 0
        self.body_pos = Position3()
        self.velocity = Velocity()
        self.velocity_s = Velocity()
        self.rotate_angle = Position3()


    def fkine(self, angle1, angle2, angle3):
        x = np.cos(angle1) * (self.config.LEG_LEN1 + self.config.LEG_LEN3 * np.cos(angle2 + angle3) + self.config.LEG_LEN2 * np.cos(angle2))
        y = np.sin(angle1) * (self.config.LEG_LEN1 + self.config.LEG_LEN3 * np.cos(angle2 + angle3) + self.config.LEG_LEN2 * np.cos(angle2))
        z = self.config.LEG_LEN3 * np.sin(angle2 + angle3) + self.config.LEG_LEN2 * np.sin(angle2)
        return Position3(x, y, z)



    def ikine(self, pos : Position3):
        pos1 = pos
        R = np.sqrt(pos1.x ** 2 + pos1.y ** 2)
        Lr = np.sqrt(pos1.z ** 2 + (R - self.config.LEG_LEN1) ** 2)
        alpha_r = np.arctan(-pos1.z / (R - self.config.LEG_LEN1))
        alpha1 = np.arccos(np.clip((self.config.LEG_LEN2 ** 2 + Lr ** 2 - self.config.LEG_LEN3 ** 2) / (2 * self.config.LEG_LEN2 * Lr), -1.0, 1.0))
        alpha2 = np.arccos(np.clip((Lr ** 2 + self.config.LEG_LEN3 ** 2 - self.config.LEG_LEN2 ** 2) / (2 * Lr * self.config.LEG_LEN3), -1.0, 1.0))
        angle1 = np.arctan2(pos1.y, pos1.x)
        angle2 = alpha1 - alpha_r
        angle3 = -(alpha1 + alpha2)
        angle2 = np.clip(angle2, self.config.MIN_JOINT2_RAD, self.config.MAX_JOINT2_RAD)
        angle3 = np.clip(angle3, self.config.MIN_JOINT3_RAD, self.config.MAX_JOINT3_RAD)
        return Thetas(angle1, angle2, angle3)
    
    # def ikine(self, pos):
    #     x, y, z = pos.x, pos.y, pos.z
    #     R  = np.hypot(x, y)
    #     # —— 奇异点处理 —— 
    #     if R < 1e-6:
    #         return self.prev_thetas if self.prev_thetas else Thetas(0.0, THETA_STAND_2, THETA_STAND_3)
    #     Lr = np.hypot(z, R - LEG_LEN1)
    #     theta1 = np.arctan2(y, x)

    #     D = (LEG_LEN2**2 + LEG_LEN3**2 - Lr**2) / (2*LEG_LEN2*LEG_LEN3)
    #     D = np.clip(D, -1.0, 1.0)
    #     theta3_dn = np.arctan2(+np.sqrt(1-D**2), D) * (-1)
    #     theta3_up = np.arctan2(-np.sqrt(1-D**2), D) * (-1)

    #     def hip_pitch(t3):
    #         phi = np.arctan2(z, R - LEG_LEN1)
    #         psi = np.arctan2(LEG_LEN3*np.sin(t3), LEG_LEN2 + LEG_LEN3*np.cos(t3))
    #         return phi + psi

    #     # 两套合法解
    #     cand = [
    #         (theta1, hip_pitch(theta3_dn), theta3_dn),
    #         (theta1, hip_pitch(theta3_up), theta3_up),
    #     ]
    #     legal = [c for c in cand if limits_ok(c)]
    #     if not legal:
    #         raise ValueError("目标点不可达")

    #     # —— 选择与上一次解最接近的解 —— 
    #     if self.prev_thetas is None or len(legal) == 1:
    #         choice = legal[0]
    #     else:
    #         choice = min(
    #             legal,
    #             key=lambda c: np.linalg.norm(np.subtract(c, self.prev_thetas.angle))
    #         )
    #     new_theta = Thetas(*choice)
    #     # —— 低通滤波平滑（可选）——
    #     if self.prev_thetas is not None:
    #         beta = SMOOTH_BETA
    #         smooth_vals = [
    #             prev + beta * (new - prev)
    #             for new, prev in zip(new_theta.angle, self.prev_thetas.angle)
    #         ]
    #         new_theta = Thetas(*smooth_vals)

    #     self.prev_thetas = new_theta  # 更新“上一次解”
    #     return new_theta

    def hexapod_rotate(self, point, index):
        cos_a, sin_a = np.cos(self.rotate_angle.y), np.sin(self.rotate_angle.y)
        cos_b, sin_b = np.cos(self.rotate_angle.z), np.sin(self.rotate_angle.z)
        cos_g, sin_g = np.cos(self.rotate_angle.x), np.sin(self.rotate_angle.x)

        rotation_matrix = np.array([
            [cos_b * cos_a, cos_b * sin_a, -sin_b],
            [sin_g * sin_b * cos_a - cos_g * sin_a, sin_g * sin_b * sin_a + cos_g * cos_a, sin_g * cos_b],
            [cos_g * sin_b * cos_a + sin_g * sin_a, cos_g * sin_b * sin_a - sin_g * cos_a, cos_g * cos_b]
        ])

        new_coords = rotation_matrix.dot(point.data)

        return Position3(*new_coords)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_height(self, height):
        for i in range(6):
            self.Pws[i].z = self.Pws_default[i].z - height

    def get_body_pos(self):
        return self.body_pos

    def set_body_position(self, body_pos):
        self.body_pos = body_pos
        for i in range(6):
            self.Pws[i] = self.Pws_default[i] - self.body_pos

    def CEN_and_pace_cal(self):
        self.velocity.Vx = 0.001 if self.velocity.Vx == 0.0 else self.velocity.Vx
        self.velocity.Vy = 0.001 if self.velocity.Vy == 0.0 else self.velocity.Vy
        self.velocity.omega = 0.001 if self.velocity.omega == 0.0 else self.velocity.omega

        module_CEN = self.config.K_CEN / self.velocity.omega * np.sqrt(self.velocity.Vx ** 2 + self.velocity.Vy ** 2)

        self.velocity_s.Vx = -self.velocity.Vy
        self.velocity_s.Vy = self.velocity.Vx

        if self.velocity_s.Vx >= 0:
            self.CEN.x = np.sqrt((module_CEN ** 2) / (1 + self.velocity.Vx ** 2 / self.velocity.Vy ** 2))
        else:
            self.CEN.x = -np.sqrt((module_CEN ** 2) / (1 + self.velocity.Vx ** 2 / self.velocity.Vy ** 2))

        module_speed = (self.velocity.Vx ** 2 + self.velocity.Vy ** 2 + self.velocity.omega ** 2) ** (1 / 2)
        module_speed = module_speed if module_speed < self.config.MAX_SPEED else self.config.MAX_SPEED
        self.R_pace = self.config.KR_2 * module_speed
        self.pace_time = 1000 if self.R_pace <= self.config.MAX_R_PACE else 1000 * self.config.MAX_R_PACE / self.R_pace
        # self.R_pace = MAX_R_PACE
        # self.pace_time = MAX_R_PACE / module_speed   * 1000
        self.R_pace = min(self.R_pace, self.config.MAX_R_PACE)

        self.CEN.y = -self.CEN.x * self.velocity.Vx / self.velocity.Vy

    def gait_programing(self, LegControl_round, N_POINTS, MIN_Z_PACE):
        Vec_CEN2leg_ends = [Position3() for _ in range(6)]
        angle_off = [0.0] * 6
        norm_CEN2legs = [0.0] * 6
        Rp_ratios = [0.0] * 6
        Vec_Leg_Start2CEN_s = [Position3() for _ in range(6)]

        for i in range(6):
            Vec_CEN2leg_ends[i] = self.Pws[i] + self.P_legs[i] - self.CEN
            angle_off[i] = np.arctan2(Vec_CEN2leg_ends[i].y, Vec_CEN2leg_ends[i].x)
            norm_CEN2legs[i] = np.sqrt(Vec_CEN2leg_ends[i].x ** 2 + Vec_CEN2leg_ends[i].y ** 2)
            Vec_Leg_Start2CEN_s[i] = self.CEN - self.P_legs[i]

        max_norm_CEN2legs = max(norm_CEN2legs)

        R_paces = [0.0] * 6
        for i in range(6):
            Rp_ratios[i] = norm_CEN2legs[i] / max_norm_CEN2legs
            R_paces[i] = Rp_ratios[i] * self.R_pace

        d_theta = 2 * R_paces[0] / norm_CEN2legs[0]
        step_size = d_theta / (N_POINTS / 2)

        for i in range(0, 6, 2):
            if LegControl_round < N_POINTS / 2:
                angle_t = angle_off[i] + d_theta / 2 - step_size * LegControl_round
                point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
                point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)
                point_z = self.Pws[i].z
            else:
                angle_t = angle_off[i] - d_theta / 2 + step_size * (LegControl_round - N_POINTS / 2)
                point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
                point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)

                y_temp = -self.R_pace + (LegControl_round - N_POINTS / 2) * (self.R_pace * 4 / N_POINTS)
                # if (self.step_mode == 0):
                if 0.5 < self.R_pace < MIN_Z_PACE:
                    point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * self.config.RATIO + self.Pws[i].z
                else:
                    point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * self.config.RATIO + self.Pws[i].z
                # else:
                #     if 0.5 < self.R_pace < MIN_Z_PACE:
                #         point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * PSTEP + self.Pws[i].z
                #     else:
                #         point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * PSTEP + self.Pws[i].z




            point = Position3(point_x, point_y, point_z)
            rotated_point = self.hexapod_rotate(point, i)
            self.points[LegControl_round, i] = rotated_point.data + self.P_legs[i].data
            self.actions[LegControl_round, i] = self.ikine(rotated_point).angle

        for i in range(1, 6, 2):
            if LegControl_round < N_POINTS / 2:
                angle_t = angle_off[i] - d_theta / 2 + step_size * LegControl_round
                point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
                point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)

                y_temp = -self.R_pace + LegControl_round * (self.R_pace * 4 / N_POINTS)
                # if (self.step_mode == 0):
                if 0.5 < self.R_pace < MIN_Z_PACE:
                    point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * self.config.RATIO + self.Pws[i].z
                else:
                    point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * self.config.RATIO + self.Pws[i].z
                # else:
                #     if 0.5 < self.R_pace < MIN_Z_PACE:
                #         point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * PSTEP + self.Pws[i].z
                #     else:
                #         point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * PSTEP + self.Pws[i].z
            else:
                angle_t = angle_off[i] + d_theta / 2 - step_size * (LegControl_round - N_POINTS / 2)
                point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
                point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)
                point_z = self.Pws[i].z


            point = Position3(point_x, point_y, point_z)
            rotated_point = self.hexapod_rotate(point, i)
            self.points[LegControl_round, i] = rotated_point.data + self.P_legs[i].data
            self.actions[LegControl_round, i] = self.ikine(rotated_point).angle

    # def gait4_programing(self, LegControl_round, N_POINTS, MIN_Z_PACE):
    #     Vec_CEN2leg_ends = [Position3() for _ in range(6)]
    #     angle_off = [0.0] * 6
    #     norm_CEN2legs = [0.0] * 6
    #     Rp_ratios = [0.0] * 6
    #     Vec_Leg_Start2CEN_s = [Position3() for _ in range(6)]

    #     for i in range(6):
    #         Vec_CEN2leg_ends[i] = self.Pws[i] + self.P_legs[i] - self.CEN
    #         angle_off[i] = np.arctan2(Vec_CEN2leg_ends[i].y, Vec_CEN2leg_ends[i].x)
    #         norm_CEN2legs[i] = np.sqrt(Vec_CEN2leg_ends[i].x ** 2 + Vec_CEN2leg_ends[i].y ** 2)
    #         Vec_Leg_Start2CEN_s[i] = self.CEN - self.P_legs[i]

    #     max_norm_CEN2legs = max(norm_CEN2legs)

    #     R_paces = [0.0] * 6
    #     for i in range(6):
    #         Rp_ratios[i] = norm_CEN2legs[i] / max_norm_CEN2legs
    #         R_paces[i] = Rp_ratios[i] * self.R_pace

    #     d_theta = 2 * R_paces[0] / norm_CEN2legs[0]
    #     step_size = d_theta / (N_POINTS / 2)
    #     for i in [0, 5]:
    #         if LegControl_round < N_POINTS / 2:
    #             angle_t = angle_off[i] + d_theta / 2 - step_size * LegControl_round
    #             point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
    #             point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)
    #             point_z = self.Pws[i].z
    #         else:
    #             angle_t = angle_off[i] - d_theta / 2 + step_size * (LegControl_round - N_POINTS / 2)
    #             point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
    #             point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)

    #             y_temp = -self.R_pace + (LegControl_round - N_POINTS / 2) * (self.R_pace * 4 / N_POINTS)
    #             if (self.step_mode == 0):
    #                 if 0.5 < self.R_pace < MIN_Z_PACE:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 + self.Pws[i].z
    #                 else:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] + self.Pws[i].z
    #             else:
    #                 if 0.5 < self.R_pace < MIN_Z_PACE:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * PSTEP + self.Pws[i].z
    #                 else:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * PSTEP + self.Pws[i].z


    #         point = Position3(point_x, point_y, point_z)
    #         rotated_point = self.hexapod_rotate(point, i)
    #         self.points[LegControl_round, i] = rotated_point.data + self.P_legs[i].data
    #         self.actions[LegControl_round, i] = self.ikine(rotated_point).angle

    #     for i in [2, 3]:
    #         if LegControl_round < N_POINTS / 2:
    #             angle_t = angle_off[i] - d_theta / 2 + step_size * LegControl_round
    #             point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
    #             point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)

    #             y_temp = -self.R_pace + LegControl_round * (self.R_pace * 4 / N_POINTS)
    #             if (self.step_mode == 0):
    #                 if 0.5 < self.R_pace < MIN_Z_PACE:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 + self.Pws[i].z
    #                 else:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] + self.Pws[i].z
    #             else:
    #                 if 0.5 < self.R_pace < MIN_Z_PACE:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * 3 * PSTEP + self.Pws[i].z
    #                 else:
    #                     point_z = np.sqrt(self.R_pace ** 2 - y_temp ** 2) * Rp_ratios[i] * PSTEP + self.Pws[i].z
    #         else:
    #             angle_t = angle_off[i] + d_theta / 2 - step_size * (LegControl_round - N_POINTS / 2)
    #             point_x = Vec_Leg_Start2CEN_s[i].x + norm_CEN2legs[i] * np.cos(angle_t)
    #             point_y = Vec_Leg_Start2CEN_s[i].y + norm_CEN2legs[i] * np.sin(angle_t)
    #             point_z = self.Pws[i].z

    #         point = Position3(point_x, point_y, point_z)
    #         rotated_point = self.hexapod_rotate(point, i)
    #         self.points[LegControl_round, i] = rotated_point.data + self.P_legs[i].data
    #         self.actions[LegControl_round, i] = self.ikine(rotated_point).angle

    # def gait_programing(self, LegControl_round, N_POINTS, MIN_Z_PACE):
    #     if self.leg_num == 6:
    #         self.gait6_programing(LegControl_round, N_POINTS, MIN_Z_PACE)
    #     elif self.leg_num == 4:
    #         self.gait4_programing(LegControl_round, N_POINTS, MIN_Z_PACE)
    #     else:
    #         print("leg_num error!")

    def get_pace_time(self):
        return self.pace_time

    def normalize_angle(self, a):
        return (a + PI) % (2*PI) - PI
    # def setJointAngle(self, dirOffset, legIndex, angle, time):
    #     pulse = 500 + angle / PI * 750 if dirOffset == 1 else 500 - angle / PI * 750
    #     Board.setBusServoPulse(legIndex, int(pulse), int(time))

    def set_leg(self, leg_id: int, position: Position3, time: int = 500) -> None: #leg_id: 0-5
        thetas = self.ikine(position)#已知xyz调用函数求角度
        # print(f"thetas = {thetas}")
        # print("啊啊啊")
        # print("啊啊啊")
        # print(f"leg_id = {leg_id}")
        # if thetas.angle[0] <= -PI:
        #     thetas.angle[0] += 2 * PI
        thetas.angle[0] = self.normalize_angle(thetas.angle[0])
        for i in range(3):
            self.setJointAngle(self.config.dir_offsets[leg_id][i],self.config.legs[leg_id][i],(thetas.angle[i]+self.config.angle_offsets[leg_id][i]),time)
            # print(f"i={i}")

    def set_all_legs(self, leg_action: List[6], time: int = 500):
        for i in range(6):
            self.set_leg(i, leg_action[i], time)

    def setJointAngle(self, dirOffset, legIndex, angle, time):
        pulse = 500 + angle / PI * 750 if dirOffset == 1 else 500 - angle / PI * 750
        pulse = int(pulse)

        # 若与上一次脉冲不变，则跳过
        if self.last_pulses.get(legIndex) != pulse:
            Board.setBusServoPulse(legIndex, pulse, int(time))
            self.last_pulses[legIndex] = pulse
        else:
            pass

    def move(self, round_time, LegControl_round):
        # if self.leg_num == 6:
        for leg in range(6):
            theta_temp = self.actions[LegControl_round, leg] + self.angle_offsets[leg]
            # if theta_temp[0] < -2 / 3 * PI:
            #     theta_temp[0] += 2 * PI
            theta_temp[0] = self.normalize_angle(theta_temp[0])
            for joint in range(3):
                self.setJointAngle(self.dir_offsets[leg][joint], self.legs[leg][joint], theta_temp[joint],
                                    round_time)
        # elif self.leg_num == 4:
        #     for leg in [0, 2, 3, 5]:
        #         theta_temp = self.actions[LegControl_round, leg] + self.angle_offsets[leg]
        #         # if theta_temp[0] < -2 / 3 * PI:
        #         #     theta_temp[0] += 2 * PI
        #         theta_temp[0] = self.normalize_angle(theta_temp[0])
        #         for joint in range(3):
        #             self.setJointAngle(self.dir_offsets[leg][joint], self.legs[leg][joint], theta_temp[joint],
        #                                round_time)
        # else:
        #     print("leg_num error!")
    
    # def set_step_mode(self):
    #     if self.step_mode == 0:
    #         print("Switched to manual mode")
    #         self.step_mode = 1
    #     else:
    #         print("Switched to auto mode")
    #         self.step_mode = 0

# gait_prg = None
# move_flag = False
# def hexapod_init():
#     global gait_prg
#     gait_prg = GaitPrg(leg_num, default_angles, dir_offsets, angle_offsets, legs)

# def hexapod_move():
#     global LegControl_round
#     global gait_prg
#     time.sleep(0.1)
#     while True:
#         while move_flag:
#             for _ in range(N_POINTS):
#                 code_time_start = time.time()  # 获取当前时间（毫秒）

#                 if gait_prg.velocity.omega >= 0:
#                     LegControl_round = (LegControl_round + 1) % N_POINTS  # 控制回合自增长
#                 else:
#                     if LegControl_round == 0:
#                         LegControl_round = N_POINTS - 1
#                     else:
#                         LegControl_round -= 1
#                 # 步态控制
#                 gait_prg.CEN_and_pace_cal()
#                 gait_prg.gait_programing(LegControl_round, N_POINTS, MIN_Z_PACE)

#                 # 开始移动
#                 round_time = gait_prg.get_pace_time() / N_POINTS
#                 gait_prg.move(round_time, LegControl_round)
#                 code_time_end = time.time()  # 获取当前时间（毫秒）
#                 code_time = code_time_end - code_time_start  # 计算程序运行时间（毫秒）
#                 if code_time < round_time:
#                     time.sleep((round_time - code_time) / 1000)  # 保证程序执行周期等于回合时间
#                 else:
#                     time.sleep(0.001)  # 至少延时1ms

# def set_body_pos(x, y, z):
#     bodypos = Position3(x, y, z)
#     gait_prg.set_body_position(bodypos)

# def set_velocity(Vx, Vy, omega):
#     velocity = Velocity(Vx, Vy, omega)
#     gait_prg.set_velocity(velocity)

# def set_step_mode():
#     gait_prg.set_step_mode()

# def get_body_pos():
#     return gait_prg.set_body_pos()