"""
TG换绑助手Bot - 主程序
"""
import asyncio
import re
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from changebind import ChangeBinder
from database import Database

# 用户状态
user_states = {}

def normalize_phone(phone):
    """规范化手机号（自动添加+号）"""
    phone = phone.strip()
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

def parse_input(text):
    """
    解析输入格式：手机号 API网址
    支持格式：
    - +972555509621 https://logincode.add4533.com/?token=xxx
    - 551191074765 https://tgapi88880.duckdns.org/verify/xxx
    """
    parts = text.strip().split()
    
    if len(parts) < 2:
        return None, None
    
    phone = normalize_phone(parts[0])
    api_url = parts[1]
    
    return phone, api_url

class ChangeBindBot:
    """换绑助手Bot"""
    
    def __init__(self):
        # 验证配置
        Config.validate()
        
        # 初始化数据库
        self.db = Database()
        
        # 初始化换绑器
        self.binder = ChangeBinder()
        
        # 创建应用
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # 设置处理器
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置处理器"""
        self.app.add_handler(CommandHandler('start', self.cmd_start))
        self.app.add_handler(CommandHandler('login', self.cmd_login))
        self.app.add_handler(CommandHandler('status', self.cmd_status))
        self.app.add_handler(CommandHandler('list', self.cmd_list))
        self.app.add_handler(CommandHandler('changebind', self.cmd_changebind))
        self.app.add_handler(CommandHandler('help', self.cmd_help))
        self.app.add_handler(CommandHandler('cancel', self.cmd_cancel))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))  # 文件处理
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """启动命令"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限。本Bot仅供管理员使用。')
            return
        
        await update.message.reply_text(
            '👋 欢迎使用TG换绑助手！\n\n'
            '📱 功能：\n'
            '/login - 登录账号到新设备（开始24小时等待）\n'
            '/status - 查看账号状态\n'
            '/list - 列出所有账号\n'
            '/changebind - 执行换绑\n'
            '/help - 查看帮助\n'
            '/cancel - 取消当前操作\n\n'
            '💡 使用流程：\n'
            '1️⃣ /login 登录账号\n'
            '2️⃣ 等待24小时\n'
            '3️⃣ /changebind 换绑到新手机号'
        )
    
    async def cmd_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """登录命令"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        user_states[user_id] = {'step': 'waiting_login_info'}
        
        await update.message.reply_text(
            '📱 请输入账号信息\n\n'
            '单个账号：\n'
            '手机号 API网址\n\n'
            '批量登录（每行一个）：\n'
            '+972555509621 https://logincode.add4533.com/?token=xxx\n'
            '+55119107476 https://tgapi88880.duckdns.org/verify/yyy\n'
            '+8613800138000 https://logincode.add4533.com/?token=zzz\n\n'
            '或发送 TXT 文件（每行一个账号）\n\n'
            '💡 如果手机号没有+号，会自动添加\n\n'
            '发送 /cancel 取消'
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """查看状态"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        accounts = self.db.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text('📋 暂无账号')
            return
        
        # 统计
        pending = sum(1 for a in accounts if a['status'] == 'pending')
        ready = sum(1 for a in accounts if a['status'] == 'ready')
        completed = sum(1 for a in accounts if a['status'] == 'completed')
        failed = sum(1 for a in accounts if a['status'] == 'failed')
        
        text = (
            f'📊 账号状态统计\n\n'
            f'⏳ 等待中: {pending}\n'
            f'✅ 就绪: {ready}\n'
            f'🎉 已完成: {completed}\n'
            f'❌ 失败: {failed}\n'
            f'➖➖➖➖➖➖➖➖➖\n'
            f'📱 总计: {len(accounts)}\n\n'
            f'使用 /list 查看详细列表'
        )
        
        await update.message.reply_text(text)
    
    async def cmd_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """列出所有账号"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        accounts = self.db.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text('📋 暂无账号')
            return
        
        text = '📋 账号列表\n\n'
        
        for acc in accounts:
            status_emoji = {
                'pending': '⏳',
                'ready': '✅',
                'completed': '🎉',
                'failed': '❌'
            }.get(acc['status'], '❓')
            
            text += f'{status_emoji} #{acc["id"]} {acc["old_phone"]}\n'
            text += f'   状态: {acc["status"]}\n'
            
            if acc['status'] == 'pending':
                ready_dt = datetime.fromtimestamp(acc['ready_time'])
                text += f'   就绪时间: {ready_dt.strftime("%m-%d %H:%M")}\n'
            
            if acc['status'] == 'completed':
                text += f'   新手机号: {acc["new_phone"]}\n'
            
            if acc['error_message']:
                text += f'   错误: {acc["error_message"]}\n'
            
            text += '\n'
        
        await update.message.reply_text(text)
    
    async def cmd_changebind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """换绑命令"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        user_states[user_id] = {'step': 'waiting_changebind_id'}
        
        await update.message.reply_text(
            '🔄 请输入账号ID和新手机号信息\n\n'
            '格式：\n'
            '账号ID 新手机号 API网址\n\n'
            '示例：\n'
            '1 +8613900139000 https://logincode.add4533.com/?token=xxx\n\n'
            '💡 使用 /list 查看账号ID\n\n'
            '发送 /cancel 取消'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """帮助命令"""
        await update.message.reply_text(
            '📖 使用帮助\n\n'
            '1️⃣ 登录账号\n'
            '/login\n'
            '输入：手机号 API网址\n\n'
            '2️⃣ 等待24小时\n'
            '使用 /status 查看就绪状态\n\n'
            '3️⃣ 执行换绑\n'
            '/changebind\n'
            '输入：账号ID 新手机号 API网址\n\n'
            '💡 格式示例：\n'
            '+972555509621 https://logincode.add4533.com/?token=xxx\n'
            '551191074765 https://tgapi88880.duckdns.org/verify/xxx'
        )
    
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """取消命令"""
        user_id = update.effective_user.id
        
        if user_id in user_states:
            del user_states[user_id]
            await update.message.reply_text('✅ 已取消')
        else:
            await update.message.reply_text('💡 没有进行中的操作')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            return
        
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        step = state.get('step')
        
        if step == 'waiting_login_info':
            await self.handle_login_input(update)
        elif step == 'waiting_changebind_id':
            await self.handle_changebind_input(update)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文件上传（TXT批量导入）"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            return
        
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        step = state.get('step')
        
        if step != 'waiting_login_info':
            return
        
        # 下载文件
        file = await update.message.document.get_file()
        file_path = f'temp_{user_id}.txt'
        
        await file.download_to_drive(file_path)
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 删除临时文件
            os.remove(file_path)
            
            # 处理内容（复用handle_login_input的逻辑）
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) == 0:
                await update.message.reply_text('❌ 文件为空')
                return
            
            # 解析所有账号
            accounts_to_login = []
            for line in lines:
                phone, api_url = parse_input(line)
                if phone and api_url:
                    accounts_to_login.append((phone, api_url))
                else:
                    await update.message.reply_text(
                        f'❌ 格式错误（第{len(accounts_to_login)+1}行）：\n{line}\n\n'
                        f'正确格式：\n手机号 API网址'
                    )
                    return
            
            # 清除状态
            if user_id in user_states:
                del user_states[user_id]
            
            # 批量登录
            await self._login_batch(update, accounts_to_login)
            
        except Exception as e:
            await update.message.reply_text(f'❌ 文件处理失败: {e}')
            if os.path.exists(file_path):
                os.remove(file_path)
    
    
    async def handle_login_input(self, update: Update):
        """处理登录输入（支持批量）"""
        text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # 检测是否为批量（多行）
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) == 0:
            await update.message.reply_text('❌ 输入为空')
            return
        
        # 解析所有账号
        accounts_to_login = []
        for line in lines:
            phone, api_url = parse_input(line)
            if phone and api_url:
                accounts_to_login.append((phone, api_url))
            else:
                await update.message.reply_text(
                    f'❌ 格式错误（第{len(accounts_to_login)+1}行）：\n{line}\n\n'
                    f'正确格式：\n手机号 API网址'
                )
                return
        
        # 清除状态
        if user_id in user_states:
            del user_states[user_id]
        
        total = len(accounts_to_login)
        
        if total == 1:
            # 单个登录
            await self._login_single(update, accounts_to_login[0][0], accounts_to_login[0][1])
        else:
            # 批量登录
            await self._login_batch(update, accounts_to_login)
    
    async def _login_single(self, update: Update, phone: str, api_url: str):
        """单个登录"""
        await update.message.reply_text(
            f'⏳ 开始登录...\n\n'
            f'手机号: {phone}\n'
            f'API: {api_url}\n\n'
            f'请稍候...'
        )
        
        # 生成session文件名
        session_file = f'sessions/login_{phone.replace("+", "")}'
        os.makedirs('sessions', exist_ok=True)
        
        # 执行登录
        result = await self.binder.login_account(phone, api_url, session_file)
        
        if result['success']:
            # 添加到数据库
            account_id = self.db.add_account(
                phone,
                api_url,
                session_file,
                result['device_model']
            )
            
            ready_time = datetime.now() + timedelta(hours=24)
            
            await update.message.reply_text(
                f'✅ 登录成功！\n\n'
                f'账号ID: #{account_id}\n'
                f'手机号: {phone}\n'
                f'设备: {result["device_model"]}\n\n'
                f'⏰ 就绪时间: {ready_time.strftime("%m-%d %H:%M")}\n'
                f'（24小时后可换绑）\n\n'
                f'使用 /status 查看状态'
            )
        else:
            await update.message.reply_text(
                f'❌ 登录失败\n\n'
                f'错误: {result["error"]}'
            )
    
    async def _login_batch(self, update: Update, accounts: list):
        """批量登录"""
        total = len(accounts)
        
        await update.message.reply_text(
            f'📦 批量登录模式\n\n'
            f'总数: {total} 个账号\n'
            f'开始处理...\n\n'
            f'⏱️ 预计耗时: {total * 2}-{total * 3} 分钟'
        )
        
        success_count = 0
        failed_count = 0
        results = []
        
        for idx, (phone, api_url) in enumerate(accounts, 1):
            # 发送进度
            progress_msg = await update.message.reply_text(
                f'⏳ 进度: {idx}/{total}\n\n'
                f'正在处理: {phone}\n'
                f'设备连接中...'
            )
            
            # 生成session文件名
            session_file = f'sessions/login_{phone.replace("+", "")}'
            os.makedirs('sessions', exist_ok=True)
            
            try:
                # 执行登录
                result = await self.binder.login_account(phone, api_url, session_file)
                
                if result['success']:
                    # 添加到数据库
                    account_id = self.db.add_account(
                        phone,
                        api_url,
                        session_file,
                        result['device_model']
                    )
                    
                    success_count += 1
                    results.append({
                        'success': True,
                        'id': account_id,
                        'phone': phone,
                        'device': result['device_model']
                    })
                    
                    # 更新进度消息
                    await progress_msg.edit_text(
                        f'✅ 成功: {idx}/{total}\n\n'
                        f'账号: {phone}\n'
                        f'ID: #{account_id}\n'
                        f'设备: {result["device_model"]}'
                    )
                else:
                    failed_count += 1
                    results.append({
                        'success': False,
                        'phone': phone,
                        'error': result['error']
                    })
                    
                    # 更新进度消息
                    await progress_msg.edit_text(
                        f'❌ 失败: {idx}/{total}\n\n'
                        f'账号: {phone}\n'
                        f'错误: {result["error"][:100]}'
                    )
                
            except Exception as e:
                failed_count += 1
                results.append({
                    'success': False,
                    'phone': phone,
                    'error': str(e)
                })
                
                # 更新进度消息
                await progress_msg.edit_text(
                    f'❌ 异常: {idx}/{total}\n\n'
                    f'账号: {phone}\n'
                    f'错误: {str(e)[:100]}'
                )
        
        # 发送汇总
        ready_time = datetime.now() + timedelta(hours=24)
        
        summary_text = (
            f'📊 批量登录完成！\n\n'
            f'✅ 成功: {success_count}\n'
            f'❌ 失败: {failed_count}\n'
            f'📱 总计: {total}\n\n'
            f'⏰ 就绪时间: {ready_time.strftime("%m-%d %H:%M")}\n\n'
        )
        
        # 添加成功账号列表
        if success_count > 0:
            summary_text += '✅ 成功账号：\n'
            for r in results:
                if r['success']:
                    summary_text += f'#{r["id"]} {r["phone"]}\n'
            summary_text += '\n'
        
        # 添加失败账号列表
        if failed_count > 0:
            summary_text += '❌ 失败账号：\n'
            for r in results:
                if not r['success']:
                    error_short = r['error'][:30]
                    summary_text += f'{r["phone"]} - {error_short}\n'
        
        summary_text += '\n使用 /status 查看详情'
        
        await update.message.reply_text(summary_text)
    
    async def handle_changebind_input(self, update: Update):
        """处理换绑输入"""
        text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # 解析：账号ID 新手机号 API网址
        parts = text.split()
        
        if len(parts) < 3:
            await update.message.reply_text(
                '❌ 格式错误\n\n'
                '正确格式：\n'
                '账号ID 新手机号 API网址'
            )
            return
        
        try:
            account_id = int(parts[0])
            new_phone = normalize_phone(parts[1])
            api_url = parts[2]
        except ValueError:
            await update.message.reply_text('❌ 账号ID必须是数字')
            return
        
        # 清除状态
        if user_id in user_states:
            del user_states[user_id]
        
        # 获取账号信息
        account = self.db.get_account(account_id)
        
        if not account:
            await update.message.reply_text(f'❌ 账号ID #{account_id} 不存在')
            return
        
        if account['status'] != 'pending':
            await update.message.reply_text(
                f'❌ 账号状态错误\n\n'
                f'当前状态: {account["status"]}\n'
                f'只有 pending 状态的账号可以换绑'
            )
            return
        
        # 检查是否就绪
        import time
        now = int(time.time())
        if now < account['ready_time']:
            ready_dt = datetime.fromtimestamp(account['ready_time'])
            await update.message.reply_text(
                f'❌ 账号尚未就绪\n\n'
                f'就绪时间: {ready_dt.strftime("%m-%d %H:%M")}\n'
                f'还需等待: {(account["ready_time"] - now) // 3600} 小时'
            )
            return
        
        await update.message.reply_text(
            f'⏳ 开始换绑...\n\n'
            f'账号: {account["old_phone"]}\n'
            f'新手机号: {new_phone}\n'
            f'API: {api_url}\n\n'
            f'请稍候...'
        )
        
        # 执行换绑
        result = await self.binder.change_phone(
            account['session_file'],
            new_phone,
            api_url
        )
        
        if result['success']:
            # 更新数据库
            self.db.update_changebind(account_id, new_phone, api_url)
            
            await update.message.reply_text(
                f'✅ 换绑成功！\n\n'
                f'账号ID: #{account_id}\n'
                f'旧手机号: {result["old_phone"]}\n'
                f'新手机号: {result["new_phone"]}\n\n'
                f'🎉 换绑完成！'
            )
        else:
            # 更新失败状态
            self.db.update_status(account_id, 'failed', result['error'])
            
            await update.message.reply_text(
                f'❌ 换绑失败\n\n'
                f'错误: {result["error"]}'
            )
    
    async def start(self):
        """启动Bot"""
        print('='*60)
        print('🤖 TG换绑助手Bot启动')
        print('='*60)
        print(f'管理员ID: {Config.ADMIN_ID}')
        print('='*60)
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        # 保持运行
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print('\n⚠️ 正在关闭...')
    
    async def stop(self):
        """停止Bot"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

async def main():
    """主函数"""
    bot = ChangeBindBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())
