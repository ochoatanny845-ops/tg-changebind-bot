# 🚀 创建GitHub仓库步骤

## 1. 在GitHub创建新仓库

访问: https://github.com/new

**仓库设置：**
- Repository name: `tg-changebind-bot`
- Description: `Telegram账号手机号更换自动化助手`
- Public / Private: 选择Private（如果不想公开）
- ❌ 不要勾选 "Initialize this repository with a README"

点击 "Create repository"

---

## 2. 关联本地仓库

复制GitHub显示的命令，或使用以下命令：

```bash
cd C:\Users\Administrator\.openclaw\workspace\tg-changebind-bot

# 添加远程仓库
git remote add origin https://github.com/你的用户名/tg-changebind-bot.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 3. 验证

访问仓库地址，应该能看到所有文件。

---

## 快速命令（替换你的用户名）

```bash
cd C:\Users\Administrator\.openclaw\workspace\tg-changebind-bot
git remote add origin https://github.com/YOUR_USERNAME/tg-changebind-bot.git
git branch -M main
git push -u origin main
```

**替换 `YOUR_USERNAME` 为你的GitHub用户名！**
