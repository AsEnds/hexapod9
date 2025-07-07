# utils 文件夹
存放一些工具

## thread_init.py
配置全局的共享队列和线程锁，所有文件都'from utils.thread_init import cmd_queue，controller_lock'，保证使用的是同一个队列和线程锁。
- `cmd_queue`：传递控制指令的队列。
- `controller_lock`：在多线程环境下保护共享资源。

## test_board.py
在测试时，替换原有的驱动舵机的函数。
- 提供 `DummyBoard` 类，便于在无硬件时模拟舵机接口。

## math.py
存放一些数学工具或类
- 定义向量、位姿等数据结构及常用几何计算。

## logger_tools.py
配置多文件可共享的logger，其他文件只需要'from utils.logger_tools import logger'即可让logger替代print进行调试。可以在'config/log_config.json'修改一些参数

logger用法：自查
- `logger.debug/info/warning` 等方法输出不同级别日志。
- 日志级别及输出路径由 `log_config.json` 控制。

## cv_debug_tools.py
目前提供两个：

**cv_debug 装饰器**
将图像处理函数包裹起来，开启或关闭“Debug Panel”滑条参数输入。

* `debug=False`：使用默认初始值直接执行。
* `debug=True`：实时读取滑条值传入函数，实现调参预览。

**show_hsv_overlay**
在原图上标记当前鼠标位置并显示该点的 HSV 值。

* 读取全局 `mouse_pos`，转换图像到 HSV，获取像素值。
* 绘制小圆点并在图上写出 `HSV:h,s,v`，方便颜色调试。

## base_func.py 测试用，防止无法导入Board.py，报错

## _utils_path_setup.py
用于动态修改 `sys.path`，确保测试脚本可以顺利导入本目录下的模块。






