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
    def get_proxy_for_phone(cls, phone):
        """
        根据手机号选择对应国家的代理
        
        参数：
        - phone: 手机号（格式：+972555509621）
        
        返回：
        - 代理字典 或 None
        """
        if not os.path.exists(cls.PROXY_FILE):
            print(f'  ⚠️ 代理文件不存在: {cls.PROXY_FILE}')
            return None
        
        # 提取国家代码（手机号前缀）
        country_code = cls._extract_country_code(phone)
        
        if not country_code:
            print(f'  ⚠️ 无法识别手机号国家: {phone}')
            return None
        
        print(f'  🌍 手机号国家代码: +{country_code}')
        
        # 读取代理配置
        with open(cls.PROXY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            print(f'  ⚠️ 代理文件为空')
            return None
        
        # 解析代理（按国家分组）
        proxies_by_country = {}
        global_proxies = []
        
        for line in lines:
            if '|' not in line:
                # 旧格式兼容（没有国家标识，当作全局代理）
                global_proxies.append(line)
                continue
            
            country, proxy_url = line.split('|', 1)
            country = country.strip()
            proxy_url = proxy_url.strip()
            
            if country == 'global':
                global_proxies.append(proxy_url)
            else:
                if country not in proxies_by_country:
                    proxies_by_country[country] = []
                proxies_by_country[country].append(proxy_url)
        
        # 优先使用对应国家的代理
        if country_code in proxies_by_country:
            proxy_list = proxies_by_country[country_code]
            print(f'  ✅ 找到 {len(proxy_list)} 个 +{country_code} 代理')
            proxy_url = random.choice(proxy_list)
        elif global_proxies:
            print(f'  ⚠️ 未找到 +{country_code} 代理，使用全局代理')
            proxy_url = random.choice(global_proxies)
        else:
            print(f'  ❌ 没有可用的代理')
            return None
        
        # 解析代理URL
        return cls._parse_proxy_url(proxy_url)
    
    @classmethod
    def _extract_country_code(cls, phone):
        """
        从手机号提取国家代码
        
        示例：
        - +972555509621 → 972
        - +8613800138000 → 86
        - +16501234567 → 1
        """
        import re
        
        # 移除+号和空格
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # 常见国家代码长度：1-3位
        # 优先匹配较长的（避免86被识别为8）
        
        # 3位国家代码（优先）
        if phone[:3] in ['971', '972', '973', '974', '975', '976', '977', '994', '995', '998']:
            return phone[:3]
        
        # 2位国家代码
        if phone[:2] in ['20', '27', '30', '31', '32', '33', '34', '36', '39', '40', 
                          '41', '43', '44', '45', '46', '47', '48', '49', '51', '52', 
                          '53', '54', '55', '56', '57', '58', '60', '61', '62', '63', 
                          '64', '65', '66', '81', '82', '84', '86', '90', '91', '92', 
                          '93', '94', '95', '98']:
            return phone[:2]
        
        # 1位国家代码（美国/加拿大）
        if phone[:1] == '1':
            return '1'
        
        # 7位（俄罗斯/哈萨克斯坦）
        if phone[:1] == '7':
            return '7'
        
        # 无法识别
        return None
    
    @classmethod
    def get_random_proxy(cls):
        """
        从proxy.txt随机获取一个代理（旧方法，保持兼容）
        
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
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            print(f'  ⚠️ 代理文件为空')
            return None
        
        # 过滤掉国家标识，获取所有代理URL
        proxies = []
        for line in lines:
            if '|' in line:
                _, proxy_url = line.split('|', 1)
                proxies.append(proxy_url.strip())
            else:
                proxies.append(line)
        
        if not proxies:
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
