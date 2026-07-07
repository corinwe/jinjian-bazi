---
name: addy-api-design
description: 生产级API与接口设计——契约优先、Hyrum法则、单版本规则、错误语义、边界验证。来自addyosmani/agent-skills
category: software-development
---

# API and Interface Design (生产级API设计)

## 概述

契约优先的设计方法——先定义接口，再实现。API是永久性的（Hyrum法则：一旦有人用你的API，你的API就是固定的）。单版本规则——维护向后兼容性而不是多版本。

## 核心原则

### 契约优先
在编写任何实现代码之前，定义API契约：
```typescript
// 先定义类型/接口
interface CreateTaskRequest {
  title: string;       // 必填，1-200字符
  description?: string; // 选填，0-2000字符
  dueDate?: string;     // ISO 8601日期
  priority: 'low' | 'medium' | 'high';
}

interface TaskResponse {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  dueDate: string | null;
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}
```

### Hyrum法则
一旦API被使用：
- 你不能改变已有的字段名或类型
- 你不能使已有的字段成为必填
- 你不能减少响应的数据
- 错误消息也是API的一部分（不要随意改变它们）

### 单版本规则
- 仅维护一个API版本
- 通过添加（而不是修改）来演进
- 旧的客户端仍然工作
- 对新行为使用新端点或新字段

## REST API设计

### URL结构
```
GET    /api/v1/tasks           # 列表任务
POST   /api/v1/tasks           # 创建任务
GET    /api/v1/tasks/:id       # 获取任务
PUT    /api/v1/tasks/:id       # 更新任务
DELETE /api/v1/tasks/:id       # 删除任务
```

### 响应格式
```json
// 成功
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}

// 错误
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "details": { "field": "title" }
  }
}
```

### 分页
```json
GET /api/v1/tasks?page=1&limit=20
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

## 错误处理

### 错误类别
| HTTP状态码 | 意思 | 使用场景 |
|-----------|------|---------|
| 400 | Bad Request | 验证失败 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 未授权 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（重复创建） |
| 422 | Unprocessable | 语义错误 |
| 429 | Too Many Requests | 速率限制 |
| 500 | Internal Server Error | 服务器错误 |

### 边界验证
- 所有输入在边界处验证
- 验证错误有清晰的消息
- 输入长度和类型限制
- 枚举值验证
- 业务规则验证

## 接口设计清单
- [ ] 契约是否在实现之前定义？
- [ ] API是否有清晰的所有权和边界？
- [ ] 默认值是否有意义？
- [ ] 错误消息是否有帮助？
- [ ] 分页和过滤是否支持？
- [ ] 速率限制和认证是否到位？
- [ ] API是否遵守单版本规则？
