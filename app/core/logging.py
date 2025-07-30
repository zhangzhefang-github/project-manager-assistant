import sys
import os
from loguru import logger

def setup_logging():
    """设置全局日志配置，支持不同级别和输出方式"""
    logger.remove()
    
    # 控制台日志 - 只显示WARNING及以上级别，减少输出
    logger.add(
        sys.stderr,
        level="WARNING",  # 从INFO改为WARNING，减少控制台输出
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件日志 - 保留详细信息用于调试
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/app.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",  # 单文件最大10MB
        retention="7 days",  # 保留7天
        compression="zip"  # 自动压缩旧日志
    )
    
    # 错误日志单独记录
    logger.add(
        "logs/error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="5 MB",
        retention="30 days"
    )
    
    logger.info("优化的日志系统已配置 - 控制台输出已减少，详细日志保存在logs/目录")

setup_logging() 