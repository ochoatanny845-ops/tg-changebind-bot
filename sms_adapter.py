"""
接码API适配器
支持多种接码平台
"""
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup

class SMSAdapter:
    """接码适配器"""
    
    def __init__(self, api_url):
        self.api_url = api_url
        self.platform = self.detect_platform()
    
    def detect_platform(self):
        """根据URL自动识别平台"""
        if 'logincode.add4533.com' in self.api_url:
            return 'logincode'
        elif 'tgapi88880.duckdns.org' in self.api_url:
            return 'tgapi'
        else:
            return 'custom'
    
    async def get_code(self, timeout=180):
        """
        获取验证码（统一接口）
        timeout: 超时时间（秒），默认3分钟
        """
        print(f'  📱 从接码平台获取验证码...')
        print(f'  平台: {self.platform}')
        print(f'  URL: {self.api_url}')
        
        if self.platform == 'logincode':
            return await self._get_code_logincode(timeout)
        elif self.platform == 'tgapi':
            return await self._get_code_tgapi(timeout)
        else:
            return await self._get_code_custom(timeout)
    
    async def _get_code_logincode(self, timeout):
        """logincode.add4533.com 平台"""
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    async with session.get(self.api_url) as resp:
                        html = await resp.text()
                        
                        # 解析HTML，查找验证码
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 尝试多种可能的选择器
                        code = None
                        
                        # 方式1: 查找包含数字的元素
                        for elem in soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3']):
                            text = elem.get_text().strip()
                            # 匹配5-6位数字
                            match = re.search(r'\b(\d{5,6})\b', text)
                            if match:
                                code = match.group(1)
                                break
                        
                        if code:
                            print(f'  ✅ 获取到验证码: {code}')
                            return code
                        
                        # 等待5秒后重试
                        await asyncio.sleep(5)
                        
                except Exception as e:
                    print(f'  ⚠️ 查询失败: {e}')
                    await asyncio.sleep(5)
        
        print(f'  ❌ 超时未获取到验证码')
        return None
    
    async def _get_code_tgapi(self, timeout):
        """tgapi88880.duckdns.org 平台"""
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    async with session.get(self.api_url) as resp:
                        html = await resp.text()
                        
                        # 解析HTML
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 查找验证码
                        code = None
                        
                        for elem in soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3']):
                            text = elem.get_text().strip()
                            match = re.search(r'\b(\d{5,6})\b', text)
                            if match:
                                code = match.group(1)
                                break
                        
                        if code:
                            print(f'  ✅ 获取到验证码: {code}')
                            return code
                        
                        await asyncio.sleep(5)
                        
                except Exception as e:
                    print(f'  ⚠️ 查询失败: {e}')
                    await asyncio.sleep(5)
        
        print(f'  ❌ 超时未获取到验证码')
        return None
    
    async def _get_code_custom(self, timeout):
        """通用平台（自定义）"""
        print(f'  ⚠️ 未识别的接码平台，使用通用解析')
        return await self._get_code_logincode(timeout)
