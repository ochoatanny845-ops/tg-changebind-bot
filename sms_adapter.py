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
        """logincode.add4533.com 平台（API方式）"""
        # 从URL提取token
        # 格式: https://logincode.add4533.com/?token=39822457-96cd-4d9c-af62-4576b7dd7d5f
        import re
        match = re.search(r'[?&]token=([^&]+)', self.api_url)
        
        if not match:
            print(f'  ⚠️ 无法从URL提取token: {self.api_url}')
            return None
        
        token = match.group(1)
        
        # API endpoint（猜测，根据常见模式）
        api_url = f'https://logincode.add4533.com/api/code?token={token}'
        
        print(f'  🔍 尝试API查询: {api_url}')
        
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            # 尝试多种可能的字段名
                            code = data.get('code') or data.get('verifyCode') or data.get('sms')
                            
                            if code:
                                print(f'  ✅ 获取到验证码: {code}')
                                return str(code)
                        
                        # 如果API不存在，回退到HTML解析
                        if resp.status == 404:
                            print(f'  ⚠️ API不存在，回退到HTML解析')
                            return await self._get_code_logincode_html(timeout)
                        
                        await asyncio.sleep(5)
                        
                except aiohttp.ClientError as e:
                    print(f'  ⚠️ API查询失败，尝试HTML解析: {e}')
                    return await self._get_code_logincode_html(timeout)
                except Exception as e:
                    print(f'  ⚠️ 查询失败: {e}')
                    await asyncio.sleep(5)
        
        print(f'  ❌ 超时未获取到验证码')
        return None
    
    async def _get_code_logincode_html(self, timeout):
        """logincode HTML解析（备用）"""
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    async with session.get(self.api_url) as resp:
                        html = await resp.text()
                        
                        # 尝试从HTML中提取（可能在<script>标签中）
                        import re
                        
                        # 匹配JavaScript中的验证码变量
                        patterns = [
                            r'verifyCode["\']?\s*[:=]\s*["\']?(\d{5,6})',
                            r'code["\']?\s*[:=]\s*["\']?(\d{5,6})',
                            r'sms["\']?\s*[:=]\s*["\']?(\d{5,6})',
                            r'"code":\s*"?(\d{5,6})"?',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, html, re.IGNORECASE)
                            if match:
                                code = match.group(1)
                                print(f'  ✅ 获取到验证码: {code}')
                                return code
                        
                        await asyncio.sleep(5)
                        
                except Exception as e:
                    print(f'  ⚠️ 查询失败: {e}')
                    await asyncio.sleep(5)
        
        print(f'  ❌ 超时未获取到验证码')
        return None
    
    async def _get_code_tgapi(self, timeout):
        """tgapi88880.duckdns.org 平台（SSE实时推送）"""
        # 从verify URL提取API key
        # 格式: https://tgapi88880.duckdns.org/verify/09990aadf5b37c05e373ce2300aa378f
        api_key = self.api_url.split('/verify/')[-1]
        
        # SSE stream URL
        sse_url = f"https://tgapi88880.duckdns.org/api/stream/{api_key}"
        
        print(f'  📡 连接SSE stream: {sse_url}')
        
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sse_url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    async for line in resp.content:
                        # 检查超时
                        if asyncio.get_event_loop().time() - start_time > timeout:
                            print(f'  ❌ 超时未获取到验证码')
                            return None
                        
                        # 解析SSE数据
                        line_str = line.decode('utf-8').strip()
                        
                        # SSE格式: data: {"code":"9689","time":"2026-04-18 00:52:43"}
                        if line_str.startswith('data:'):
                            data_json = line_str[5:].strip()
                            
                            try:
                                import json
                                data = json.loads(data_json)
                                
                                if 'code' in data and data['code']:
                                    code = str(data['code']).strip()
                                    print(f'  ✅ 获取到验证码: {code}')
                                    return code
                                    
                            except json.JSONDecodeError:
                                continue
                        
            except asyncio.TimeoutError:
                print(f'  ❌ SSE连接超时')
                return None
            except Exception as e:
                print(f'  ⚠️ SSE连接失败: {e}')
                return None
        
        print(f'  ❌ 未获取到验证码')
        return None
    
    async def _get_code_custom(self, timeout):
        """通用平台（自定义）"""
        print(f'  ⚠️ 未识别的接码平台，使用通用解析')
        return await self._get_code_logincode(timeout)
