"""
配置管理
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # Bot配置
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Telegram API
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', '')
    
    # 管理员
    ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
    
    # API
    SMS_API_URL = os.getenv('SMS_API_URL', '')
    
    # 数据库
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'changebind.db')
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.BOT_TOKEN:
            raise ValueError('BOT_TOKEN 未配置')
        if not cls.API_ID or not cls.API_HASH:
            raise ValueError('API_ID 或 API_HASH 未配置')
        if not cls.ADMIN_ID:
            raise ValueError('ADMIN_ID 未配置')
