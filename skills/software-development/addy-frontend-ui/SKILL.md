---
name: addy-frontend-ui
description: 生产级前端UI工程——组件架构、设计系统、状态管理、响应式设计、WCAG 2.1 AA无障碍。避免AI审美，构建顶级公司的UI。来自addyosmani/agent-skills(67K⭐)
category: software-development
---

# Frontend UI Engineering (生产级前端UI工程)

## 概述

构建生产质量的用户界面——无障碍、高性能、视觉精致。目标是看起来像顶级公司设计意识的工程师构建的UI，不是AI生成的。

## 组件架构

### 文件结构

```
src/components/
  TaskList/
    TaskList.tsx          # 组件实现
    TaskList.test.tsx     # 测试
    TaskList.stories.tsx  # Storybook故事
    use-task-list.ts      # 自定义hook（复杂状态时）
    types.ts              # 组件特定类型
```

### 组件模式

**组合优于配置：**
```tsx
// 好：可组合
<Card>
  <CardHeader><CardTitle>Tasks</CardTitle></CardHeader>
  <CardBody><TaskList tasks={tasks} /></CardBody>
</Card>

// 避免：过度配置
<Card title="Tasks" headerVariant="large" bodyPadding="md" content={<TaskList />}/>
```

**分离数据获取与展示：**
```tsx
// Container: 处理数据
export function TaskListContainer() {
  const { tasks, isLoading, error } = useTasks();
  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="加载失败" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="暂无任务" />;
  return <TaskList tasks={tasks} />;
}

// Presentation: 处理渲染
export function TaskList({ tasks }) {
  return <ul role="list">{tasks.map(t => <TaskItem key={t.id} task={t} />)}</ul>;
}
```

## 状态管理选择

```
本地状态 (useState)           → 组件特定UI状态
提升状态                      → 2-3个兄弟组件共享
Context                       → 主题/认证/语言（读多写少）
URL状态 (searchParams)        → 筛选/分页/可分享UI状态
服务端状态 (React Query/SWR)  → 带缓存的远程数据
全局状态 (Zustand/Redux)      → 应用范围复杂客户端状态
```

**避免prop drilling超过3层。** 如果props穿过不使用的组件，引入context或重组组件树。

## 设计系统遵守

### 避免AI审美

| AI默认 | 问题 | 生产质量 |
|--------|------|---------|
| 紫色/靛蓝所有东西 | 所有应用看起来一样 | 使用项目的实际调色板 |
| 过度渐变 | 视觉噪音 | 扁平或微妙渐变 |
| 全圆角 (rounded-2xl) | 忽略角半径层次 | 设计系统一致的border-radius |
| 通用英雄区 | 模板驱动 | 内容优先的布局 |
| Lorem ipsum | 隐藏真实内容会暴露的布局问题 | 真实感占位内容 |
| 超大内边距 | 破坏视觉层次 | 一致的间距刻度 |
| 统一卡片网格 | 忽略信息优先级 | 目的驱动布局 |
| 重阴影设计 | 与内容竞争、低端设备渲染慢 | 设计系统指定的微妙或无阴影 |

### 间距和布局

使用一致的间距刻度。不要发明值：
```css
/* 好 */  padding: 1rem;     /* 16px */
/* 好 */  gap: 0.75rem;      /* 12px */
/* 坏 */  padding: 13px;     /* 不在任何刻度上 */
/* 坏 */  margin-top: 2.3rem;/* 不在任何刻度上 */
```

## 无障碍 (WCAG 2.1 AA)

### 键盘导航
每个交互元素必须可通过键盘访问：
```tsx
<button onClick={handleClick}>Click me</button>        // ✓ 默认可聚焦
<div onClick={handleClick}>Click me</div>               // ✗ 不可聚焦
```

### ARIA标签
```tsx
// 为缺乏可见文本的交互元素加标签
<button aria-label="关闭对话框"><XIcon /></button>
// 表单输入标签
<label htmlFor="email">邮箱</label>
<input id="email" type="email" />
```

### 关键无障碍检查
- 所有交互元素可通过键盘访问（Tab/Enter/Space）
- 颜色对比度≥4.5:1（普通文本）和≥3:1（大文本）
- 不要只靠颜色传达信息（同时使用图标/文字/模式）
- 表单输入有相关联的<label>
- 图片有alt文本
- 屏幕阅读器公告使用aria-live区域

## 响应式设计
- 移动优先CSS
- 使用CSS Grid / Flexbox进行布局
- 使用相对单位（rem/em/%）而非绝对（px）
- 关键的断点：320px（小手机）、768px（平板）、1024px（桌面）、1440px（大屏）
- 触摸目标至少44x44px

## 性能
- 代码分割（React.lazy, Suspense）
- 图片优化（next/image或响应式srcset）
- 虚拟列表用于长列表（react-window）
- 防抖/节流用于频繁事件
- 动画使用will-change和transform（GPU加速）
