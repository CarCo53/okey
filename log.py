import logging
from functools import wraps
import os

class CentralLogger:
    def __init__(self, name="okey_logger", log_file="game.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Önceki handler'ları temizle
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        fh = logging.FileHandler(log_file, encoding='utf-8', mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
    
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def debug(self, msg): self.logger.debug(msg)
    
    def log_function(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"CALL {func.__qualname__}")
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"RETURN {func.__qualname__} -> {result}")
                return result
            except Exception as e:
                self.logger.error(f"ERROR in {func.__qualname__}: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                raise
        return wrapper

# Global logger instance
logger = CentralLogger()