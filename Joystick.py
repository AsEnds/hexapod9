# joystick.py

import sys
import os
import time
import pygame
import joystick_callbacks as cb

# 确保能 import pod2（如果回调里还用到 pod2）
sys.path.append('/home/pi/SpiderPi/')

# PS 手柄按钮映射
key_map = {
    "PSB_CROSS": 0,  "PSB_CIRCLE": 1,   "PSB_SQUARE": 3,   "PSB_TRIANGLE": 4,
    "PSB_L1": 6,     "PSB_R1": 7,       "PSB_L2": 8,       "PSB_R2": 9,
    "PSB_SELECT": 10,"PSB_START": 11
}

# 去抖间隔（秒）
DEBOUNCE_INTERVAL = 0.05

# 记录按钮状态与上次触发时间
button_states     = {key: False for key in key_map}
last_press_time   = {key: 0.0 for key in key_map}

# 记录方向帽状态，避免重复松开回调
hat_flag = False

def joystick_init():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.init()
    pygame.joystick.init()
    js = pygame.joystick.Joystick(0)
    js.init()
    print("Joystick initialized:", js.get_name(),
          "| Axes:", js.get_numaxes(),
          "| Buttons:", js.get_numbuttons(),
          "| Hats:", js.get_numhats())

def get_joystick_data():
    """主循环：检测设备、按键、摇杆、方向帽，触发回调并带去抖"""
    global hat_flag
    connected = False
    js = None

    while True:
        # 检测设备节点
        if os.path.exists("/dev/input/js0"):
            if not connected:
                try:
                    joystick_init()
                    js = pygame.joystick.Joystick(0)
                    js.init()
                    connected = True
                    print("Joystick connected.")
                except Exception as e:
                    print("Init error:", e)
        else:
            if connected:
                print("Joystick disconnected.")
                connected = False
                pygame.joystick.quit()

        if connected:
            pygame.event.pump()
            now = time.time()
            try:
                # —— 按键按下/松开（带去抖） —— 
                for button, idx in key_map.items():
                    pressed = bool(js.get_button(idx))
                    if pressed and not button_states[button]:
                        # 按键按下且之前为释放状态
                        if now - last_press_time[button] > DEBOUNCE_INTERVAL:
                            func = getattr(cb, f"on_{button}_press", None)
                            if callable(func):
                                func()
                            button_states[button] = True
                            last_press_time[button] = now
                    elif not pressed and button_states[button]:
                        # 按键松开
                        cb.on_button_release()
                        button_states[button] = False

                # —— 左摇杆 —— 
                lx1, ly1 = js.get_axis(0), js.get_axis(1)
                if abs(lx1) > 1e-3 or abs(ly1) > 1e-3:
                    cb.on_LEFT_STICK_press(lx1, ly1)

                # —— 右摇杆 —— 
                lx2, ly2 = js.get_axis(2), js.get_axis(3)
                if abs(lx2) > 1e-3 or abs(ly2) > 1e-3:
                    cb.on_RIGHT_STICK_press(lx2, ly2)

                # —— 方向帽 —— 
                hat_x, hat_y = js.get_hat(0)
                if hat_x != 0 or hat_y != 0:
                    if not hat_flag:
                        if hat_x == 1:    cb.on_HAT_RIGHT_press()
                        elif hat_x == -1: cb.on_HAT_LEFT_press()
                        if hat_y == 1:    cb.on_HAT_UP_press()
                        elif hat_y == -1: cb.on_HAT_DOWN_press()
                        hat_flag = True
                else:
                    if hat_flag:
                        cb.on_button_release()
                        hat_flag = False

            except Exception as e:
                print("Loop error:", e)
                connected = False

        time.sleep(0.01)


if __name__ == "__main__":
    get_joystick_data()
