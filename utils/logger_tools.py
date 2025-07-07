from utils._utils_path_setup import ROOT_DIR
import logging
import json
import os
import threading


# 可以通过环境变量指定配置文件
_config_path = os.getenv("LOGGER_CONFIG", f"{ROOT_DIR}/config/log_config.json")


def _load_config():
    """
    从 JSON 文件加载配置，失败时返回默认
    """
    try:
        with open(_config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # 加载失败，使用默认
        return {"level": "INFO", "to_file": False, "file_path": "app.log"}

    # 手动校验配置字段类型
    level = data.get("log_level", "INFO")
    to_file = data.get("log_to_file", False)
    file_path = data.get("log_file_path", "app.log")

    if not isinstance(level, str):
        level = "INFO"
    if not isinstance(to_file, bool):
        to_file = False
    if not isinstance(file_path, str):
        file_path = "app.log"

    return {"level": level.upper(), "to_file": to_file, "file_path": file_path}


class LoggerManager:
    _lock = threading.Lock()

    def __init__(self):
        # 获取或创建同名 Logger
        self.logger = logging.getLogger("my_logger")
        self._setup_handlers()

    def _setup_handlers(self):
        """
        初始化并添加 Handler，仅在 __init__ 时调用，线程安全
        """
        cfg = _load_config()
        level = getattr(logging, cfg["level"], logging.INFO)

        with LoggerManager._lock:
            self.logger.setLevel(level)
            # 移除旧的所有 handler
            for h in list(self.logger.handlers):
                self.logger.removeHandler(h)

            # 日志格式
            fmt = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # 控制台输出
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(fmt)
            self.logger.addHandler(ch)

            # 文件输出（可选）
            if cfg["to_file"]:
                # 确保目录存在
                dirpath = os.path.dirname(cfg["file_path"]) or "."
                os.makedirs(dirpath, exist_ok=True)
                fh = logging.FileHandler(cfg["file_path"], encoding="utf-8")
                fh.setLevel(level)
                fh.setFormatter(fmt)
                self.logger.addHandler(fh)


# 全局单例
logger = LoggerManager().logger


if __name__ == "__main__":
    logger.info("Logger initialized with validated config and thread-safe handlers.")
