---
name: addy-testing-browser
description: 生产级浏览器测试——Chrome DevTools MCP进行实时运行时数据、DOM检查、控制台日志、网络追踪、性能分析。来自addyosmani/agent-skills
category: software-development
---

# Browser Testing with DevTools (生产级浏览器测试)

## 概述

使用Chrome DevTools协议进行实时浏览器测试。测试应该是确定性的、可重复的，并且测试真实的浏览器行为——不是模拟的。

## 你应该测试什么

### DOM交互
- 元素是否存在、可见、可交互
- 点击、悬停、表单输入、滚动
- 动画和转换
- 条件渲染

### 控制台
- 无错误（特别是生产构建）
- 警告有合理的理由
- 预期的日志消息输出

### 网络
- API调用成功（状态码2xx）
- 请求体/响应体正确
- 加载时序
- 缓存行为
- 错误处理（4xx/5xx）

### 性能
- 首次内容绘制（FCP）
- 最大内容绘制（LCP）
- 累计布局偏移（CLS）
- 交互到下次绘制（INP）
- 总阻塞时间（TBT）
- Core Web Vitals全部"良好"

## 测试策略

### E2E测试（关键用户流程）
```typescript
it('completes full checkout flow', async () => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('[data-testid="submit-order"]');
  await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
});
```

### 组件测试（单元）
隔离测试UI组件的行为和外观，不使用完整的浏览器环境。

### 视觉回归测试
在视觉差异时捕获截图并发出警报。关键页面和组件的基线截图。

## Playwright最佳实践
- 使用data-testid属性定位元素（而不是CSS选择器或文本）
- 使用定位器的可访问性标签
- 避免page.waitFor(timeout)——使用等待特定条件的定位器
- 并行运行测试（sharding）
- 在CI中使用追踪查看器进行调试
