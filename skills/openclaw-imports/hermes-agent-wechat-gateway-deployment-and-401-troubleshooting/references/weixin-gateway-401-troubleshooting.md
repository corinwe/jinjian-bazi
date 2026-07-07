# 微信网关 401 认证错误排查指南

## 问题现象
微信消息可以接收，但发送回复时出现 `HTTP 401: Missing Authentication header`。

## 排查步骤

### 1. 检查 token 存储格式
凭证文件 `/root/.hermes/weixin_accounts.json` 中的 token 格式应为：`account_id:hex_characters`

### 2. 直接调用 iLink API 验证 token 有效性
```bash
curl -X POST "https://ilinkai.weixin.qq.com/ilink/bot/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <完整token值>" \
  -d '{"to_wxid":"目标用户wxid","content":"测试消息"}'
```
如果返回 Status 200，说明 token 有效。

### 3. 清理旧凭证文件
- 删除 `/root/.hermes/context-tokens.json`（可能包含旧 bot 账号的上下文 token）
- 重新执行 `hermes gateway setup` 扫码登录获取新凭证

### 4. 区分 WeixinAdapter.send 与 gateway.run 的发送行为
- 直接调用 `WeixinAdapter.send` 发送成功 → token 和 adapter 本身没问题
- 通过 `gateway.run` 发送失败 → 问题出在 gateway 层的 token 传递或 session 使用

### 5. 添加调试 patch
在 `weixin.py` 中添加日志，打印每次 `_api_post` 的 token 值，定位 token 在 gateway 层是否被正确传递。

## 注意事项
- `get_updates` 轮询超时（15秒）是微信 iLink API 的 long polling 正常行为，不影响发送功能
- 确保 `.env` 中 `WEIXIN_TOKEN` 的值与 `weixin_accounts.json` 中的 token 完全一致