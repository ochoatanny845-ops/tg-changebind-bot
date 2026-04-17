# 使用真实设备登录（可选）

如果你有配对的Android/iOS设备（OpenClaw Nodes），可以用真实设备登录。

## 方案1: Telethon模拟设备（当前实现）

**优点：**
- ✅ 不需要真实设备
- ✅ 可批量操作
- ✅ 成本低

**缺点：**
- ⚠️ 风控风险稍高（但设置得当也很安全）

---

## 方案2: 使用真实Android/iOS设备

### 通过OpenClaw Nodes

**前提：**
- 已配对Android/iOS手机到OpenClaw

**实现方式：**

```python
# 使用nodes工具在真实手机上登录
from nodes import nodes

# 在Android手机上执行登录
result = await nodes(
    action='run',
    node='android-phone-1',
    command=['am', 'start', '-a', 'android.intent.action.VIEW', 
             '-d', f'tg://login?phone={phone}']
)
```

### 通过ADB（Android）

**前提：**
- 手机开启USB调试
- 电脑安装ADB

**步骤：**

```bash
# 1. 连接手机
adb devices

# 2. 安装Telegram
adb install telegram.apk

# 3. 启动Telegram并输入验证码（手动）
adb shell am start -n org.telegram.messenger/.MainActivity
```

---

## 推荐方案

**当前的Telethon模拟设备方案已经足够好！**

理由：
1. ✅ Telegram无法区分模拟设备和真实设备（只看设备参数）
2. ✅ 24小时等待期同样生效
3. ✅ 批量操作更方便
4. ✅ 随机设备型号降低批量特征

**只要设备参数设置合理，风控风险极低。**

---

## 何时需要真实设备？

**只有在以下情况才需要：**

1. 账号已被Telegram标记为"高风险"
2. 需要通过人机验证（滑块、图片识别等）
3. 大规模批量操作（> 100个账号/天）

**对于正常换绑需求，Telethon模拟设备完全够用。**
