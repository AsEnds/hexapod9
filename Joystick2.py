import time
import pygame
import joystick_callbacks as cb

# 键盘映射：key name → 模拟按钮名
key_map = {
    pygame.K_j: "PSB_CROSS",
    pygame.K_k: "PSB_CIRCLE",
    pygame.K_u: "PSB_SQUARE",
    pygame.K_l: "PSB_TRIANGLE",
    pygame.K_a: "PSB_L1",
    pygame.K_d: "PSB_R1",
    pygame.K_s: "PSB_L2",
    pygame.K_f: "PSB_R2",
    pygame.K_q: "PSB_SELECT",
    pygame.K_e: "PSB_START",
    pygame.K_LEFT:  "HAT_LEFT",
    pygame.K_RIGHT: "HAT_RIGHT",
    pygame.K_UP:    "HAT_UP",
    pygame.K_DOWN:  "HAT_DOWN",
}

DEBOUNCE_INTERVAL = 0.05
key_states = {k: False for k in key_map}  # 按键状态（去抖）
last_press_time = {k: 0 for k in key_map}


def get_keyboard_data():
    pygame.init()
    screen = pygame.display.set_mode((100, 100))  # 必须启用窗口，才能获取键盘事件
    pygame.display.set_caption("Keyboard Simulation")

    running = True
    while running:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in key_map and not key_states[event.key]:
                    if now - last_press_time[event.key] > DEBOUNCE_INTERVAL:
                        key_states[event.key] = True
                        last_press_time[event.key] = now
                        btn = key_map[event.key]
                        func = getattr(cb, f"on_{btn}_press", None)
                        if callable(func): func()

            elif event.type == pygame.KEYUP:
                if event.key in key_map:
                    key_states[event.key] = False
                    cb.on_button_release()

        time.sleep(0.01)


if __name__ == "__main__":
    get_keyboard_data()