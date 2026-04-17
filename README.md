# TG换绑助手Bot

Telegram账号手机号更换自动化助手

## 功能特性

- 🔄 自动化换绑流程
- 📱 支持批量换绑
- 🔐 自动获取验证码（通过API）
- 📊 换绑进度追踪
- 💬 Telegram交互式操作

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

### 运行

```bash
python bot.py
```

## 使用方法

1. 启动Bot并发送 `/start`
2. 发送 `/changebind` 开始换绑
3. 按提示输入新手机号或上传批量配置文件
4. 等待自动完成

## 架构

```
tg-changebind-bot/
├── bot.py              # Bot主程序
├── changebind.py       # 换绑核心逻辑
├── config.py           # 配置管理
├── api_helper.py       # API接码助手
├── database.py         # 数据库操作
├── requirements.txt    # 依赖列表
├── .env.example        # 配置示例
└── README.md           # 项目文档
```

## 配置说明

### 必需配置

- `BOT_TOKEN` - Telegram Bot Token
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `ADMIN_ID` - 管理员Telegram ID

### 可选配置

- `SMS_API_URL` - 短信接码API地址
- `DATABASE_PATH` - 数据库路径（默认：changebind.db）

## 开发计划

- [x] 项目初始化
- [ ] 单账号换绑功能
- [ ] 批量换绑功能
- [ ] API接码集成
- [ ] 进度追踪
- [ ] 日志记录
- [ ] 错误处理

## License

MIT
