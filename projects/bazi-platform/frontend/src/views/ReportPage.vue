<template>
  <div class="report-page">
    <!-- 工具栏 -->
    <div class="report-toolbar">
      <div class="toolbar-left">
        <router-link to="/" class="btn-outline">← 重新输入</router-link>
      </div>
      <div class="toolbar-right">
        <button class="btn-primary" @click="doDownloadPDF">📄 下载PDF</button>
        <button class="btn-outline" @click="showRaw = !showRaw">🔍 {{ showRaw ? '隐藏' : '原始' }}数据</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="!report" class="empty-state">
      <div class="icon">📜</div>
      <p>暂无报告数据，请先输入生辰</p>
      <router-link to="/" class="btn-primary" style="display:inline-flex;margin-top:12px">← 返回输入</router-link>
    </div>

    <!-- ═══ 报告主体 ═══ -->
    <div v-else ref="reportContent" class="report-content">

      <!-- ① 个人档案 -->
      <div class="card profile-header">
        <div class="profile-name">{{ meta.name }}</div>
        <div class="profile-bazi">{{ bazi }}</div>
        <div class="profile-info">
          <span>{{ meta.gender }}</span><span class="dot">·</span>
          <span>{{ meta.year }}年{{ meta.month }}月{{ meta.day }}日</span><span class="dot">·</span>
          <span>{{ hourLabel }}时</span><span class="dot">·</span>
          <span>出生 {{ meta.birthplace }}</span>
        </div>
      </div>

      <!-- ② 四柱信息 -->
      <div class="card">
        <div class="card-title">📋 四柱八字</div>
        <table class="pillar-table">
          <tr><th></th><th>年柱</th><th>月柱</th><th>日柱</th><th>时柱</th></tr>
          <tr><td class="label-cell">十神</td><td v-for="p in pillars">{{ p.shi_shen || '' }}</td></tr>
          <tr><td class="label-cell">天干</td><td v-for="p in pillars" class="tg">{{ p.tian_gan || '' }}</td></tr>
          <tr><td class="label-cell">地支</td><td v-for="p in pillars" class="dz">{{ p.di_zhi || '' }}</td></tr>
          <tr><td class="label-cell">藏干</td><td v-for="p in pillars">{{ formatCangGan(p.cang_gan) }}</td></tr>
          <tr><td class="label-cell">纳音</td><td v-for="p in pillars">{{ p.na_yin || '' }}</td></tr>
          <tr><td class="label-cell">空亡</td><td v-for="p in pillars">{{ p.kong_wang || '' }}</td></tr>
        </table>
      </div>

      <!-- ③ 核心指标 -->
      <div class="card">
        <div class="card-title">⚖️ 命局核心数据</div>
        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-label">日主</div>
            <div class="metric-value gold">{{ riGan }}<span class="wx">{{ riWx }}</span></div>
          </div>
          <div class="metric-item">
            <div class="metric-label">身强弱</div>
            <div class="metric-value" :class="sqrColor">{{ sqrLabel }}<span class="sub">{{ sqrScore }}分</span></div>
          </div>
          <div class="metric-item">
            <div class="metric-label">格局</div>
            <div class="metric-value gold" style="font-size:13px">{{ geDetail || '—' }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">财星</div>
            <div class="metric-value gold">{{ caiTotal }}<span class="sub">分</span></div>
          </div>
          <div class="metric-item">
            <div class="metric-label">喜用神</div>
            <div class="metric-value gold" style="font-size:13px">{{ xiArr.join('、') || '—' }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">忌神</div>
            <div class="metric-value" style="color:var(--red);font-size:13px">{{ jiArr.join('、') || '—' }}</div>
          </div>
        </div>
      </div>

      <!-- ④ 命理分析正文（21§详细解读） -->
      <div class="card">
        <div class="card-title">📜 命理详细解读</div>
        <div class="report-body">

          <!-- §1 一页总览 -->
          <h3>一、一页总览</h3>
          <p>八字【<strong>{{ bazi }}</strong>】，日主<strong>{{ riGan }}{{ riWx ? '('+riWx+')' : '' }}</strong>，{{ genderText }}。</p>
          <p>日主性格特质：<NatureText :gan="riGan" />。</p>
          <p>命局{{ sqrDesc }}，{{ sqrLabel === '从弱' ? '格局特殊，全局能量高度集中，非凡俗之命。' : sqrLabel === '身强' && sqrScore >= 70 ? '体质强健，能扛压力，有担当大事的底子。' : '宜借平台和贵人发力，不宜单打独斗。' }}</p>
          <p v-if="geDetail">格局为<strong>{{ geDetail }}</strong>，{{ geDesc }}。</p>
          <p v-if="tiaoHou">调候用神为<strong>{{ tiaoHou }}</strong>，补足调候则运势顺遂。</p>

          <!-- §2 格局分析 -->
          <h3>二、格局分析</h3>
          <div v-html="secText('sec_2_ge_ju', 'detail') || '格局判断见上。'" class="sec-text"></div>
          <p v-if="geJuDetail">{{ geJuDetail }}</p>

          <!-- §3 身强弱 -->
          <h3>三、身强弱判定</h3>
          <p>命局<strong>{{ sqrLabel }}</strong>，综合评分<strong>{{ sqrScore }}分</strong>。</p>
          <div v-html="sqrDetailText" class="sec-text"></div>

          <!-- §4 喜用神与忌神 -->
          <h3>四、喜用神与忌神</h3>
          <p>喜用神：<strong style="color:var(--g)">{{ xiArr.join('、') || '—' }}</strong>。喜用神为命局平衡所需的关键五行，补足则诸事顺遂。</p>
          <p>忌神：<strong style="color:var(--red)">{{ jiArr.join('、') || '—' }}</strong>。忌神为命局过旺的五行，宜避让或化解。</p>
          <div v-if="tiaoHou"><p>调候用神：<strong style="color:var(--g)">{{ tiaoHou }}</strong>。调候为先，以调候用神弥补寒暖燥湿之偏。</p></div>

          <!-- §5 灾祸与化解 -->
          <h3>五、灾祸预警与化解</h3>
          <p v-if="riskLevel">风险评级：<strong>{{ riskLevel }}</strong>。</p>
          <p v-if="chongList.length">地支相冲：{{ chongList.join('、') }}。冲则动，易有变动、冲突之事。</p>
          <p v-if="xingList.length">地支相刑：{{ xingList.join('、') }}。刑则伤，人际关系易有摩擦。</p>
          <p v-if="haiList.length">地支相害：{{ haiList.join('、') }}。害则损，需防小人暗算。</p>
          <p v-if="remissionAdvice">化解建议：{{ remissionAdvice }}。</p>

          <!-- §6 性格解析 -->
          <h3>六、性格解析</h3>
          <p v-if="riZhuBase">日主特质：{{ riZhuBase }}。</p>
          <p v-if="personalityType">性格类型：{{ personalityType }}。</p>
          <p v-if="keyTraits.length">关键特质：{{ keyTraits.join('、') }}。</p>
          <p v-if="talents.length">天赋潜能：{{ talents.join('、') }}。</p>

          <!-- §7 身材外貌 -->
          <h3>七、身材外貌</h3>
          <p v-if="riZhuAppearance">基本特征：{{ riZhuAppearance }}。</p>
          <p v-if="buildText">{{ buildText }}。</p>
          <p v-if="styleText">气质风格：{{ styleText }}。</p>
          <p v-if="weightTendency">体重倾向：{{ weightTendency }}。</p>

          <!-- §8 财富格局 -->
          <h3>八、财富格局</h3>
          <p>财星<strong>{{ caiTotal }}分</strong>，属<strong>{{ wealthLevel || '—' }}</strong>层次。</p>
          <p v-if="levelDesc[wealthLevel]">{{ levelDesc[wealthLevel] }}。</p>
          <p v-if="ck.has">命带财库（{{ (ck.zhi || []).join('、') }}），有财富储存能力。</p>
          <div v-html="secText('sec_8_wealth', 'detail') || ''" class="sec-text"></div>

          <!-- §9 置业分析 -->
          <h3>九、置业分析</h3>
          <div v-html="secText('sec_9_property', 'detail') || '暂无置业分析数据。'" class="sec-text"></div>
          <p v-if="propertyPotential">置业方位：{{ propertyPotential }}。</p>
          <p v-if="propertyLevel">置业能力：{{ propertyLevel }}。</p>

          <!-- §10 事业发展 -->
          <h3>十、事业发展</h3>
          <p v-if="careerDir">事业方向宜走<strong>{{ careerDir }}</strong>路线。</p>
          <p v-if="careerGrade">{{ careerGrade }}。</p>
          <p v-if="industry">适宜行业：{{ industry }}。</p>
          <p v-if="ent">{{ ent }}</p>
          <p v-if="bestPath">{{ bestPath }}</p>
          <div v-html="secText('sec_10_career', 'detail') || ''" class="sec-text"></div>

          <!-- §11 学业学历 -->
          <h3>十一、学业学历</h3>
          <p v-if="eduLevel">学业层次：<strong>{{ eduLevel }}</strong>。</p>
          <p v-if="eduDetail">{{ eduDetail }}</p>
          <p v-if="ncShiShen === '伤官'">年干为伤官，少年时期或有叛逆倾向，学习方式偏灵活。</p>
          <p v-if="ncShiShen === '正印' || ncShiShen === '偏印'">年干见印星，有学业基因，学习能力强。</p>
          <div v-html="secText('sec_11_education', 'detail') || ''" class="sec-text"></div>

          <!-- §12 婚姻感情 -->
          <h3>十二、婚姻感情</h3>
          <p v-if="marQuality">婚姻质量：<strong>{{ marQuality }}</strong><span v-if="marScore">（{{ marScore }}/10分）</span>。</p>
          <p v-if="marWindow">最佳婚恋窗口：<strong>{{ marWindow }}</strong>。</p>
          <p v-if="spouseTrait">配偶特征：{{ spouseTrait }}。</p>
          <div v-html="secText('sec_12_marriage', 'detail') || ''" class="sec-text"></div>

          <!-- §13 子女运势 -->
          <h3>十三、子女运势</h3>
          <p v-if="childText">{{ childText }}</p>
          <p v-if="childAch">子女成就趋势：{{ childAch }}。</p>
          <div v-html="secText('sec_13_children', 'detail') || ''" class="sec-text"></div>

          <!-- §14 健康注意 -->
          <h3>十四、健康注意</h3>
          <p v-if="constitution">体质方面：{{ constitution }}。</p>
          <div v-for="w in wxOverThree" :key="w.wx"><p v-if="w.wx && w.organ">五行<strong>{{ w.wx }}</strong>过旺，对应<strong>{{ w.organ }}</strong>需留意保养。</p></div>
          <div v-for="b in wxBattles" :key="b.disease"><p v-if="b.disease">{{ b.disease }}。</p></div>
          <div v-html="secText('sec_14_health', 'detail') || ''" class="sec-text"></div>

          <!-- §15 六亲关系 -->
          <h3>十五、六亲关系</h3>
          <p v-if="familySummary">{{ familySummary }}。</p>
          <p v-if="familyEco">家庭经济：{{ familyEco }}。</p>
          <p v-if="familyPressure">家庭压力：{{ familyPressure }}。</p>
          <div v-html="secText('sec_15_family', 'detail') || ''" class="sec-text"></div>

          <!-- §16 流年事件 -->
          <h3>十六、流年关键事件</h3>
          <div v-if="eventsList.length">
            <p v-for="e in eventsList.slice(0,6)" :key="e.year">{{ e.year }}年：{{ e.description }}</p>
          </div>
          <p v-else>当前无显著流年事件触发。</p>
          <div v-html="secText('sec_16_events', 'detail') || ''" class="sec-text"></div>

          <!-- §17 大运详解 -->
          <h3>十七、大运详解</h3>
          <div v-if="dyList.length" class="dy-detail-grid">
            <div v-for="dy in dyList" :key="dy.gan_zhi" class="dy-detail-item" :class="dyClass(dy.score)">
              <div class="dy-name">{{ dy.gan_zhi }}</div>
              <div class="dy-age">{{ dy.start_age }}~{{ dy.end_age }}岁</div>
              <div class="dy-score">{{ dy.score }}分</div>
              <div class="dy-rank">{{ dy.rank || '' }}</div>
            </div>
          </div>
          <div v-html="secText('sec_17_da_yun_detail', 'detail') || ''" class="sec-text"></div>

        </div>
      </div>

      <!-- ⑤ 大运可视化 -->
      <div class="card" v-if="dyList.length">
        <div class="card-title">🚀 大运走势</div>
        <div class="da-yun-grid">
          <div v-for="dy in dyList" :key="dy.gan_zhi" class="dy-item" :class="dyClass(dy.score)">
            <div class="dy-name">{{ dy.gan_zhi }}</div>
            <div class="dy-age">{{ dy.start_age }}~{{ dy.end_age }}岁</div>
            <div class="dy-bar">
              <div class="dy-fill" :style="{width: (dy.score||5)*10+'%'}"></div>
            </div>
            <div class="dy-score">{{ dy.score }}分</div>
          </div>
        </div>
      </div>

      <!-- ⑥ 八维评分 -->
      <div class="card" v-if="dimKeys.length">
        <div class="card-title">📊 八维运势评分</div>
        <div class="dim-list">
          <div v-for="k in dimKeys" :key="k" class="dim-row">
            <div class="dim-name">{{ dimLabel(k) }}</div>
            <div class="dim-bar-bg"><div class="dim-bar" :style="{width: (dims[k].total||0)*10+'%', background: dimColor(dims[k].total)}"></div></div>
            <div class="dim-score">{{ dims[k].total }}</div>
          </div>
        </div>
      </div>

      <!-- ⑦ 三决断 -->
      <div class="card" v-if="verdicts.length">
        <div class="card-title">🎯 三决断</div>
        <div class="verdict-list">
          <div v-for="(v,i) in verdicts" :key="i" class="verdict-item">
            <div class="verdict-title">{{ v.title }}</div>
            <div class="verdict-body">{{ v.event }}</div>
          </div>
        </div>
      </div>

      <!-- ⑧ 五行开运 -->
      <div class="card" v-if="wxColors||wxDirs||wxJewel">
        <div class="card-title">🌈 五行开运指南</div>
        <div class="wx-advice-grid">
          <div v-if="wxColors" class="wx-item"><span class="wx-label">🎨 颜色</span>{{ wxColors }}</div>
          <div v-if="wxDirs" class="wx-item"><span class="wx-label">🧭 方位</span>{{ wxDirs }}</div>
          <div v-if="wxJewel" class="wx-item"><span class="wx-label">💎 饰品</span>{{ wxJewel }}</div>
          <div v-if="wxDiet" class="wx-item"><span class="wx-label">🥗 饮食</span>{{ wxDiet }}</div>
          <div v-if="wxNumbers" class="wx-item"><span class="wx-label">🔢 数字</span>{{ wxNumbers }}</div>
          <div v-if="wxAdvice" class="wx-item full"><span class="wx-label">💡 建议</span>{{ wxAdvice }}</div>
        </div>
      </div>

      <!-- ⑨ 人生建议 -->
      <div class="card" v-if="advice21">
        <div class="card-title">💡 人生建议</div>
        <div class="advice-text" v-html="advice21"></div>
      </div>

    </div>

    <!-- 原始数据调试 -->
    <div v-if="showRaw && report" class="raw-data">{{ JSON.stringify(report, null, 2) }}</div>
  </div>
</template>

<script>
import NatureText from '../components/NatureText.vue'

export default {
  name: 'ReportPage',
  components: { NatureText },
  setup() {
    const showToast = (msg, type) => {
      const c = document.querySelector('.toast-container') || (()=>{const d=document.createElement('div');d.className='toast-container';document.body.appendChild(d);return d})()
      const t=document.createElement('div');t.className=`toast ${type}`;t.textContent=msg
      c.appendChild(t);setTimeout(()=>{t.style.opacity='0';t.style.transition='opacity 0.3s';setTimeout(()=>t.remove(),300)},2500)
    }
    return { showToast }
  },
  data() {
    return { showRaw: false }
  },
  computed: {
    report() {
      const raw = sessionStorage.getItem('lastReport')
      if (!raw) return null
      try { return JSON.parse(raw) } catch { return null }
    },
    meta() { return this.report?._meta || {} },
    bazi() { return this.report?.paipan?.bazi || this.report?.result?.sec_1_overview?.bazi || '' },
    pillars() {
      const bd = this.report?.basic_data?.pillars || {}
      return ['year','month','day','hour'].map(k => bd[k] || {})
    },
    riGan() {
      return this.report?.basic_data?.ri_zhu?.gan || this.report?.result?.sec_1_overview?.ri_zhu?.gan || ''
    },
    riWx() {
      return this.report?.basic_data?.ri_zhu?.wu_xing || this.report?.result?.sec_1_overview?.ri_zhu?.wx || ''
    },
    genderText() { return this.meta.gender === '男' ? '男性' : '女性' },
    hourLabel() {
      const names = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
      return names[Math.floor((this.meta.hour||0)/2)] || '子'
    },
    // §3 身强弱
    sqrLabel() { return this.report?.result?.sec_3_shen_qiang_ruo?.label || this.report?.analysis?.shen_qiang_ruo?.label || '' },
    sqrScore() { return this.report?.result?.sec_3_shen_qiang_ruo?.score || this.report?.analysis?.shen_qiang_ruo?.score || 0 },
    sqrDesc() {
      const l = this.sqrLabel, s = this.sqrScore
      if (l === '从弱') return '为从弱格'
      if (l === '身强' && s >= 70) return '偏旺'
      if (l === '身强') return '身强'
      if (l === '身弱') return '身弱'
      if (l === '中和') return '中和'
      return ''
    },
    sqrColor() {
      if (this.sqrLabel === '从弱') return 'gold'
      if (this.sqrLabel === '身强') return this.sqrScore >= 70 ? 'gold' : 'green'
      return 'yellow'
    },
    sqrDetailText() {
      const s3 = this.report?.result?.sec_3_shen_qiang_ruo || {}
      const a = this.report?.analysis?.shen_qiang_ruo || {}
      return s3.detail || a.detail || ''
    },
    // §2 格局
    geDetail() { return this.report?.result?.sec_2_ge_ju?.detail || this.report?.analysis?.ge_ju?.detail || '' },
    geJuDetail() { return this.report?.result?.sec_2_ge_ju?.description || '' },
    geDesc() {
      const map = {
        '正官格':'为人正直守信，有管理才能',
        '七杀格':'魄力非凡，有闯劲，适合挑战性工作',
        '正财格':'求财踏实稳重，适合稳定收入',
        '偏财格':'财路宽广灵活，有投资天赋',
        '正印格':'学识渊博，有贵人运，适合文职',
        '偏印格':'思维独特，有冷门专长，宜从事技术',
        '食神格':'心态好福气厚，适合创意性工作',
        '伤官格':'才华横溢有灵气，宜发挥创造力',
      }
      return map[this.geDetail] || '命局结构清晰'
    },
    tiaoHou() { return this.report?.result?.sec_4_xi_yong?.tiao_hou || this.report?.analysis?.xi_yong_shen?.tiao_hou || '' },
    xiArr() { return this.report?.result?.sec_4_xi_yong?.xi || this.report?.analysis?.xi_yong_shen?.xi || [] },
    jiArr() { return this.report?.result?.sec_4_xi_yong?.ji || this.report?.analysis?.xi_yong_shen?.ji || [] },
    // §5 灾祸
    riskLevel() { return this.report?.result?.sec_5_zai_huo?.misfortune_full?.risk_level || '' },
    chongList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_chong || [] },
    xingList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_xing || [] },
    haiList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_hai || [] },
    remissionAdvice() { return this.report?.result?.sec_5_zai_huo?.remission_advice?.advice || '' },
    // §6 性格
    riZhuBase() { return this.report?.result?.sec_6_character?.ri_zhu_base || '' },
    personalityType() { return this.report?.result?.sec_6_character?.personality_type || '' },
    keyTraits() { return this.report?.result?.sec_6_character?.key_traits || [] },
    talents() { return this.report?.result?.sec_6_character?.talents || [] },
    // §7 外貌
    riZhuAppearance() { return this.report?.result?.sec_7_appearance?.ri_zhu_appearance || '' },
    buildText() { const s7=this.report?.result?.sec_7_appearance||{}; return [s7.build, s7.height_estimate].filter(Boolean).join('，') },
    styleText() { return this.report?.result?.sec_7_appearance?.style || '' },
    weightTendency() { return this.report?.result?.sec_7_appearance?.weight_tendency || '' },
    // §8 财富
    caiTotal() { return this.report?.result?.sec_8_wealth?.cai_xing_total || this.report?.analysis?.cai_xing?.total || 0 },
    wealthLevel() { return this.report?.result?.sec_8_wealth?.wealth_level || '' },
    ck() { return this.report?.result?.sec_8_wealth?.cai_ku || {} },
    levelDesc() { return {'巨富':'亿万级别','大富':'数千万至亿级','中富':'百万至千万级','小富':'小康以上','一般':'普通水平'} },
    // §9 置业
    propertyPotential() { return this.report?.result?.sec_9_property?.property_potential || '' },
    propertyLevel() { return this.report?.result?.sec_9_property?.property_level || '' },
    // §10 事业
    careerDir() { return this.report?.result?.sec_10_career?.career_direction || '' },
    careerGrade() { return this.report?.result?.sec_10_career?.career_grade || '' },
    industry() { return this.report?.result?.sec_10_career?.recommended_industries || '' },
    ent() { return this.report?.result?.sec_10_career?.entrepreneurship || '' },
    bestPath() { return this.report?.result?.sec_10_career?.best_path || '' },
    // §11 学历
    eduLevel() { return this.report?.result?.sec_11_education?.display || this.report?.result?.sec_11_education?.school_level || '' },
    eduDetail() { const s11=this.report?.result?.sec_11_education||{}; return s11.year_pillar_check?.detail || s11.analysis || '' },
    ncShiShen() { const s11=this.report?.result?.sec_11_education||{}; return s11.nian_gan_check?.shi_shen || '' },
    // §12 婚姻
    marQuality() { return this.report?.result?.sec_12_marriage?.quality || '' },
    marScore() { return this.report?.result?.sec_12_marriage?.quality_score || '' },
    marWindow() { return this.report?.result?.sec_12_marriage?.best_window_age || '' },
    spouseTrait() { return this.report?.result?.sec_12_marriage?.spouse_trait || '' },
    // §13 子女
    childText() { const s13=this.report?.result?.sec_13_children||{}; const c=s13.child_count_estimate; return c ? (typeof c === 'object' ? (c.text||c.数量||JSON.stringify(c)) : c) : '' },
    childAch() { return this.report?.result?.sec_13_children?.child_achievement || '' },
    // §14 健康
    constitution() { return this.report?.result?.sec_14_health?.constitution || '' },
    wxOverThree() { return this.report?.result?.sec_14_health?.wu_xing_over_three || [] },
    wxBattles() { return this.report?.result?.sec_14_health?.wu_xing_battles || [] },
    // §15 六亲
    familySummary() { const s15=this.report?.result?.sec_15_family||{}; return s15.summary || '' },
    familyEco() { const s15=this.report?.result?.sec_15_family||{}; return s15.family_economy || '' },
    familyPressure() { const s15=this.report?.result?.sec_15_family||{}; return s15.family_pressure || '' },
    // §16 流年
    eventsList() {
      const s16=this.report?.result?.sec_16_events||{}
      const ke=s16.key_events||{}
      const out=[]
      Object.entries(ke).forEach(([type,evts])=>{
        if(Array.isArray(evts)) evts.forEach(e=>{ if(e.year&&e.description) out.push(e) })
      })
      return out.sort((a,b)=>a.year-b.year)
    },
    // §17 大运
    dyList() { return this.report?.result?.sec_17_da_yun_detail?.list || this.report?.analysis?.da_yun?.list || [] },
    // §18 三决断
    verdicts() { return this.report?.result?.sec_18_verdicts || [] },
    // §19 运程曲线在da_yun里
    // §20 五行开运
    wxS20() { return this.report?.result?.sec_20_wu_xing_advice || {} },
    wxColors() { return this.wxS20.colors || '' },
    wxDirs() { return this.wxS20.directions || '' },
    wxJewel() { return this.wxS20.jewellery || '' },
    wxDiet() { return this.wxS20.diet || '' },
    wxNumbers() { return this.wxS20.lucky_numbers || '' },
    wxAdvice() { return this.wxS20.advice || '' },
    // §21 人生建议
    advice21() {
      const s21 = this.report?.result?.sec_21_advice || {}
      const parts = []
      if(s21.career?.advice) parts.push(`<p><strong>🏢 事业：</strong>${s21.career.advice}</p>`)
      if(s21.wealth?.advice) parts.push(`<p><strong>💰 财富：</strong>${s21.wealth.advice}</p>`)
      if(s21.health?.advice) parts.push(`<p><strong>🏥 健康：</strong>${s21.health.advice}</p>`)
      if(s21.marriage?.advice) parts.push(`<p><strong>💑 婚姻：</strong>${s21.marriage.advice}</p>`)
      return parts.join('')
    },
    // 8维评分
    dims() { return this.report?.analysis?.dimensions || this.report?.dimensions || {} },
    dimKeys() { return Object.keys(this.dims) },
    dimensionsV2() { return this.report?.result?.sec_19_overall?.dimensions || {} },
    // raw debug
  },
  methods: {
    formatCangGan(cg) {
      if (!cg) return ''
      return cg.map(x => typeof x === 'object' ? (x.gan || x[0] || '') : x).join(' ')
    },
    secText(section, field) {
      const s = this.report?.result?.[section] || {}
      return s[field] || s.description || s.analysis || ''
    },
    dyClass(score) {
      if (score >= 8) return 'gold'
      if (score >= 6) return 'green'
      if (score >= 4) return 'yellow'
      return 'red'
    },
    dimLabel(key) {
      const map = {'事业':'事业','财富':'财富','婚姻':'婚姻','健康':'健康','子女':'子女','学业':'学业','贵人':'贵人','综合':'综合'}
      return map[key] || key
    },
    dimColor(score) {
      if (score >= 7) return 'var(--green)'
      if (score >= 5) return 'var(--g)'
      return 'var(--red)'
    },
    async doDownloadPDF() {
      this.showToast('正在生成PDF...', 'info')
      // 直接从API获取 — 真正的文本PDF，不是截图
      const params = {
        name: this.meta.name || '用户',
        gender: this.meta.gender || '男',
        birth_year: this.meta.year || 2000,
        birth_month: this.meta.month || 1,
        birth_day: this.meta.day || 1,
        birth_hour: this.meta.hour || 0,
        birth_place: this.meta.birthplace || '',
      }
      try {
        const res = await fetch('/api/v1/report/pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params),
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.detail || `请求失败 (${res.status})`)
        }
        // 下载PDF文件
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        const name = this.meta.name || '命理报告'
        a.href = url
        a.download = `${name}_金鉴真人命理报告.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        this.showToast('PDF下载成功！（文本格式，可选中文字）', 'success')
      } catch (e) {
        console.error('PDF生成失败:', e)
        this.showToast('PDF生成失败: ' + e.message, 'error')
      }
    },
  },
}
</script>

<style scoped>
.report-page { padding-top: 4px; }
.report-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; gap: 8px; flex-wrap: wrap;
}
.toolbar-left, .toolbar-right { display: flex; gap: 6px; align-items: center; }
.profile-header { text-align: center; background: linear-gradient(135deg,#1e1e3a,#2a2a4a); }
.profile-name { font-size: 20px; font-weight: 700; }
.profile-bazi { font-size: 28px; color: var(--g); letter-spacing: 6px; margin: 6px 0; }
.profile-info { font-size: 12px; color: var(--m); }
.profile-info .dot { margin: 0 6px; }

.pillar-table { width:100%; border-collapse:collapse; font-size:13px; }
.pillar-table th { color:var(--g); font-weight:600; font-size:11px; padding:7px 4px; border-bottom:1px solid rgba(255,255,255,0.06); text-align:center; }
.pillar-table td { padding:6px 4px; text-align:center; border-bottom:1px solid rgba(255,255,255,0.03); }
.pillar-table .label-cell { color:var(--m); font-size:11px; text-align:left; padding-left:6px; width:52px; }
.pillar-table .tg { color: var(--g); font-weight: 600; }
.pillar-table .dz { color: var(--g-light); }

.metrics-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
.metric-item { background:rgba(0,0,0,0.15); border-radius:8px; padding:12px 8px; text-align:center; }
.metric-label { font-size:11px; color:var(--m); margin-bottom:4px; }
.metric-value { font-size:20px; font-weight:700; }
.metric-value .sub { font-size:12px; font-weight:400; margin-left:3px; color:var(--m); }
.metric-value .wx { font-size:12px; font-weight:400; color:var(--m); }
.metric-value.gold { color:var(--g); }
.metric-value.green { color:var(--green); }
.metric-value.yellow { color:var(--yellow); }

.report-body { line-height:2; font-size:14px; }
.report-body h3 { font-size:15px; color:var(--g); margin:16px 0 8px; padding-bottom:4px; border-bottom:1px solid rgba(255,255,255,0.04); }
.report-body p { margin-bottom:6px; }
.sec-text { font-size:13px; color:var(--m); line-height:1.8; margin-top:4px; }

.da-yun-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.dy-item { background:rgba(0,0,0,0.12); border-radius:8px; padding:10px 8px; text-align:center; font-size:12px; }
.dy-item .dy-name { font-size:16px; font-weight:600; margin-bottom:2px; }
.dy-item .dy-age { font-size:10px; color:var(--m); }
.dy-bar { height:4px; background:rgba(255,255,255,0.06); border-radius:2px; margin:4px 0; overflow:hidden; }
.dy-fill { height:100%; background:var(--g); border-radius:2px; }
.dy-score { font-size:10px; color:var(--m); }
.dy-item.gold { border:1px solid var(--g); }
.dy-item.green { border:1px solid rgba(76,175,80,0.3); }
.dy-item.yellow { border:1px solid rgba(255,152,0,0.3); }
.dy-item.red { border:1px solid rgba(192,57,43,0.3); }

.dy-detail-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:6px; }
.dy-detail-item { background:rgba(0,0,0,0.12); border-radius:8px; padding:10px; text-align:center; }
.dy-detail-item .dy-name { font-size:16px; font-weight:600; }
.dy-detail-item .dy-age { font-size:10px; color:var(--m); }
.dy-detail-item .dy-score { font-size:12px; font-weight:700; margin-top:2px; }
.dy-detail-item .dy-rank { font-size:10px; color:var(--m); }
.dy-detail-item.gold { border:1px solid var(--g); }
.dy-detail-item.green { border:1px solid rgba(76,175,80,0.3); }
.dy-detail-item.yellow { border:1px solid rgba(255,152,0,0.3); }
.dy-detail-item.red { border:1px solid rgba(192,57,43,0.3); }

.dim-list { margin-top:4px; }
.dim-row { display:flex; align-items:center; margin-bottom:8px; }
.dim-name { width:56px; font-size:12px; color:var(--m); flex-shrink:0; }
.dim-bar-bg { flex:1; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:0 10px; }
.dim-bar { height:100%; border-radius:4px; }
.dim-score { font-size:13px; color:var(--g); width:28px; text-align:right; }

.verdict-list { margin-top:4px; }
.verdict-item { background:rgba(0,0,0,0.1); border-radius:8px; padding:12px; margin-bottom:6px; }
.verdict-title { font-size:13px; color:var(--g); font-weight:600; margin-bottom:2px; }
.verdict-body { font-size:13px; }

.wx-advice-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.wx-item { background:rgba(0,0,0,0.1); border-radius:6px; padding:8px 12px; font-size:13px; }
.wx-label { display:block; font-size:11px; color:var(--m); margin-bottom:2px; }
.wx-item.full { grid-column:1/3; }

.advice-text { font-size:14px; line-height:2; }
.advice-text p { margin-bottom:6px; }

.raw-data {
  background:#0a0a12; border-radius:8px; padding:14px; margin-top:12px;
  font-family:monospace; font-size:10px; color:#666; white-space:pre-wrap;
  max-height:400px; overflow:auto;
}

@media print {
  .report-toolbar, .raw-data { display:none!important; }
  body { background:#fff!important; color:#222!important; }
  .card { background:#fff!important; border:1px solid #ddd!important; break-inside:avoid; }
  .profile-header { background:#f8f6f0!important; }
  .profile-bazi, .card-title, .report-body h3 { color:#222!important; }
  .metrics-grid .metric-item { background:#f5f5f5!important; }
  .pillar-table td, .pillar-table th { border-color:#ddd!important; }
}

@media (max-width:480px) {
  .metrics-grid { grid-template-columns:1fr 1fr; }
  .da-yun-grid, .dy-detail-grid { grid-template-columns:repeat(2,1fr); }
  .wx-advice-grid { grid-template-columns:1fr; }
  .wx-item.full { grid-column:1; }
}
</style>
