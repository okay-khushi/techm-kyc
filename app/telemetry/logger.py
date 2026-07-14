import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", backtrace=False, diagnose=False)


def get_logger():
    return logger
