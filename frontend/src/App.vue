<template>
  <div id="app-root">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">✦</span>
          <span class="logo-text">金鉴真人</span>
          <span class="logo-sub">八字命理</span>
        </router-link>
        <nav class="header-nav">
          <router-link to="/" class="nav-link" title="首页">🏠</router-link>
          <router-link to="/history" class="nav-link" title="历史记录" v-if="isLoggedIn">📋</router-link>
          <a v-if="isLoggedIn" class="nav-link" title="退出" @click="doLogout">🚪</a>
          <router-link v-else to="/login" class="nav-link" title="登录">👤</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>金鉴真人 · 以金为鉴，照见命理真相</p>
      <p class="footer-sub">确定性规则引擎驱动 · 零幻觉 · 全透明</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    }
  },
  methods: {
    doLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(13, 13, 26, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
}
.header-inner {
  max-width: 820px;
  margin: 0 auto;
  padding: 0 16px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}
.logo-icon { color: var(--g); font-size: 20px; }
.logo-text { font-size: 18px; font-weight: 700; color: var(--g); letter-spacing: 2px; }
.logo-sub { font-size: 11px; color: var(--m); font-weight: 400; margin-left: 4px; }
.header-nav { display: flex; gap: 4px; }
.nav-link {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 8px;
  font-size: 16px; cursor: pointer; text-decoration: none;
  transition: background 0.2s;
}
.nav-link:hover { background: rgba(255,255,255,0.06); }
.app-main {
  max-width: 820px; margin: 0 auto; padding: 0 16px 20px; min-height: calc(100vh - 140px);
}
.app-footer {
  text-align: center; padding: 20px 16px 32px;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.app-footer p { font-size: 12px; color: var(--m); margin: 0; }
.footer-sub { font-size: 10px; color: rgba(138, 128, 112, 0.5); margin-top: 4px; }
</style>
