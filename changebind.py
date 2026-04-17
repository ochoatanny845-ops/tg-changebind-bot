"""
换绑核心逻辑
"""
import asyncio
import random
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.tl.functions.account import SendChangePhoneCodeRequest, ChangePhoneRequest
from telethon.tl.types import CodeSettings
from config import Config
from sms_adapter import SMSAdapter

# 随机设备型号池
DEVICE_MODELS = [
    'Samsung Galaxy S21',
    'Samsung Galaxy S22',
    'iPhone 13 Pro',
    'iPhone 14',
    'Xiaomi Mi 11',
    'OnePlus 9',
    'Google Pixel 6',
    'Huawei P50'
]

class ChangeBinder:
    """换绑器"""
    
    def __init__(self):
        self.config = Config()
    
    async def login_account(self, phone, api_url, session_file):
        """登录账号到新设备"""
        print(f'\n📱 登录账号')
        print(f'  手机号: {phone}')
        print(f'  API: {api_url}')
        print(f'  Session: {session_file}')
        
        try:
            # 随机选择设备型号
            device_model = random.choice(DEVICE_MODELS)
            print(f'  设备: {device_model}')
            
            # 根据手机号国家选择代理
            proxy = Config.get_proxy_for_phone(phone)
            
            # 创建客户端（模拟设备）
            client = TelegramClient(
                session_file,
                Config.API_ID,
                Config.API_HASH,
                device_model=device_model,
                system_version='Android 12' if 'Samsung' in device_model or 'Xiaomi' in device_model else 'iOS 16',
                app_version='9.5.2',
                lang_code='zh',
                system_lang_code='zh-CN',
                proxy=proxy  # 使用匹配国家的代理
            )
            
            await client.connect()
            
            # 检查是否已登录
            if await client.is_user_authorized():
                print(f'  ✅ Session有效，已登录')
                me = await client.get_me()
                print(f'  账号: {me.first_name} (@{me.username or "无用户名"})')
                await client.disconnect()
                return {
                    'success': True,
                    'device_model': device_model,
                    'already_logged_in': True
                }
            
            # 1. 发起登录请求
            print(f'\n[1/3] 发起登录请求...')
            await client.send_code_request(phone)
            
            # 2. 获取验证码
            print(f'[2/3] 获取验证码...')
            sms = SMSAdapter(api_url)
            code = await sms.get_code(timeout=180)
            
            if not code:
                await client.disconnect()
                return {
                    'success': False,
                    'error': '未获取到验证码'
                }
            
            # 3. 登录
            print(f'[3/3] 登录...')
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await client.disconnect()
                return {
                    'success': False,
                    'error': '账号启用了2FA，需要密码'
                }
            
            # 验证登录
            me = await client.get_me()
            print(f'  ✅ 登录成功!')
            print(f'  账号: {me.first_name} (@{me.username or "无用户名"})')
            print(f'  ID: {me.id}')
            
            await client.disconnect()
            
            return {
                'success': True,
                'device_model': device_model,
                'user_info': {
                    'id': me.id,
                    'name': me.first_name,
                    'username': me.username
                }
            }
            
        except Exception as e:
            print(f'  ❌ 登录失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    async def change_phone(self, session_file, new_phone, api_url):
        """更换手机号"""
        print(f'\n🔄 开始换绑')
        print(f'  新手机号: {new_phone}')
        print(f'  API: {api_url}')
        print(f'  Session: {session_file}')
        
        try:
            # 根据新手机号国家选择代理
            proxy = Config.get_proxy_for_phone(new_phone)
            
            # 1. 连接客户端
            print(f'\n[1/5] 连接账号...')
            client = TelegramClient(
                session_file,
                Config.API_ID,
                Config.API_HASH,
                proxy=proxy  # 使用匹配国家的代理
            )
            
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {
                    'success': False,
                    'error': 'Session失效，请重新登录'
                }
            
            # 获取当前账号信息
            me = await client.get_me()
            old_phone = me.phone
            print(f'  当前手机号: +{old_phone}')
            print(f'  账号: {me.first_name}')
            
            # 2. 发起换绑请求
            print(f'[2/5] 发起换绑请求...')
            result = await client(SendChangePhoneCodeRequest(
                phone_number=new_phone,
                settings=CodeSettings()
            ))
            
            phone_code_hash = result.phone_code_hash
            print(f'  ✅ 换绑请求已发送')
            
            # 3. 获取验证码
            print(f'[3/5] 获取验证码...')
            sms = SMSAdapter(api_url)
            code = await sms.get_code(timeout=180)
            
            if not code:
                await client.disconnect()
                return {
                    'success': False,
                    'error': '未获取到验证码'
                }
            
            # 4. 完成换绑
            print(f'[4/5] 提交验证码...')
            await client(ChangePhoneRequest(
                phone_number=new_phone,
                phone_code_hash=phone_code_hash,
                phone_code=code
            ))
            
            # 5. 验证结果
            print(f'[5/5] 验证结果...')
            me = await client.get_me()
            current_phone = me.phone
            
            await client.disconnect()
            
            if current_phone == new_phone.lstrip('+'):
                print(f'  ✅ 换绑成功!')
                print(f'  旧手机号: +{old_phone}')
                print(f'  新手机号: +{current_phone}')
                return {
                    'success': True,
                    'old_phone': f'+{old_phone}',
                    'new_phone': f'+{current_phone}'
                }
            else:
                return {
                    'success': False,
                    'error': f'换绑失败，当前手机号仍为 +{current_phone}'
                }
            
        except Exception as e:
            print(f'  ❌ 换绑失败: {e}')
            if 'client' in locals():
                await client.disconnect()
            return {
                'success': False,
                'error': str(e)
            }
