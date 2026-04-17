"""
配置管理
"""
import os
import random
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
    
    # 代理配置
    PROXY_FILE = os.getenv('PROXY_FILE', 'proxy.txt')
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.BOT_TOKEN:
            raise ValueError('BOT_TOKEN 未配置')
        if not cls.API_ID or not cls.API_HASH:
            raise ValueError('API_ID 或 API_HASH 未配置')
        if not cls.ADMIN_ID:
            raise ValueError('ADMIN_ID 未配置')
    
    @classmethod
    def get_random_proxy(cls):
        """
        从proxy.txt随机获取一个代理
        
        支持格式：
        - http://127.0.0.1:7890
        - socks5://127.0.0.1:1080
        - socks5://user:pass@host:port
        - http://user:pass@host:port
        
        返回格式：
        {
            'proxy_type': 'socks5',  # or 'http'
            'addr': '127.0.0.1',
            'port': 1080,
            'username': None,        # or 'user'
            'password': None         # or 'pass'
        }
        """
        if not os.path.exists(cls.PROXY_FILE):
            print(f'  ⚠️ 代理文件不存在: {cls.PROXY_FILE}')
            return None
        
        with open(cls.PROXY_FILE, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not proxies:
            print(f'  ⚠️ 代理文件为空')
            return None
        
        # 随机选择一个代理
        proxy_url = random.choice(proxies)
        
        # 解析代理URL
        return cls._parse_proxy_url(proxy_url)
    
    @classmethod
    def _parse_proxy_url(cls, proxy_url):
        """
        解析代理URL
        
        示例：
        - socks5://127.0.0.1:1080
        - http://user:pass@host:port
        """
        import re
        
        # 匹配格式：(type)://(user:pass@)?host:port
        pattern = r'^(http|https|socks4|socks5)://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)$'
        match = re.match(pattern, proxy_url)
        
        if not match:
            print(f'  ⚠️ 代理格式错误: {proxy_url}')
            return None
        
        proxy_type, username, password, host, port = match.groups()
        
        # Telethon只支持socks5和http
        if proxy_type not in ['socks5', 'http', 'https']:
            print(f'  ⚠️ 不支持的代理类型: {proxy_type}（仅支持http/socks5）')
            return None
        
        # https当作http处理
        if proxy_type == 'https':
            proxy_type = 'http'
        
        proxy_dict = {
            'proxy_type': proxy_type,
            'addr': host,
            'port': int(port),
            'username': username or None,
            'password': password or None
        }
        
        print(f'  🔒 使用代理: {proxy_type}://{host}:{port}')
        
        return proxy_dict
