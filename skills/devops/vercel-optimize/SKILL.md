---
name: vercel-optimize
description: Vercel官方性能优化——Core Web Vitals优化、图片优化、ISR/SSR/SSG策略、数据缓存、边缘函数。来自vercel-labs/agent-skills
category: devops
---

# Vercel Optimize (Vercel官方性能优化)

## 概述

Vercel平台特有的性能优化策略。涵盖渲染策略选择、图片优化、缓存策略和边缘计算。

## 渲染策略选择

| 策略 | 使用场景 | 性能特征 |
|------|---------|---------|
| **SSG** (静态生成) | 内容不经常变化（博客、文档） | 最快——CDN提供 |
| **ISR** (增量静态再生) | 内容定期更新（产品目录） | 快——CDN提供，后台重新生成 |
| **SSR** (服务端渲染) | 个性化内容（仪表板、用户配置） | 中等——每次请求生成 |
| **CSR** (客户端渲染) | 高度交互的体验（仪表板） | 客户端生成 |
| **Edge Functions** | 低延迟全球响应 | 边缘网络执行 |

### 选择指南
```
内容是公开的且很少变化? → SSG
内容定期更新? → ISR（revalidate时间）
内容是个性化的但需要SEO? → SSR
内容是个性化的不需要SEO? → CSR
需要极低延迟的数据转换? → Edge Functions
```

## 图片优化

```tsx
// Next.js Image组件
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // 首屏图片使用priority
  placeholder="blur" // 占位符
/>
```

## 数据缓存

```typescript
// fetch缓存（Next.js App Router）
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 } // 每小时重新验证
});

// 不稳定缓存
import { unstable_cache } from 'next/cache';

const getCachedData = unstable_cache(
  async () => {
    return await db.query('SELECT * FROM tasks');
  },
  ['tasks'],
  { revalidate: 3600 }
);
```

## 边缘配置

```typescript
// 边缘函数配置
export const config = {
  runtime: 'edge',
  regions: ['iad1', 'hkg1', 'gru1'], // 部署区域
};

export default async function handler(req: Request) {
  // 在边缘运行——接近用户
  return new Response(JSON.stringify({ hello: 'world' }), {
    headers: { 'content-type': 'application/json' },
  });
}
```
