---
name: vercel-react-best-practices
description: Vercel官方React最佳实践——组件组合模式、性能优化、状态管理、代码分割、数据获取模式。来自vercel-labs/agent-skills(28.4K⭐)
category: software-development
---

# React Best Practices (Vercel官方)

## 概述

Vercel工程团队认证的React最佳实践。专注于性能、可维护性和生产可靠性。

## 组件模式

### 组合优于继承
```tsx
// 好：组合
<Card>
  <CardHeader>
    <CardTitle>用户信息</CardTitle>
  </CardHeader>
  <CardBody>
    <UserProfile user={user} />
  </CardBody>
</Card>

// 避免：深层prop传递
<Card title="用户信息" body={<UserProfile user={user} />} />
```

### 保持组件专注
- 一个组件 = 一个责任
- 如果组件做超过一件事，拆分它
- 组件应该可在不同上下文中复用

## 性能优化

### React.memo（明智地使用）
```tsx
// 仅在以下情况使用：
// 1. 组件渲染开销大
// 2. 同一组件的不同实例在相同props下渲染相同的东西
// 3. props是原始类型或通过useCallback/useMemo稳定引用

const TaskItem = React.memo(({ task, onToggle }: Props) => {
  return (
    <div onClick={() => onToggle(task.id)}>
      {task.title}
    </div>
  );
});
```

### useCallback和useMemo
```tsx
// useCallback：当函数作为props传递给memoized子组件时
const handleToggle = useCallback((id: string) => {
  setTasks(prev => prev.map(t => 
    t.id === id ? { ...t, done: !t.done } : t
  ));
}, []); // 没有依赖，因为setTasks使用函数形式

// useMemo：当计算开销大时
const sortedTasks = useMemo(() => 
  [...tasks].sort((a, b) => b.priority - a.priority),
  [tasks]
);
```

### 代码分割
```tsx
// 延迟加载路由组件
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

## 数据获取

### 使用SWR或React Query
```tsx
// SWR示例
const { data, error, isLoading } = useSWR('/api/tasks', fetcher);

if (isLoading) return <Skeleton />;
if (error) return <Error message="加载失败" />;
return <TaskList tasks={data} />;
```

### 在服务器上获取数据（Next.js）
```tsx
// 服务器组件内获取数据
async function TaskList() {
  const tasks = await db.tasks.findMany();
  return <ul>{tasks.map(t => <li key={t.id}>{t.title}</li>)}</ul>;
}
```

## 状态管理
- 本地状态 → useState
- 服务端状态 → SWR/React Query/TanStack Query
- 全局客户端状态 → Zustand（轻量）或 Context（简单场景）
- URL状态 → next/navigation useSearchParams
