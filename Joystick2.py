# Joystick.py
import sys
import os
import time
import pygame
import joystick_callbacks as cb

# 可选地添加 Raspberry Pi 路径
spi_path = '/home/pi/SpiderPi/'
if os.path.exists(spi_path):
    sys.path.append(spi_path)

# PS 手柄按钮映射
key_map = {
    "PSB_CROSS": 0,  "PSB_CIRCLE": 1,   "PSB_SQUARE": 3,   "PSB_TRIANGLE": 4,
    "PSB_L1": 6,     "PSB_R1": 7,       "PSB_L2": 8,       "PSB_R2": 9,
    "PSB_SELECT": 10,"PSB_START": 11
}

DEBOUNCE_INTERVAL = 0.05
button_states = {key: False for key in key_map}
last_press_time = {key: 0.0 for key in key_map}
hat_flag = False


def joystick_init():
    """初始化 Joystick 实例"""
    if os.name != 'nt':
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.init()
    pygame.joystick.init()
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Joystick initialized: {js.get_name()} | Axes: {js.get_numaxes()} | Buttons: {js.get_numbuttons()} | Hats: {js.get_numhats()}")
    return js


def get_joystick_data():
    """主循环：仅在未连接时检测设备，已连接时处理输入"""
    global hat_flag
    pygame.init()
    connected = False
    js = None

    while True:
        if not connected:
            # 检测并初始化设备
            pygame.joystick.quit()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                try:
                    js = joystick_init()
                    connected = True
                    print("Joystick connected.")
                except Exception as e:
                    print("Init error:", e)
                    js = None
        else:
            # 检查是否断开
            if pygame.joystick.get_count() == 0:
                print("Joystick disconnected.")
                connected = False
                js = None
            else:
                # 处理输入事件
                pygame.event.pump()
                now = time.time()

                # 按键按下/松开
                for button, idx in key_map.items():
                    pressed = False
                    try:
                        pressed = bool(js.get_button(idx))
                    except Exception:
                        pass
                    if pressed and not button_states[button]:
                        if now - last_press_time[button] > DEBOUNCE_INTERVAL:
                            func = getattr(cb, f"on_{button}_press", None)
                            if callable(func): func()
                            button_states[button] = True
                            last_press_time[button] = now
                    elif not pressed and button_states[button]:
                        cb.on_button_release()
                        button_states[button] = False

                # 摇杆 (Axes)
                lx1, ly1 = js.get_axis(0), js.get_axis(1)
                if abs(lx1) > 1e-3 or abs(ly1) > 1e-3:
                    cb.on_LEFT_STICK_press(lx1, ly1)
                lx2, ly2 = js.get_axis(2), js.get_axis(3)
                if abs(lx2) > 1e-3 or abs(ly2) > 1e-3:
                    cb.on_RIGHT_STICK_press(lx2, ly2)

                # 方向帽 (Hat)
                hat_x, hat_y = js.get_hat(0)
                if (hat_x, hat_y) != (0, 0):
                    if not hat_flag:
                        if hat_x == 1: cb.on_HAT_RIGHT_press()
                        elif hat_x == -1: cb.on_HAT_LEFT_press()
                        if hat_y == 1: cb.on_HAT_UP_press()
                        elif hat_y == -1: cb.on_HAT_DOWN_press()
                        hat_flag = True
                else:
                    if hat_flag:
                        cb.on_button_release()
                        hat_flag = False

        time.sleep(0.01)

if __name__ == "__main__":
    get_joystick_data()