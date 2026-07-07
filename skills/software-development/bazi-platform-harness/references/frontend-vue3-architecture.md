# 金鉴真人·前端Vue3+Vite架构参考

> 创建时间：2026-06-27  
> 用途：下次前端开发/修改时的快速参考

## 技术栈

| 层 | 技术 |
|:---|:-----|
| 框架 | Vue 3 (Composition API + Options API混合) |
| 构建 | Vite 8 |
| 路由 | vue-router 4 (hash模式) |
| 渲染 | 原生DOM操作（无UI框架） |
| PDF | html2canvas + jsPDF |
| 样式 | 全局CSS变量 + scoped样式 |
| API | fetch (无axios) |

## 项目结构

```
frontend/
├── index.html              # 入口HTML
├── vite.config.js          # Vite配置（含API代理）
├── src/
│   ├── main.js             # Vue应用入口
│   ├── App.vue             # 主布局（header/footer/router-view）
│   ├── assets/
│   │   └── main.css        # 全局品牌CSS（暗金配色）
│   ├── router/
│   │   └── index.js        # 路由定义（含导航守卫）
│   ├── api/
│   │   └── index.js        # 所有API调用封装
│   ├── views/
│   │   ├── InputPage.vue   # 输入表单页（首页）
│   │   ├── ReportPage.vue  # 报告展示页（21§ + PDF）
│   │   ├── LoginPage.vue   # 登录/注册页
│   │   └── HistoryPage.vue # 历史记录页
│   └── components/
│       └── NatureText.vue  # 日主性格描述文字组件
```

## 路由

| 路径 | 视图 | 说明 |
|:-----|:-----|:------|
| `#/` | InputPage | 首页·输入生辰 |
| `#/report` | ReportPage | 报告展示（从sessionStorage取数据） |
| `#/login` | LoginPage | 登录（支持切换到注册） |
| `#/register` | LoginPage | 注册（相同组件，isRegister=true） |
| `#/history` | HistoryPage | 历史记录（需登录） |

## 品牌配色

| 变量 | 值 | 用途 |
|:-----|:---|:------|
| `--g` | `#c9a84c` | 金色主色 · 标题/高亮 |
| `--g-light` | `#e8d48b` | 金色亮色 |
| `--g-dark` | `#a08030` | 金色暗色 · 按钮渐变 |
| `--d` | `#1a1a2e` | 深蓝 · 按钮文字 |
| `--c` | `#252542` | 卡片背景 |
| `--t` | `#e8e0d0` | 主文字 |
| `--m` | `#8a8070` | 辅助文字 |
| `--b` | `#0d0d1a` | 页面背景 |
| `--a` | `#c0392b` | 警示红 |

## API通信模式

```javascript
// 1. 无认证请求
import { analyzeRequest } from '../api/index.js'
const result = await analyzeRequest({ name, gender, birth_year, ... })

// 2. 有认证请求（token自动从localStorage取）
import { getHistory, saveAnalysis } from '../api/index.js'
const history = await getHistory()
// Token通过Authorization header传递
```

## 数据流

```
用户输入 → InputPage表单 → analyzeRequest(API) 
  → FastAPI → 规则引擎 → 数据返回
  → sessionStorage.setItem('lastReport', JSON.stringify(data))
  → $router.push('/report')
  → ReportPage从sessionStorage读取并渲染
  → 如已登录：同时POST /api/v1/analyses保存
```

## PDF生成流程

```javascript
// ReportPage.vue — doDownloadPDF()
import('html2canvas').then(html2canvas => {
  import('jspdf').then(({ jsPDF }) => {
    const el = this.$refs.reportContent
    html2canvas(el, { scale: 2, backgroundColor: '#0d0d1a' })
      .then(canvas => {
        const pdf = new jsPDF('p', 'mm', 'a4')
        // 多页处理（支持超长报告）
        pdf.save(`${name}_八字命理报告.pdf`)
      })
  })
})
```

## 关键注意事项

1. **Vue Router用hash模式**（`createWebHashHistory`）— 不需要服务器端路由配置
2. **报告数据存sessionStorage** — 页面刷新会丢失，但登录用户可通过历史记录找回
3. **认证token存localStorage** — 30天有效期，logout时清除
4. **导航守卫** — `/history` 路由需要token，无则跳转`/login`
5. **构建输出** — `npm run build` → `frontend/dist/`，FastAPI自动服务