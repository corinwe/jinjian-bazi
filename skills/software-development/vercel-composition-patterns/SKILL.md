---
name: vercel-composition-patterns
description: Vercel官方React组件组合模式——组件组合、渲染属性、高阶组件、自定义Hook模式对比。来自vercel-labs/agent-skills
category: software-development
---

# Composition Patterns (Vercel官方组合模式)

## 概述

React组件组合模式——当使用组合而非继承时，选择正确的模式。

## 模式对比

### 1. 组件组合（推荐）
```tsx
function Panel({ header, children, footer }) {
  return (
    <div className="panel">
      <div className="panel-header">{header}</div>
      <div className="panel-body">{children}</div>
      <div className="panel-footer">{footer}</div>
    </div>
  );
}

// 使用
<Panel header={<h2>标题</h2>} footer={<Button>保存</Button>}>
  <p>内容...</p>
</Panel>
```

### 2. 自定义Hook（共享逻辑）
```tsx
function useWindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });
  useEffect(() => {
    function handleResize() {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    }
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return size;
}
```

### 3. Render Props（旧模式，尽量避免）
```tsx
// 较旧模式，大多数情况下自定义Hook更好
<DataFetcher url="/api/tasks">
  {({ data, loading }) => (
    loading ? <Spinner /> : <TaskList tasks={data} />
  )}
</DataFetcher>
```

## 黄金法则
- **组合** > 继承（始终如此）
- **自定义Hook** > HOC（高阶组件）用于共享逻辑
- **组件组合** > Render Props用于布局
- 模式服务于可读性和可维护性，而不是"正确性"
