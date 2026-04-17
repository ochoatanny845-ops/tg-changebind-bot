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
  - **推荐使用 Android 官方**: `API_ID=6`, `API_HASH=eb06d4abfb49dc3eeb1aeb98ae0f581e`
  - iOS 官方: `API_ID=1`（不推荐，API_HASH不公开）
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

**单个账号：**
```
+972555509621 https://logincode.add4533.com/?token=xxx
```

**批量登录（每行一个）：**
```
+972555509621 https://logincode.add4533.com/?token=xxx
+55119107476 https://tgapi88880.duckdns.org/verify/yyy
+8613800138000 https://logincode.add4533.com/?token=zzz
```

**或上传TXT文件：**
```
每行一个账号，格式同上
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

### 5. 配置代理（推荐 - IPDeep 一次一换）

**IPDeep 代理配置（一次一换模式）**

创建 `proxy.txt` 文件：

```
# 基础模式（一次一换，不限国家）
gate.ipdeep.com:8082:d1561533000-res-session-{random}-sessiontime-0:Qqesi3rN

# 国家限制模式（一次一换 + 自动匹配国家）
gate.ipdeep.com:8082:d1561533000-res-country-{country}-session-{random}-sessiontime-0:Qqesi3rN
```

**模板变量说明：**
- `{random}` - 自动生成随机数（10000-9999999999）
- `{country}` - 根据手机号自动替换国家代码（br/il/cn等）
- `sessiontime-0` - IP时长为0（一次一换）

**生成示例：**
```
登录 +55119107476 (巴西)
→ gate.ipdeep.com:8082:d1561533000-res-country-br-session-8472635-sessiontime-0:Qqesi3rN

登录 +972555509621 (以色列)
→ gate.ipdeep.com:8082:d1561533000-res-country-il-session-9138264-sessiontime-0:Qqesi3rN

每次操作使用新的随机数 → 每次都是新IP（一次一换）
```

**如需粘性IP（例如10分钟不变）：**
```
gate.ipdeep.com:8082:d1561533000-res-session-{random}-sessiontime-10:Qqesi3rN
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
- `PROXY_FILE` - 代理文件路径（默认：proxy.txt）

### 代理配置（推荐 - 按国家自动匹配）

**新格式（推荐）：按国家分类**

```
# 格式：国家代码|代理URL
# 国家代码 = 手机号国际区号（去掉+号）

# 全局代理（备用）
global|socks5://127.0.0.1:10808
global|http://127.0.0.1:7890

# 以色列 (+972)
972|socks5://il-proxy1.example.com:1080
972|socks5://il-proxy2.example.com:1080

# 巴西 (+55)
55|socks5://br-proxy.example.com:1080

# 中国 (+86)
86|socks5://cn-proxy.example.com:1080

# 美国/加拿大 (+1)
1|socks5://us-proxy.example.com:1080

# 俄罗斯/哈萨克斯坦 (+7)
7|socks5://ru-proxy.example.com:1080
```

**自动匹配规则：**
- 登录 `+972555509621` → 自动使用 `972` 代理
- 登录 `+8613800138000` → 自动使用 `86` 代理
- 换绑到 `+5511910747` → 自动使用 `55` 代理
- 没有匹配时 → 使用 `global` 代理

**旧格式兼容：**
```
# 不加国家代码，直接写代理（会当作全局代理）
socks5://127.0.0.1:1080
http://127.0.0.1:7890
```

**优势：**
- 🔒 隐藏真实IP
- 🌍 **自动匹配手机号所属国家的代理**
- 🎲 同一国家多个代理随机选择
- ⚡ 降低被封风险
- 📍 符合地理位置一致性（降低风控）

**如果没有代理：**
- 程序仍可正常运行
- 使用本地直连
- 风控风险稍高

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
