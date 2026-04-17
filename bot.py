"""
TG换绑助手Bot - 主程序
"""
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config

# 用户状态
user_states = {}

class ChangeBindBot:
    """换绑助手Bot"""
    
    def __init__(self):
        # 验证配置
        Config.validate()
        
        # 创建应用
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # 设置处理器
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置处理器"""
        self.app.add_handler(CommandHandler('start', self.cmd_start))
        self.app.add_handler(CommandHandler('changebind', self.cmd_changebind))
        self.app.add_handler(CommandHandler('help', self.cmd_help))
        self.app.add_handler(CommandHandler('cancel', self.cmd_cancel))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """启动命令"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限。本Bot仅供管理员使用。')
            return
        
        await update.message.reply_text(
            '👋 欢迎使用TG换绑助手！\n\n'
            '📱 功能：\n'
            '/changebind - 更换账号手机号\n'
            '/help - 查看帮助\n'
            '/cancel - 取消当前操作\n\n'
            '💡 提示：支持单个和批量换绑'
        )
    
    async def cmd_changebind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """换绑命令"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        user_states[user_id] = {'step': 'waiting_account'}
        
        await update.message.reply_text(
            '📱 请输入账号信息\n\n'
            '格式：\n'
            '旧手机号 新手机号 API链接\n\n'
            '示例：\n'
            '+8613800138000 +8613900139000 https://api.example.com/xxx\n\n'
            '发送 /cancel 取消'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """帮助命令"""
        await update.message.reply_text(
            '📖 使用帮助\n\n'
            '1️⃣ 发送 /changebind 开始换绑\n'
            '2️⃣ 输入：旧手机号 新手机号 API链接\n'
            '3️⃣ 等待自动完成\n\n'
            '💡 API链接用于自动获取验证码'
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
        
        if step == 'waiting_account':
            await self.handle_account_input(update, state)
    
    async def handle_account_input(self, update: Update, state):
        """处理账号输入"""
        text = update.message.text.strip()
        
        # TODO: 解析账号信息
        # TODO: 调用换绑逻辑
        
        await update.message.reply_text(
            '⚠️ 功能开发中...\n\n'
            f'收到输入：{text}'
        )
        
        # 清除状态
        user_id = update.effective_user.id
        if user_id in user_states:
            del user_states[user_id]
    
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
