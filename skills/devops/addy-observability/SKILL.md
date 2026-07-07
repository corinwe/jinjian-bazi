---
name: addy-observability
description: 生产级可观测性与仪表化——结构化日志、RED指标、OpenTelemetry追踪、症状告警、边构建边仪表化。来自addyosmani/agent-skills
category: devops
---

# Observability and Instrumentation (生产级可观测性)

## 概述

边构建边仪表化——在写代码的同时添加日志、指标和追踪。在生产中运行的每个服务都必须可观测。

## 三大支柱

### 1. 日志（结构化）
```json
// 好：结构化JSON日志
{
  "level": "error",
  "message": "支付处理失败",
  "service": "payment-service",
  "traceId": "abc123",
  "userId": "user_456",
  "error": {
    "type": "payment_declined",
    "code": "insufficient_funds"
  },
  "duration": 245,
  "timestamp": "2026-06-26T10:30:00Z"
}

// 坏：非结构化文本
// [ERROR] 支付失败
```

### 2. 指标（RED方法）
```
Rate    → 每秒请求数
Errors  → 失败的请求数
Duration → 请求持续时间（p50, p95, p99）
```

### 3. 追踪（OpenTelemetry）
- 每个请求有一个traceId
- 跨服务传播
- 可视化请求的完整路径

## 什么需要仪表化

### 每个API端点
```typescript
// 在中间件中自动仪表化
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    logger.info({
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: Date.now() - start,
      traceId: req.headers['x-trace-id']
    });
  });
  next();
});
```

### 数据库查询
- 查询持续时间
- 受影响行数
- 慢查询日志

### 外部服务调用
- 出站HTTP请求
- 响应时间
- 错误和重试

## 告警

### 症状告警（而不是原因告警）
```
✅ 好：错误率 > 1%（症状——用户受到影响）
❌ 坏：CPU > 80%（原因——用户不一定受影响）
```

### 告警级别
| 级别 | 响应时间 | 例子 |
|------|---------|------|
| P0 | 立即 | 服务宕机、数据丢失 |
| P1 | 15分钟 | 高错误率、关键功能中断 |
| P2 | 1小时 | 非关键功能降级 |
| P3 | 下一个工作日 | 小缺陷、性能微降 |

## 预发门禁

在部署之前确认：
- [ ] 所有端点有日志
- [ ] RED指标已设置
- [ ] 关键告警已创建
- [ ] 仪表盘已准备
- [ ] 日志有足够的上下文（traceId、userId等）
