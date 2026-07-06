<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-icon">✦</div>
      <h2>{{ isRegister ? '注册账号' : '登录' }}</h2>
      <p class="login-sub">{{ isRegister ? '创建账号，保存您的命理报告' : '登录后查看历史分析报告' }}</p>

      <div class="form-group">
        <label>用户名</label>
        <input class="form-input" v-model="username" placeholder="请输入用户名" @keyup.enter="submit">
      </div>
      <div class="form-group">
        <label>密码</label>
        <input class="form-input" type="password" v-model="password" placeholder="请输入密码" @keyup.enter="submit">
      </div>

      <button class="btn-gold" :disabled="loading" @click="submit">
        {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
      </button>

      <div class="login-switch">
        <span v-if="isRegister">已有账号？</span>
        <span v-else>没有账号？</span>
        <a href="#" @click.prevent="isRegister = !isRegister">
          {{ isRegister ? '去登录' : '去注册' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { login, register } from '../api/index.js'

export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      isRegister: this.$route.name === 'register',
    }
  },
  methods: {
    showToast(msg, type='info') {
      const c = document.querySelector('.toast-container') || (()=>{const d=document.createElement('div');d.className='toast-container';document.body.appendChild(d);return d})()
      const t=document.createElement('div');t.className=`toast ${type}`;t.textContent=msg
      c.appendChild(t);setTimeout(()=>{t.style.opacity='0';t.style.transition='opacity 0.3s';setTimeout(()=>t.remove(),300)},2500)
    },
    async submit() {
      if (!this.username.trim() || !this.password.trim()) {
        this.showToast('请填写用户名和密码', 'error'); return
      }
      this.loading = true
      try {
        if (this.isRegister) {
          await register(this.username.trim(), this.password.trim())
          this.showToast('注册成功，请登录', 'success')
          this.isRegister = false
          this.password = ''
        } else {
          const res = await login(this.username.trim(), this.password.trim())
          localStorage.setItem('token', res.token)
          localStorage.setItem('username', this.username.trim())
          this.showToast('登录成功', 'success')
          setTimeout(() => this.$router.push('/'), 500)
        }
      } catch (e) {
        this.showToast(e.message || '操作失败', 'error')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-page { display:flex; justify-content:center; padding-top:48px; }
.login-card {
  width:100%; max-width:380px; background:var(--c); border-radius:14px;
  padding:32px 28px; text-align:center;
  border:1px solid rgba(255,255,255,0.04);
}
.login-icon { font-size:32px; color:var(--g); margin-bottom:8px; }
h2 { font-size:20px; color:var(--g); margin-bottom:4px; }
.login-sub { font-size:12px; color:var(--m); margin-bottom:20px; }
.form-group { text-align:left; margin-bottom:14px; }
.form-group label { font-size:12px; color:var(--m); margin-bottom:4px; display:block; }
.login-switch { margin-top:14px; font-size:13px; color:var(--m); }
.login-switch a { color:var(--g); }
</style>
