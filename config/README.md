# config文件夹
用于存放与机器人相关的各种配置文件。

## hexapod_config.py
- 将旧项目中 `Hexapod.py` 的全局变量整合为 `HexapodConfig` 类。
- 定义机器人的尺寸、步态周期等核心参数，供各模块读取。

## leg_conf.json
- 保存每条腿的零位校准数据，在启动时由 `HexapodConfig` 载入。

## leg_conf_default.json
- 作为 `leg_conf.json` 的模板文件，可在需要重置或调试时参考。

## log_config.json
存放 `utils/logger_tools` 的日志配置：
- 调试等级（低于该级别的日志不会输出到控制台）。
- 是否输出文件。
- 日志文件保存路径。
