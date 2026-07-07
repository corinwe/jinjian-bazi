---
name: addy-code-simplify
description: 生产级代码简化——Chesterton栅栏原则、500法则、在保持精确行为的同时降低复杂度。来自addyosmani/agent-skills
category: software-development
---

# Code Simplification (生产级代码简化)

## 概述

让代码更简单而不改变行为。Chesterton栅栏原则——在理解为什么存在之前，不要移除看似多余的代码。500法则——如果一个文件超过500行，把它拆分成更小的模块。

## 核心原则

### Chesterton栅栏原则
在移除看起来不必要的代码之前，先理解它为什么存在。代码存在都是有原因的，即使原因不再有效。

### 500法则
```
< 200行  → 好
200-500行 → 可以接受
500-1000行 → 考虑拆分
> 1000行  → 必须拆分
```

### 降低复杂度
目标是减少阅读代码时必须同时考虑的概念数量。

## 简化模式

### 1. 提取函数
当一段代码需要注释来解释时，提取为一个函数：
```typescript
// 坏：需要注释解释
// 检查用户是否有权限编辑文档
const hasAccess = user.role === 'admin' || 
  (doc.ownerId === user.id && doc.status !== 'archived');

// 好：函数名本身就是解释
const hasAccess = canEditDocument(user, doc);
```

### 2. 合并条件
```typescript
// 坏：重复条件
if (user.age >= 18 && user.isVerified) { allowPurchase(); }
if (user.age >= 18 && user.isVerified) { allowBidding(); }

// 好：提取变量
const canParticipate = user.age >= 18 && user.isVerified;
if (canParticipate) { allowPurchase(); }
if (canParticipate) { allowBidding(); }
```

### 3. 减少嵌套
```typescript
// 坏：深层嵌套
function process(order) {
  if (order) {
    if (order.items.length > 0) {
      if (order.paymentStatus === 'paid') {
        // 处理...
      }
    }
  }
}

// 好：提前返回
function process(order) {
  if (!order) return;
  if (order.items.length === 0) return;
  if (order.paymentStatus !== 'paid') return;
  // 处理...
}
```

## 测量复杂度

| 指标 | 简单 | 中等 | 复杂 | 非常复杂 |
|------|------|------|------|---------|
| 每个函数的行数 | < 20 | 20-50 | 50-100 | > 100 |
| 圈复杂度 | < 5 | 5-10 | 10-20 | > 20 |
| 每个文件的参数 | < 3 | 3-5 | 5-7 | > 7 |
| 嵌套深度 | < 2 | 2-3 | 3-4 | > 4 |

## 反合理化

| 借口 | 反驳 |
|------|------|
| "以后会需要这种灵活性" | YAGNI——你不需要它 |
| "代码本身自文档化" | 好的命名有帮助，但不能替代清晰的逻辑 |
| "加上这个模式更好" | 模式是工具，不是目标 |
| "保持原样更安全" | 复杂度带来风险——简化更安全 |
