# 接码平台说明

## 支持的平台

### 1. tgapi88880.duckdns.org（SSE实时推送）
- ✅ 自动获取验证码
- ✅ 实时推送，无需轮询
- 🔒 连接SSE stream endpoint

### 2. logincode.add4533.com（JavaScript动态加载）
- ⚠️ 需要API支持
- ⚠️ 如果API不存在，需要手动输入验证码
- 建议切换到支持API的平台

## 推荐平台

**优先使用 tgapi88880.duckdns.org**
- 实时推送
- 稳定可靠
- 完全自动化

## 如果logincode无法自动获取

**方案1: 切换平台**
使用 tgapi88880.duckdns.org

**方案2: 手动输入验证码（待实现）**
程序检测到无法自动获取时，会提示手动输入

## API要求

接码平台需要提供以下之一：
1. SSE stream endpoint（实时推送）
2. REST API endpoint（轮询查询）
3. 在HTML中直接显示验证码

**logincode.add4533.com 使用Vue.js动态渲染，需要联系平台提供API。**
