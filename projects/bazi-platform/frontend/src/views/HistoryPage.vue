<template>
  <div class="history-page">
    <h2 class="page-title">📋 历史报告</h2>
    <p class="page-sub" v-if="username">欢迎，{{ username }}</p>

    <div v-if="loading" class="empty-state">
      <div class="spinner"></div>
      <p style="margin-top:12px">加载中...</p>
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <div class="icon">📭</div>
      <p>暂无历史报告</p>
      <router-link to="/" class="btn-primary" style="display:inline-flex;margin-top:12px">去排盘</router-link>
    </div>

    <div v-else class="history-list">
      <div v-for="item in list" :key="item.id" class="history-item" @click="viewReport(item)">
        <div class="hi-name">{{ item.name || '未命名' }}</div>
        <div class="hi-bazi">{{ item.bazi || '' }}</div>
        <div class="hi-meta">
          <span>{{ item.gender || '' }}</span>
          <span class="dot">·</span>
          <span>{{ item.created_at ? item.created_at.slice(0,10) : '' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHistory } from '../api/index.js'

export default {
  name: 'HistoryPage',
  data() {
    return { list: [], loading: true }
  },
  computed: {
    username() { return localStorage.getItem('username') || '' }
  },
  async mounted() {
    try {
      const res = await getHistory()
      this.list = res.analyses || []
    } catch (e) {
      this.list = []
    } finally {
      this.loading = false
    }
  },
  methods: {
    viewReport(item) {
      // Store the analysis data and navigate to report
      if (item.data) {
        sessionStorage.setItem('lastReport', JSON.stringify(item.data))
      }
      this.$router.push('/report')
    }
  }
}
</script>

<style scoped>
.history-page { padding-top: 16px; }
.page-title { font-size: 18px; color: var(--g); margin-bottom: 4px; }
.page-sub { font-size: 12px; color: var(--m); margin-bottom: 16px; }
.history-list { display: flex; flex-direction: column; gap: 8px; }
.history-item {
  background: var(--c); border-radius: 10px; padding: 14px 16px;
  cursor: pointer; transition: all 0.2s;
  border: 1px solid rgba(255,255,255,0.04);
}
.history-item:hover { border-color: rgba(201,168,76,0.3); transform: translateY(-1px); }
.hi-name { font-size: 15px; font-weight: 600; }
.hi-bazi { font-size: 13px; color: var(--g); margin-top: 2px; letter-spacing: 1px; }
.hi-meta { font-size: 11px; color: var(--m); margin-top: 4px; }
.hi-meta .dot { margin: 0 4px; }
</style>
