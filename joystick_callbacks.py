# joystick_callbacks.py

# import pod2 as pod
from utils.thread_init import cmd_queue
from utils.math import Position3, Velocity
from utils.logger_tools import logger
'''
可以操作的gait_prg的属性
    gait_prg.set_body_position(Position3())
    gait_prg.velocity : Velocity()
    gait_prg.config.RATIO : float
    gait_prg.config.MAX_SPEED : float
    gait_prg.config.MIN_Z_PACE : float
    gait_prg.config.MAX_R_PACE :float
'''

# 按键按下回调
def on_PSB_CROSS_press():
    print("\nat joystick_cb, CROSS_PRESS\n\n")
    logger.debug("\nat joystick_cb, CROSS_PRESS\n\n")
    cmd_queue.put({
                        'mode' : 'auto',
                        'set' : (('gait_prg.set_body_position', Position3(10,0,0)),
                                ('gait_prg.velocity', Velocity(100,0,0)),)
                    }
                  )
    





def on_PSB_CIRCLE_press():
    cmd_queue.put(
                {
                    'mode' : 'manual',
                    'action_group' : 'A02.json'
                }
    )




def on_PSB_SQUARE_press():
    print("\nat joystick_cb, CROSS_PRESS\n\n")
    logger.debug("\nat joystick_cb, CROSS_PRESS\n\n")
    cmd_queue.put({
                        'mode' : 'auto',
                        'set' : (('gait_prg.set_body_position', Position3(10,0,0)),
                                ('gait_prg.velocity', Velocity(50,0,0)),)
                    }
                  )

def on_PSB_TRIANGLE_press():
    print("\nat joystick_cb, CROSS_PRESS\n\n")
    logger.debug("\nat joystick_cb, CROSS_PRESS\n\n")
    cmd_queue.put({
                        'mode' : 'auto',
                        'set' : (('gait_prg.set_body_position', Position3(10,0,0)),)
                    }
                  )

def on_PSB_L1_press():
    print("\nat joystick_cb, CROSS_PRESS\n\n")
    logger.debug("\nat joystick_cb, CROSS_PRESS\n\n")
    cmd_queue.put({
                        'mode' : 'auto',
                        'set' : (('gait_prg.set_body_position', Position3(10,0,0)),)
                    }
                  )


def on_PSB_R1_press():
    pass

def on_PSB_L2_press():
    pass

def on_PSB_R2_press():
    pass

def on_PSB_SELECT_press():
    pass

def on_PSB_START_press():
    pass




# 方向帽回调
def on_HAT_LEFT_press():
    # pod.set_Left_button()
    pass
def on_HAT_RIGHT_press():
    # pod.set_Right_button()
    pass
def on_HAT_UP_press():
    # pod.set_Up_button()
    pass
def on_HAT_DOWN_press():
    # pod.set_Down_button()
    pass

# 摇杆回调
def on_LEFT_STICK_press(x, y):
    # pod.set_LEFT_STICK_button(x, y)
    pass
def on_RIGHT_STICK_press(x, y):
    # pod.set_RIGHT_STICK_button(x, y)
    pass

# 统一的按键松开回调
def on_button_release():
    # pod.button_release()
    cmd_queue.put({
                        'mode' : 'auto',
                        'set' : (
                                ('gait_prg.velocity', Velocity(0,0,0)),)
                    }
                  )

