# main.py

import sys
import time
import threading
from utils.logger_tools import logger
#################
# 确保项目根目录在 sys.path 中
sys.path.append('/home/pi/SpiderPi/')

import Joystick2 as js
import Controller as controller

def start_threads():

    # 启动摇杆事件线程
    th_js = threading.Thread(
            target=js.get_joystick_data,
        name="JoystickThread",
        daemon=True
    )


    ctrl = controller.Controller()
    # 启动控制器主循环线程
    th_ctrl = threading.Thread(
        target=ctrl.run,
        name="ControllerThread",
        daemon=True
    )

    th_js.start()
    th_ctrl.start()
    logger.info("Started JoystickThread and ControllerThread")

if __name__ == "__main__":
    start_threads()

    # 阻塞主线程，等待中断
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, exiting.")
