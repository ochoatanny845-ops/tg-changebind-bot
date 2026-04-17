"""
配置管理
"""
import os
import random
import time
from dotenv import load_dotenv
from country_codes import get_country_code

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
        根据手机号生成对应国家的代理
        
        参数：
        - phone: 手机号（格式：+972555509621）
        
        返回：
        - 代理字典 或 None
        """
        if not os.path.exists(cls.PROXY_FILE):
            print(f'  ⚠️ 代理文件不存在: {cls.PROXY_FILE}')
            return None
        
        # 提取国家代码（手机号前缀）
        phone_country_code = cls._extract_country_code(phone)
        
        if not phone_country_code:
            print(f'  ⚠️ 无法识别手机号国家: {phone}')
            return None
        
        # 转换为ISO国家代码
        country_iso = get_country_code(phone_country_code)
        
        if not country_iso:
            print(f'  ⚠️ 未找到国家代码 +{phone_country_code} 的映射')
            # 没有国家映射时，仍然继续（使用不带国家的代理）
            country_iso = 'xx'
        
        print(f'  🌍 手机号: +{phone_country_code} → 国家: {country_iso.upper()}')
        
        # 读取代理模板
        with open(cls.PROXY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            print(f'  ⚠️ 代理文件为空')
            return None
        
        # 随机选择一个代理模板
        proxy_template = random.choice(lines)
        
        # 生成随机数（10000-9999999999）
        random_num = random.randint(10000, 9999999999)
        
        # 生成会话ID（时间戳）
        session_id = int(time.time() * 1000)
        
        # 替换模板变量
        proxy_string = (proxy_template
                       .replace('{country}', country_iso)
                       .replace('{session}', str(session_id))
                       .replace('{random}', str(random_num))
                       .replace('{session_time}', '0'))  # 一次一换
        
        print(f'  🔒 生成代理: {proxy_string}')
        
        # 解析代理字符串
        return cls._parse_proxy_string(proxy_string)
    
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
    def _parse_proxy_string(cls, proxy_string):
        """
        解析代理字符串（支持多种格式）
        
        格式1（URL）: socks5://user:pass@host:port
        格式2（简化）: host:port:user:pass
        """
        # 尝试格式2：host:port:user:pass
        if '://' not in proxy_string:
            parts = proxy_string.split(':')
            if len(parts) == 4:
                host, port, username, password = parts
                return {
                    'proxy_type': 'socks5',  # 默认使用socks5
                    'addr': host,
                    'port': int(port),
                    'username': username,
                    'password': password
                }
        
        # 格式1：使用URL解析
        return cls._parse_proxy_url(f'socks5://{proxy_string}' if '://' not in proxy_string else proxy_string)
    
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
