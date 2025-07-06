import queue
import threading

# 全局命令队列
cmd_queue = queue.Queue(maxsize=5)

# 线程锁
controller_lock = threading.Lock()    