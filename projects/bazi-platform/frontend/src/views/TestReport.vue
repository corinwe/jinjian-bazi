<template>
  <div class="report-page">
    <div class="report-toolbar">
      <router-link to="/" class="btn-outline">← 重新输入</router-link>
      <button class="btn-primary">📄 下载PDF</button>
    </div>
    <div class="empty-state">
      <p>暂无报告数据，请先输入生辰</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SimpleReport',
  data() { return { showRaw: false, expandedSec: 'sec3' } },
  computed: {
    report() {
      const raw = sessionStorage.getItem('lastReport')
      if (!raw) return null
      try { return JSON.parse(raw) } catch { return null }
    },
  },
}
</script>

<style scoped>
.report-page { padding: 20px; color: white; }
.empty-state { text-align: center; padding: 40px; }
</style>
