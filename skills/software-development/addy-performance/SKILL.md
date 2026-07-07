---
name: addy-performance
description: 生产级性能优化——先测量、Core Web Vitals目标、分析工作流、打包分析、反模式检测。来自addyosmani/agent-skills
category: software-development
---

# Performance Optimization (生产级性能优化)

## 概述

先测量再优化。没有数据的性能优化是猜测。Core Web Vitals是标准——FCP < 1.8s, LCP < 2.5s, CLS < 0.1, INP < 200ms。

## 测量优先

### 1. 建立基线
优化前先测量当前性能：
```
Lighthouse分数:
- Performance: 75
- LCP: 3.2s
- TBT: 450ms
- CLS: 0.15
```

### 2. 定义目标
```
目标:
- Performance: ≥ 90
- LCP: < 2.0s
- TBT: < 200ms
- CLS: < 0.1
```

### 3. 优化
一次改变一个变量——测量每次更改的影响。

### 4. 验证
再次测量确认改进。如果目标没有达到，返回步骤2或3。

## Core Web Vitals

| 指标 | 良好 | 需要改善 | 差 |
|------|------|---------|----|
| LCP | < 2.5s | 2.5s - 4.0s | > 4.0s |
| FID/INP | < 200ms | 200ms - 500ms | > 500ms |
| CLS | < 0.1 | 0.1 - 0.25 | > 0.25 |
| FCP | < 1.8s | 1.8s - 3.0s | > 3.0s |
| TBT | < 200ms | 200ms - 600ms | > 600ms |

## 前端优化

### JavaScript
- 代码分割（React.lazy + Suspense）
- 摇树优化
- 延迟加载非关键脚本
- 消除未使用的依赖
- 使用轻量级替代方案（date-fns vs moment）

### 图片
- 使用现代格式（webp/avif）
- 响应式图片（srcset）
- 懒加载（loading="lazy"）
- 适当的尺寸——不要使用3000px图片做缩略图
- 使用图片CDN

### CSS
- 消除未使用的CSS（PurgeCSS）
- 关键CSS内联
- CSS contain用于隔离布局
- 使用content-visibility

### 字体
- 使用font-display: swap
- 子集化字体
- 使用可变字体
- 预加载关键字体

## 后端优化

### API
- 响应压缩（gzip/brotli）
- 分页（绝不返回无限制列表）
- 数据库查询优化（N+1查询检测）
- 缓存（Redis/CDN）
- 批处理

### 数据库
- 适当的索引
- 查询优化（EXPLAIN ANALYZE）
- 连接池
- 读取副本用于读取密集型工作负载
