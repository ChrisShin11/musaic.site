# app/utils/logger.py
import os, sys
from loguru import logger

logger.remove()

# Always log to stdout (Cloud Run collects this)
logger.add(sys.stdout, enqueue=True, backtrace=True, diagnose=False, level=os.getenv("LOG_LEVEL", "INFO"))

# Optional file logging (off by default). Use /tmp which is writable on Cloud Run.
if os.getenv("LOG_TO_FILE", "0") == "1":
    log_dir = os.getenv("LOG_DIR", "/tmp/logs")
    os.makedirs(log_dir, exist_ok=True)
    logger.add(
        os.path.join(log_dir, "app.log"),
        rotation="10 MB",
        retention="7 days",
        enqueue=True,
        level=os.getenv("LOG_LEVEL", "INFO"),
    )

def get_logger(name=None):
    return logger
