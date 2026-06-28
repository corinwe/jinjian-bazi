import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'input', component: () => import('../views/InputPage.vue') },
  { path: '/report', name: 'report', component: () => import('../views/ReportPage.vue') },
  { path: '/login', name: 'login', component: () => import('../views/LoginPage.vue') },
  { path: '/register', name: 'register', component: () => import('../views/LoginPage.vue') },
  { path: '/history', name: 'history', component: () => import('../views/HistoryPage.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// Navigation guard: check auth for /history
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name === 'history' && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
