<template>
  <div class="input-page">
    <!-- 品牌标语 -->
    <div class="hero">
      <div class="hero-icon">✦</div>
      <h1>金鉴真人</h1>
      <p class="hero-sub">输入生辰，洞察命运轨迹</p>
    </div>

    <!-- 输入卡片 -->
    <div class="card input-card">
      <div class="card-title">📝 输入出生信息</div>

      <div class="form-row">
        <div class="form-group" style="flex:1">
          <label>姓名</label>
          <input class="form-input" v-model="form.name" placeholder="请输入您的姓名" maxlength="20">
        </div>
        <div class="form-group" style="width:100px">
          <label>性别</label>
          <div class="option-group">
            <div class="option-item" :class="{active:form.gender==='男'}" @click="form.gender='男'">男</div>
            <div class="option-item" :class="{active:form.gender==='女'}" @click="form.gender='女'">女</div>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group" style="flex:1">
          <label>出生日期</label>
          <input class="form-input" type="date" v-model="form.date">
        </div>
        <div class="form-group" style="width:130px">
          <label>日历类型</label>
          <div class="option-group">
            <div class="option-item" :class="{active:form.calendar==='solar'}" @click="form.calendar='solar'">阳历</div>
            <div class="option-item" :class="{active:form.calendar==='lunar'}" @click="form.calendar='lunar'">农历</div>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group" style="flex:1">
          <label>出生时辰</label>
          <select class="form-select" v-model="form.hour">
            <option v-for="s in shichen" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </div>
        <div class="form-group" style="flex:1">
          <label>出生地点 <span class="optional">(可选)</span></label>
          <input class="form-input" v-model="form.birthplace" placeholder="如：北京，默认东八区">
        </div>
      </div>

      <div style="margin-top:6px">
        <button class="btn-gold" :disabled="loading" @click="doAnalyze">
          <span v-if="loading" class="spinner" style="width:18px;height:18px;border-width:2px"></span>
          <span v-else>✦ 开始排盘</span>
          <span v-if="loading"> 分析中...</span>
        </button>
      </div>

      <!-- 快捷样本 -->
      <div class="samples">
        <span @click="fillSample('家主','1979-07-15','solar',4,'男','')">📌 家主</span>
        <span @click="fillSample('子源','2011-04-25','solar',10,'男','')">📌 子源</span>
        <span @click="fillSample('测试','1990-08-15','solar',6,'女','')">📌 示例</span>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="card" style="margin-top:12px;opacity:0.6">
      <div class="card-title" style="font-size:13px">💡 关于金鉴真人</div>
      <div style="font-size:12px;line-height:1.8;color:var(--m)">
        <p>金鉴真人八字命理分析基于<strong style="color:var(--t)">确定性规则引擎</strong>驱动，所有计算由命理规则逐条执行，无AI幻觉。</p>
        <p style="margin-top:4px">涵盖身强弱、格局、财星、事业、婚姻、学业、子女、健康、大运等21个完整维度。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { analyzeRequest, saveAnalysis } from '../api/index.js'

export default {
  name: 'InputPage',
  data() {
    return {
      form: {
        name: '',
        gender: '男',
        date: '',
        calendar: 'solar',
        hour: 4,
        birthplace: '',
      },
      loading: false,
      shichen: [
        { value:0, label:'子时 23:00-00:59' },
        { value:2, label:'丑时 01:00-02:59' },
        { value:4, label:'寅时 03:00-04:59' },
        { value:6, label:'卯时 05:00-06:59' },
        { value:8, label:'辰时 07:00-08:59' },
        { value:10, label:'巳时 09:00-10:59' },
        { value:12, label:'午时 11:00-12:59' },
        { value:14, label:'未时 13:00-14:59' },
        { value:16, label:'申时 15:00-16:59' },
        { value:18, label:'酉时 17:00-18:59' },
        { value:20, label:'戌时 19:00-20:59' },
        { value:22, label:'亥时 21:00-22:59' },
      ],
    }
  },
  methods: {
    fillSample(name, date, calendar, hour, gender, birthplace) {
      this.form.name = name
      this.form.date = date
      this.form.calendar = calendar
      this.form.hour = hour
      this.form.gender = gender
      this.form.birthplace = birthplace
    },
    showToast(msg, type='info') {
      const container = document.querySelector('.toast-container') || (()=>{
        const d = document.createElement('div'); d.className='toast-container'; document.body.appendChild(d); return d
      })()
      const t = document.createElement('div'); t.className=`toast ${type}`; t.textContent=msg
      container.appendChild(t)
      setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity 0.3s'; setTimeout(()=>t.remove(),300) }, 2500)
    },
    async doAnalyze() {
      if (!this.form.name.trim()) { this.showToast('请输入姓名', 'error'); return }
      if (!this.form.date) { this.showToast('请选择出生日期', 'error'); return }

      this.loading = true
      const [y, m, d] = this.form.date.split('-').map(Number)

      try {
        const result = await analyzeRequest({
          name: this.form.name.trim(),
          gender: this.form.gender,
          birth_year: y,
          birth_month: m,
          birth_day: d,
          birth_hour: this.form.hour,
          calendar_type: this.form.calendar,
          birth_place: this.form.birthplace || '',
        })

        // Save to session for report page
        const reportData = {
          ...result,
          _meta: {
            name: this.form.name.trim(),
            gender: this.form.gender,
            year: y, month: m, day: d,
            hour: this.form.hour,
            calendar: this.form.calendar,
            birthplace: this.form.birthplace || '默认东八区',
            timestamp: new Date().toISOString(),
          }
        }

        // Try to save to server if logged in
        const token = localStorage.getItem('token')
        if (token) {
          try {
            await saveAnalysis(reportData)
          } catch(e) { /* silent */ }
        }

        // Store in sessionStorage for report page
        sessionStorage.setItem('lastReport', JSON.stringify(reportData))
        this.$router.push('/report')
      } catch (e) {
        this.showToast(e.message || '分析失败，请重试', 'error')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.input-page { padding-top: 8px; }
.hero { text-align: center; padding: 32px 0 18px; }
.hero-icon { font-size: 36px; color: var(--g); margin-bottom: 8px; }
.hero h1 { font-size: 26px; font-weight: 700; color: var(--g); letter-spacing: 4px; }
.hero-sub { font-size: 14px; color: var(--m); margin-top: 6px; }
.input-card { margin-top: 0; }
.form-row { display: flex; gap: 10px; }
.form-row + .form-row { margin-top: 0; }
.optional { font-size: 11px; color: rgba(138,128,112,0.5); font-weight: 400; }
.samples { display: flex; gap: 8px; justify-content: center; margin-top: 14px; flex-wrap: wrap; }
.samples span {
  padding: 5px 14px; border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 12px; color: var(--m); cursor: pointer; transition: all 0.2s;
}
.samples span:hover { border-color: var(--g); color: var(--g); }
</style>
