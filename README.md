# TG换绑助手Bot

Telegram账号手机号更换自动化助手

## ✨ 功能特性

- 🔄 自动化换绑流程（24小时冷却期）
- 📱 支持批量换绑
- 🔐 自动获取验证码（通过API）
- 📊 换绑进度追踪
- 💬 Telegram交互式操作
- 🎲 随机设备型号（降低风控）

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

必需配置：
- `BOT_TOKEN` - Telegram Bot Token（从@BotFather获取）
- `API_ID` - Telegram API ID（从 https://my.telegram.org 获取）
- `API_HASH` - Telegram API Hash
- `ADMIN_ID` - 管理员Telegram ID

### 运行

```bash
python bot.py
```

## 📖 使用方法

### 1. 登录账号到新设备

```
/login
```

输入格式：
```
手机号 API网址
```

示例：
```
+972555509621 https://logincode.add4533.com/?token=xxx
551191074765 https://tgapi88880.duckdns.org/verify/xxx
```

💡 如果手机号没有+号，会自动添加

### 2. 等待24小时

使用 `/status` 查看就绪状态

### 3. 执行换绑

```
/changebind
```

输入格式：
```
账号ID 新手机号 API网址
```

示例：
```
1 +8613900139000 https://logincode.add4533.com/?token=xxx
```

### 4. 查看状态

```
/status  # 查看统计
/list    # 查看详细列表
```

## 🏗️ 架构

```
tg-changebind-bot/
├── bot.py              # Bot主程序（Telegram交互）
├── changebind.py       # 换绑核心逻辑（Telethon）
├── sms_adapter.py      # 接码适配器（支持多平台）
├── database.py         # 数据库操作（SQLite）
├── config.py           # 配置管理
├── requirements.txt    # 依赖列表
├── .env.example        # 配置示例
└── README.md           # 项目文档
```

## 🔄 工作流程

```
1. /login 登录账号
   ├─ 使用Telethon模拟设备登录
   ├─ 通过接码API获取登录验证码
   ├─ 保存Session文件
   └─ 记录登录时间

2. 等待24小时
   ├─ 数据库记录状态：pending
   ├─ 24小时后自动变为：ready
   └─ 使用 /status 查看

3. /changebind 换绑
   ├─ 调用Telegram换绑API
   ├─ 通过接码API获取验证码
   ├─ 提交验证码完成换绑
   └─ 状态变更为：completed

4. 完成
   └─ 数据库记录新旧手机号
```

## 📊 支持的接码平台

- ✅ logincode.add4533.com
- ✅ tgapi88880.duckdns.org
- ✅ 其他平台（通用HTML解析）

## ⚙️ 配置说明

### 必需配置

- `BOT_TOKEN` - Telegram Bot Token
- `API_ID` - Telegram API ID（数字）
- `API_HASH` - Telegram API Hash
- `ADMIN_ID` - 管理员Telegram ID（数字）

### 可选配置

- `DATABASE_PATH` - 数据库路径（默认：changebind.db）

## 🔐 安全说明

### 24小时等待期

- ✅ 符合Telegram安全策略
- ✅ 降低风控风险
- ✅ 新设备登录后等待，让Telegram认为是"正常迁移"

### 设备指纹

- 🎲 随机选择设备型号（Samsung/iPhone/Xiaomi等）
- ✅ 降低批量操作特征

### Session文件

- 💾 保存在 `sessions/` 目录
- 🔐 包含登录凭证，请妥善保管

## 📋 命令列表

| 命令 | 功能 |
|------|------|
| `/start` | 查看欢迎信息 |
| `/login` | 登录账号到新设备 |
| `/status` | 查看账号统计 |
| `/list` | 列出所有账号详情 |
| `/changebind` | 执行换绑 |
| `/help` | 查看帮助 |
| `/cancel` | 取消当前操作 |

## 🚨 常见问题

### Q: 为什么要等24小时？

A: Telegram规定新设备登录后24小时内无法更换手机号，这是安全机制。

### Q: 换绑失败怎么办？

A: 查看错误信息，常见原因：
- 验证码过期/错误
- 新手机号已被使用
- Session失效

### Q: 支持批量换绑吗？

A: 目前支持单个操作，批量功能将在后续版本添加。

## 📈 开发计划

- [x] 单账号登录
- [x] 24小时等待机制
- [x] 单账号换绑
- [x] 接码API集成（支持多平台）
- [x] 数据库持久化
- [x] 错误处理
- [ ] 批量登录/换绑
- [ ] 定时任务（自动换绑ready状态的账号）
- [ ] Webhook通知
- [ ] Web管理界面

## License

MIT
