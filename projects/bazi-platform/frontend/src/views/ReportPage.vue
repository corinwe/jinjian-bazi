<template>
  <div class="report-page">
    <!-- 工具栏 -->
    <div class="report-toolbar">
      <router-link to="/" class="btn-outline">← 重新输入</router-link>
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

      <!-- ════════════════ ① 命局总览 ════════════════ -->
      <div class="card profile-card">
        <div class="profile-header">
          <div class="profile-left">
            <div class="profile-name">{{ meta.name }}</div>
            <div class="profile-meta">
              <span class="tag-gender">{{ meta.gender }}</span>
              <span class="dot">·</span>
              <span>{{ meta.year }}年{{ meta.month }}月{{ meta.day }}日</span>
              <span class="dot">·</span>
              <span>{{ hourLabel }}时</span>
            </div>
          </div>
          <div class="bazi-display">{{ bazi }}</div>
        </div>
      </div>

      <!-- ═══ 四柱八字表 ═══ -->
      <div class="card">
        <div class="card-title"><span class="title-icon">📋</span> 四柱八字 <span class="title-badge">年·月·日·时</span></div>
        <div class="pillar-table-wrap">
          <table class="pillar-table">
            <thead>
              <tr>
                <th class="th-label"></th>
                <th v-for="(p, i) in pillars" :key="i">
                  <span class="pillar-order">{{ ['年柱','月柱','日柱','时柱'][i] }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="td-label">十神</td>
                <td v-for="p in pillars" class="cell-ss" :class="ssClass(p.shi_shen)">{{ p.shi_shen || '—' }}</td>
              </tr>
              <tr class="row-tg">
                <td class="td-label">天干</td>
                <td v-for="p in pillars" class="cell-tg">{{ p.gan }}<span class="wx-sub">{{ ganWx(p.gan) }}</span></td>
              </tr>
              <tr class="row-dz">
                <td class="td-label">地支</td>
                <td v-for="p in pillars" class="cell-dz">{{ p.zhi }}<span class="wx-sub">{{ zhiWx(p.zhi) }}</span></td>
              </tr>
              <tr>
                <td class="td-label">藏干</td>
                <td v-for="p in pillars" class="cell-cg">{{ formatCangGan(p.cang_gan) || '—' }}</td>
              </tr>
              <tr>
                <td class="td-label">纳音</td>
                <td v-for="p in pillars" class="cell-ny">{{ p.na_yin || '—' }}</td>
              </tr>
              <tr>
                <td class="td-label">空亡</td>
                <td v-for="p in pillars" class="cell-kw">{{ p.kong_wang || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ 命局核心数据 ═══ -->
      <div class="card">
        <div class="card-title"><span class="title-icon">⚖️</span> 命局核心数据</div>
        <div class="core-grid">
          <div class="core-item">
            <div class="core-label">日主</div>
            <div class="core-val gold">{{ riGan }} <span class="wx-tag">{{ riWx }}</span></div>
          </div>
          <div class="core-item">
            <div class="core-label">身强弱</div>
            <div class="core-val" :class="sqrColorClass">{{ sqrLabel }} <span class="score-sub">{{ sqrScore }}分</span></div>
          </div>
          <div class="core-item">
            <div class="core-label">格局</div>
            <div class="core-val gold sm">{{ geDetail || '—' }}</div>
          </div>
          <div class="core-item">
            <div class="core-label">财星</div>
            <div class="core-val gold">{{ caiTotal }} <span class="score-sub">分</span></div>
          </div>
          <div class="core-item">
            <div class="core-label">起运</div>
            <div class="core-val gold">{{ qiYunAge }}<span class="score-sub">岁</span></div>
          </div>
          <div class="core-item">
            <div class="core-label">调候</div>
            <div class="core-val gold sm">{{ tiaoHou || '—' }}</div>
          </div>
          <div class="core-item wide">
            <div class="core-label">喜用神</div>
            <div class="core-val gold sm">{{ xiArr.join('、') || '—' }}</div>
          </div>
          <div class="core-item wide">
            <div class="core-label">忌神</div>
            <div class="core-val danger sm">{{ jiArr.join('、') || '—' }}</div>
          </div>
        </div>
      </div>

      <!-- ═══ 五行能量 ═══ -->
      <div class="card" v-if="wxEnergyKeys.length">
        <div class="card-title"><span class="title-icon">🌊</span> 五行能量分布</div>
        <div class="wx-bars">
          <div v-for="k in wxEnergyKeys" :key="k" class="wx-bar-row">
            <span class="wx-bar-label">{{ k }}</span>
            <div class="wx-bar-track">
              <div class="wx-bar-fill" :style="{width: wxBarWidth(k)+'%', background: wxColor(k)}"></div>
            </div>
            <span class="wx-bar-val">{{ wxEnergy[k] }}</span>
          </div>
        </div>
      </div>

      <!-- ════════════════ ② 大运流年 ════════════════ -->
      <div class="card" v-if="dyList.length">
        <div class="card-title"><span class="title-icon">🚀</span> 大运走势</div>
        <div class="dy-timeline">
          <div v-for="(dy, i) in dyList" :key="dy.gan_zhi" class="dy-seg" :class="dyClass(dy.score)">
            <div class="dy-indicator"></div>
            <div class="dy-body">
              <div class="dy-top">
                <span class="dy-ganzhi">{{ dy.gan_zhi }}</span>
                <span class="dy-label-tag" :class="dyTagClass(dy)">{{ dy.label || '' }}</span>
              </div>
              <div class="dy-bottom">
                <span class="dy-age">{{ dy.start_age }}~{{ dy.end_age }}岁</span>
                <span class="dy-year">{{ dy.start_year }}~{{ dy.end_year }}年</span>
                <span class="dy-score">{{ dy.score || '—' }}分</span>
              </div>
            </div>
          </div>
        </div>
        <div class="dy-highlights" v-if="bestDaYun || worstDaYun">
          <div class="dy-best" v-if="bestDaYun">
            <span class="hl-icon">🏆</span> 最佳运：<strong>{{ bestDaYun }}</strong>（{{ bestDaYunLabel }}）
          </div>
          <div class="dy-worst" v-if="worstDaYun">
            <span class="hl-icon">⚠️</span> 最差运：<strong>{{ worstDaYun }}</strong>（{{ worstDaYunLabel }}）
          </div>
        </div>
      </div>

      <!-- 流年事件 -->
      <div class="card" v-if="eventsList.length">
        <div class="card-title"><span class="title-icon">📅</span> 关键流年事件</div>
        <div class="events-list">
          <div v-for="e in eventsList.slice(0,6)" :key="e.year" class="event-item">
            <span class="event-year">{{ e.year }}</span>
            <span class="event-desc">{{ e.description }}</span>
          </div>
        </div>
      </div>

      <!-- ════════════════ ③ 深度命理分析 ════════════════ -->
      <div class="card">
        <div class="card-title"><span class="title-icon">📜</span> 深度命理分析</div>
        <div class="report-body">

          <!-- §1 总览 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec1'}" @click="toggleSec('sec1')">
            <div class="sec-header"><span class="sec-num">一</span>一页总览 <span class="sec-toggle">{{ expandedSec==='sec1' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec1'" class="sec-content">
              <p>八字【<strong>{{ bazi }}</strong>】，日主<strong>{{ riGan }}{{ riWx ? '('+riWx+')' : '' }}</strong>，{{ genderText }}。</p>
              <p>命局{{ sqrLabel }}（{{ sqrScore }}分）{{ sqrLabel === '从弱' ? '，格局特殊，非凡俗之命。' : sqrLabel === '身强' && sqrScore >= 70 ? '，体质强健，能扛大事。' : '，宜借平台和贵人发力。' }}</p>
              <p v-if="geDetail">格局：<strong>{{ geDetail }}</strong> — {{ geDesc }}。</p>
              <p>喜用神：<strong class="text-xi">{{ xiArr.join('、') || '—' }}</strong>　忌神：<strong class="text-ji">{{ jiArr.join('、') || '—' }}</strong></p>
              <p v-if="tiaoHou">调候用神：<strong>{{ tiaoHou }}</strong></p>
              <p v-if="s1NaYin">纳音：{{ s1NaYin }}</p>
              <p v-if="s1QiYun">起运：<strong>{{ s1QiYun }}岁</strong></p>
              <p v-if="s1Edu">学历：{{ s1Edu }}</p>
              <p v-if="caiTotal">财星评分：<strong>{{ caiTotal }}分</strong>（{{ wealthLevel || '—' }}）</p>
              <p v-if="bestDaYun">最佳大运：<strong>{{ bestDaYun }}</strong>（{{ bestDaYunLabel || '' }}）</p>
              <p v-if="worstDaYun">最差大运：<strong>{{ worstDaYun }}</strong>（{{ worstDaYunLabel || '' }}）</p>
              <p v-if="s1Narrative" style="margin-top:8px;color:var(--m);font-size:13px;line-height:1.8">{{ s1Narrative }}</p>
            </div>
          </div>

          <!-- §2 格局 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec2'}" @click="toggleSec('sec2')">
            <div class="sec-header"><span class="sec-num">二</span>格局分析 <span class="sec-toggle">{{ expandedSec==='sec2' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec2'" class="sec-content">
              <p><strong>{{ geDetail }}</strong></p>
            </div>
          </div>

          <!-- §3 身强弱 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec3'}" @click="toggleSec('sec3')">
            <div class="sec-header"><span class="sec-num">三</span>身强弱判定 <span class="sec-toggle">{{ expandedSec==='sec3' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec3'" class="sec-content">
              <div class="score-badge" :class="sqrColorClass">{{ sqrLabel }} · {{ sqrScore }}分</div>
              <div v-if="sqrDetails" class="sqr-detail-grid">
                <div class="sqr-detail-item"><span class="sqr-d-label">月令印星</span><span class="sqr-d-val">{{ sqrDetails.yue_yin || 0 }}</span></div>
                <div class="sqr-detail-item"><span class="sqr-d-label">月令比劫</span><span class="sqr-d-val">{{ sqrDetails.yue_bi || 0 }}</span></div>
                <div class="sqr-detail-item"><span class="sqr-d-label">天干比劫</span><span class="sqr-d-val">{{ sqrDetails.tg_bi || 0 }}</span></div>
                <div class="sqr-detail-item"><span class="sqr-d-label">日支生扶</span><span class="sqr-d-val">{{ sqrDetails.rz || 0 }}</span></div>
                <div class="sqr-detail-item"><span class="sqr-d-label">年时生扶</span><span class="sqr-d-val">{{ sqrDetails.nsz || 0 }}</span></div>
                <div class="sqr-detail-item total"><span class="sqr-d-label">总分</span><span class="sqr-d-val">{{ sqrDetails.total || sqrScore }}</span></div>
              </div>
            </div>
          </div>

          <!-- §4 喜用神 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec4'}" @click="toggleSec('sec4')">
            <div class="sec-header"><span class="sec-num">四</span>喜用神与忌神 <span class="sec-toggle">{{ expandedSec==='sec4' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec4'" class="sec-content">
              <div class="xy-grid">
                <div class="xy-item xi-box">
                  <div class="xy-label">喜用神</div>
                  <div class="xy-val">{{ xiArr.join('、') || '—' }}</div>
                </div>
                <div class="xy-item ji-box">
                  <div class="xy-label">忌神</div>
                  <div class="xy-val">{{ jiArr.join('、') || '—' }}</div>
                </div>
              </div>
              <p v-if="tiaoHou">调候用神：<strong>{{ tiaoHou }}</strong></p>
            </div>
          </div>

          <!-- §5 灾祸 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec5'}" @click="toggleSec('sec5')">
            <div class="sec-header"><span class="sec-num">五</span>灾祸预警 <span class="sec-toggle">{{ expandedSec==='sec5' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec5'" class="sec-content">
              <div v-if="riskLevel" class="risk-badge" :class="riskClass">{{ riskLevel }}</div>
              <div class="dz-rel-grid">
                <div v-if="chongList.length" class="rel-item"><span class="rel-icon">⚡</span>相冲：{{ chongList.join('、') }}</div>
                <div v-if="xingList.length" class="rel-item"><span class="rel-icon">🔗</span>相刑：{{ xingList.join('、') }}</div>
                <div v-if="haiList.length" class="rel-item"><span class="rel-icon">⚔️</span>相害：{{ haiList.join('、') }}</div>
              </div>
              <p v-if="remissionAdvice">化解建议：{{ remissionAdvice }}</p>
            </div>
          </div>

          <!-- §6 性格 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec6'}" @click="toggleSec('sec6')">
            <div class="sec-header"><span class="sec-num">六</span>性格解析 <span class="sec-toggle">{{ expandedSec==='sec6' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec6'" class="sec-content">
              <p v-if="riZhuBase"><strong>日主特质：</strong>{{ riZhuBase }}</p>
              <p v-if="personalityType"><strong>性格类型：</strong>{{ personalityType }}</p>
              <div v-if="keyTraits.length" class="tag-list"><span v-for="t in keyTraits" :key="t" class="tag">{{ t }}</span></div>
              <div v-if="talents.length" class="talent-list"><strong>天赋潜能：</strong>{{ talents.join('、') }}</div>
            </div>
          </div>

          <!-- §7 外貌 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec7'}" @click="toggleSec('sec7')">
            <div class="sec-header"><span class="sec-num">七</span>身材外貌 <span class="sec-toggle">{{ expandedSec==='sec7' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec7'" class="sec-content">
              <p v-if="riZhuAppearance">{{ riZhuAppearance }}</p>
              <p v-if="buildText">{{ buildText }}</p>
              <p v-if="styleText">气质风格：{{ styleText }}</p>
              <p v-if="weightTendency">体重倾向：{{ weightTendency }}</p>
            </div>
          </div>

          <!-- §8 财富 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec8'}" @click="toggleSec('sec8')">
            <div class="sec-header"><span class="sec-num">八</span>财富格局 <span class="sec-toggle">{{ expandedSec==='sec8' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec8'" class="sec-content">
              <div class="wealth-header">
                <div class="wealth-score">{{ caiTotal }}<span class="ws-unit">分</span></div>
                <div class="wealth-level">{{ wealthLevel || '—' }}</div>
              </div>
              <p>{{ levelDesc[wealthLevel] || '' }}</p>
              <div v-if="ck && ck.has" class="ck-box">📦 命带财库（{{ (ck.zhi || []).join('、') }}），有财富储存能力。</div>
              <div class="cai-detail-grid" v-if="caiDetails">
                <div v-for="(v, k) in caiDetails" :key="k" class="cai-d-item">
                  <span class="cai-d-label">{{ caiDetailLabel(k) }}</span>
                  <span class="cai-d-val">{{ v }}分</span>
                </div>
              </div>
            </div>
          </div>

          <!-- §9 置业 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec9'}" @click="toggleSec('sec9')">
            <div class="sec-header"><span class="sec-num">九</span>置业分析 <span class="sec-toggle">{{ expandedSec==='sec9' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec9'" class="sec-content">
              <p v-if="propertyPotential">置业方位：{{ propertyPotential }}</p>
              <p v-if="propertyLevel">置业能力：{{ propertyLevel }}</p>
            </div>
          </div>

          <!-- §10 事业 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec10'}" @click="toggleSec('sec10')">
            <div class="sec-header"><span class="sec-num">十</span>事业发展 <span class="sec-toggle">{{ expandedSec==='sec10' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec10'" class="sec-content">
              <p v-if="careerDir">事业方向宜走<strong>{{ careerDir }}</strong>路线。</p>
              <p v-if="careerGrade">{{ careerGrade }}</p>
              <p v-if="industry">✅ 适宜行业：{{ industry }}</p>
              <p v-if="ent" class="ent-box">{{ ent }}</p>
              <p v-if="bestPath" class="path-box">💡 {{ bestPath }}</p>
            </div>
          </div>

          <!-- §11 学历 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec11'}" @click="toggleSec('sec11')">
            <div class="sec-header"><span class="sec-num">十一</span>学业学历 <span class="sec-toggle">{{ expandedSec==='sec11' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec11'" class="sec-content">
              <div class="edu-badge" v-if="eduLevel">{{ eduLevel }}</div>
              <p v-if="eduDetail">{{ eduDetail }}</p>
              <p v-if="ncShiShen && ncShiShen.includes('印')">年干为{{ ncShiShen }}，有学业基因，学习能力强。</p>
              <p v-if="ncShiShen && ncShiShen === '伤官'">年干为伤官，少年时期或有叛逆倾向。</p>
            </div>
          </div>

          <!-- §12 婚姻 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec12'}" @click="toggleSec('sec12')">
            <div class="sec-header"><span class="sec-num">十二</span>婚姻感情 <span class="sec-toggle">{{ expandedSec==='sec12' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec12'" class="sec-content">
              <div v-if="marQuality" class="mar-header">
                <span class="mar-badge">{{ marQuality }}</span>
                <span v-if="marScore" class="mar-score">{{ marScore }}/10分</span>
              </div>
              <p v-if="marWindow">最佳婚恋窗口：<strong>{{ marWindow }}</strong></p>
              <p v-if="spouseTrait">配偶特征：{{ spouseTrait }}</p>
            </div>
          </div>

          <!-- §13 子女 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec13'}" @click="toggleSec('sec13')">
            <div class="sec-header"><span class="sec-num">十三</span>子女运势 <span class="sec-toggle">{{ expandedSec==='sec13' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec13'" class="sec-content">
              <p v-if="childText">{{ childText }}</p>
              <p v-if="childAch">子女成就趋势：{{ childAch }}</p>
            </div>
          </div>

          <!-- §14 健康 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec14'}" @click="toggleSec('sec14')">
            <div class="sec-header"><span class="sec-num">十四</span>健康注意 <span class="sec-toggle">{{ expandedSec==='sec14' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec14'" class="sec-content">
              <p v-if="constitution"><strong>体质：</strong>{{ constitution }}</p>
              <template v-for="wx in wxOverThree" :key="wx.wx + (wx.organ||'')">
                <div v-if="wx.wx" class="health-warn">
                  ⚠️ 五行<strong>{{ wx.wx }}</strong>过旺（{{ wx.count }}），{{ wx.organ ? '对应'+wx.organ+'需留意保养' : '需注意平衡' }}
                </div>
              </template>
            </div>
          </div>

          <!-- §15 六亲 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec15'}" @click="toggleSec('sec15')">
            <div class="sec-header"><span class="sec-num">十五</span>六亲关系 <span class="sec-toggle">{{ expandedSec==='sec15' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec15'" class="sec-content">
              <p v-if="familySummary">{{ familySummary }}</p>
              <p v-if="familyEco">家庭经济：{{ familyEco }}</p>
              <p v-if="familyPressure">家庭压力：{{ familyPressure }}</p>
            </div>
          </div>

          <!-- §16 流年 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec16'}" @click="toggleSec('sec16')">
            <div class="sec-header"><span class="sec-num">十六</span>流年关键事件 <span class="sec-toggle">{{ expandedSec==='sec16' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec16'" class="sec-content">
              <div v-if="eventsList.length">
                <div v-for="e in eventsList.slice(0,10)" :key="e.year" class="event-item">
                  <span class="event-year">{{ e.year }}</span>
                  <span class="event-desc">{{ e.description }}</span>
                </div>
              </div>
              <p v-else>当前无显著流年事件触发。</p>
            </div>
          </div>

          <!-- §17 大运详解 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec17'}" @click="toggleSec('sec17')">
            <div class="sec-header"><span class="sec-num">十七</span>大运详解 <span class="sec-toggle">{{ expandedSec==='sec17' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec17'" class="sec-content">
              <div v-for="dy in dyList" :key="dy.gan_zhi" class="dy-detail-row" :class="dyClass(dy.score)">
                <div class="dd-top">
                  <span class="dd-ganzhi">{{ dy.gan_zhi }}</span>
                  <span class="dd-age">{{ dy.start_age }}~{{ dy.end_age }}岁</span>
                  <span class="dd-score">{{ dy.score || '—' }}分</span>
                  <span class="dd-label-tag" :class="dyTagClass(dy)">{{ dy.label || '' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- §18 三决断 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec18'}" @click="toggleSec('sec18')">
            <div class="sec-header"><span class="sec-num">十八</span>三决断 <span class="sec-toggle">{{ expandedSec==='sec18' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec18'" class="sec-content">
              <div v-for="(v,i) in verdicts" :key="i" class="verdict-card">
                <div class="vd-title">{{ v.title }}</div>
                <div class="vd-body">{{ v.event }}</div>
              </div>
            </div>
          </div>

          <!-- §19 运程曲线 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec19'}" @click="toggleSec('sec19')">
            <div class="sec-header"><span class="sec-num">十九</span>运程曲线 <span class="sec-toggle">{{ expandedSec==='sec19' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec19'" class="sec-content">
              <p>运程数据详见上方大运走势表。</p>
            </div>
          </div>

          <!-- §20 五行开运 -->
          <div class="sec-block" :class="{expanded: expandedSec==='sec20'}" @click="toggleSec('sec20')">
            <div class="sec-header"><span class="sec-num">二十</span>五行开运指南 <span class="sec-toggle">{{ expandedSec==='sec20' ? '▾' : '▸' }}</span></div>
            <div v-show="expandedSec==='sec20'" class="sec-content">
              <div class="wx-adv-grid">
                <div v-if="wxColors" class="wa-item"><span class="wa-icon">🎨</span><span class="wa-label">颜色</span><span class="wa-val">{{ wxColors }}</span></div>
                <div v-if="wxDirs" class="wa-item"><span class="wa-icon">🧭</span><span class="wa-label">方位</span><span class="wa-val">{{ wxDirs }}</span></div>
                <div v-if="wxJewel" class="wa-item"><span class="wa-icon">💎</span><span class="wa-label">饰品</span><span class="wa-val">{{ wxJewel }}</span></div>
                <div v-if="wxDiet" class="wa-item"><span class="wa-icon">🥗</span><span class="wa-label">饮食</span><span class="wa-val">{{ wxDiet }}</span></div>
                <div v-if="wxNumbers" class="wa-item"><span class="wa-icon">🔢</span><span class="wa-label">数字</span><span class="wa-val">{{ wxNumbers }}</span></div>
                <div v-if="wxAdvice" class="wa-item full"><span class="wa-icon">💡</span><span class="wa-label">建议</span><span class="wa-val">{{ wxAdvice }}</span></div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- ════════════════ ④ 人生建议 ════════════════ -->
      <div class="card advice-card" v-if="adviceItems.length">
        <div class="card-title"><span class="title-icon">💡</span> 人生建议</div>
        <div class="advice-list">
          <div v-for="item in adviceItems" :key="item.icon+item.label" class="advice-item">
            <div class="advice-icon">{{ item.icon }}</div>
            <div class="advice-body">
              <div class="advice-label">{{ item.label }}</div>
              <div class="advice-text">{{ item.text }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 脚注 -->
      <div class="report-footer">
        <p>金鉴真人 · 确定性规则引擎报告</p>
        <p class="footer-time">报告生成时间：{{ generateTime }}</p>
      </div>

    </div>

    <!-- 原始数据调试 -->
    <div v-if="showRaw && report" class="raw-data">{{ JSON.stringify(report, null, 2) }}</div>
  </div>
</template>

<script>
import NatureText from '../components/NatureText.vue'

const WU_XING_COLORS = {
  '木': '#4caf50',
  '火': '#ff5722',
  '土': '#ff9800',
  '金': '#c9a84c',
  '水': '#2196f3',
}

const TIAN_GAN_WX = {
  '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
}

const DI_ZHI_WX = {
  '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}

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
    return {
      showRaw: false,
      expandedSec: 'sec3',
    }
  },
  computed: {
    report() {
      const raw = sessionStorage.getItem('lastReport')
      if (!raw) return null
      try { return JSON.parse(raw) } catch { return null }
    },
    meta() { return this.report?._meta || {} },
    bazi() { return this.report?.paipan?.bazi || this.report?.result?.sec_1_overview?.bazi || '' },
    s1NaYin() {
      const ny = this.report?.result?.sec_1_overview?.na_yin
      if (Array.isArray(ny)) return ny.join('、')
      return ny || ''
    },
    s1QiYun() { return this.report?.result?.sec_1_overview?.qi_yun_age ?? '' },
    s1Edu() {
      const edu = this.report?.result?.sec_1_overview?.education
      if (!edu) return ''
      return String(edu).replace(/[🎓🥇🏅]/g, '').trim() || edu
    },
    s1Narrative() { return this.report?.result?.sec_1_overview?.narrative || '' },
    generateTime() { return this.report?.result?.meta?.generated ? new Date(this.report.result.meta.generated).toLocaleString('zh-CN') : new Date().toLocaleString('zh-CN') },

    pillars() {
      const bd = this.report?.basic_data?.pillars || {}
      return ['year','month','day','hour'].map(k => {
        const p = bd[k] || {}
        return {
          gan: p.gan || p.tian_gan || '',
          zhi: p.zhi || p.di_zhi || '',
          shi_shen: p.shi_shen || '',
          cang_gan: p.cang_gan || [],
          na_yin: p.na_yin || '',
          kong_wang: p.kong_wang || '',
        }
      })
    },
    riGan() { return this.report?.basic_data?.ri_zhu?.gan || this.report?.result?.sec_1_overview?.ri_zhu?.gan || '' },
    riWx() { return this.report?.basic_data?.ri_zhu?.wu_xing || this.report?.result?.sec_1_overview?.ri_zhu?.wx || '' },
    genderText() { return this.meta.gender === '男' ? '男性' : '女性' },
    hourLabel() {
      const names = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
      return names[Math.floor((this.meta.hour||0)/2)] || '子'
    },

    sqrLabel() { return this.report?.result?.sec_3_shen_qiang_ruo?.label || '' },
    sqrScore() { return this.report?.result?.sec_3_shen_qiang_ruo?.score || 0 },
    sqrDetails() { return this.report?.result?.sec_3_shen_qiang_ruo?.details || null },
    sqrColorClass() {
      const l = this.sqrLabel
      if (l === '从弱') return 'color-gold'
      if (l === '身强') return this.sqrScore >= 70 ? 'color-gold' : 'color-green'
      if (l === '身弱') return 'color-blue'
      return 'color-yellow'
    },
    geDetail() { return this.report?.result?.sec_2_ge_ju?.detail || '' },
    geDesc() {
      const map = {
        '正官格':'为人正直守信，有管理才能',
        '七杀格':'魄力非凡，有闯劲，适合挑战性工作',
        '正财格':'求财踏实稳重，适合稳定收入',
        '偏财格':'财路宽广灵活，有投资天赋',
        '正印格':'学识渊博，有贵人运',
        '偏印格':'思维独特，有冷门专长',
        '食神格':'心态好福气厚，适合创意性工作',
        '伤官格':'才华横溢有灵气',
      }
      return map[this.geDetail] || ''
    },
    tiaoHou() {
      const v = this.report?.result?.sec_4_xi_yong?.tiao_hou
      if (Array.isArray(v)) return v[0] || ''
      return v || ''
    },
    xiArr() { return this.report?.result?.sec_4_xi_yong?.xi || [] },
    jiArr() { return this.report?.result?.sec_4_xi_yong?.ji || [] },
    qiYunAge() { return this.report?.result?.sec_1_overview?.qi_yun_age || '' },

    propertyPotential() { return this.report?.result?.sec_9_property?.property_potential || '' },
    propertyLevel() { return this.report?.result?.sec_9_property?.property_level || '' },

    wxEnergy() { return this.report?.analysis?.energy?.wu_xing_energy || {} },
    wxEnergyKeys() { return Object.keys(this.wxEnergy).filter(k => this.wxEnergy[k] > 0) },

    caiTotal() { return this.report?.result?.sec_8_wealth?.cai_xing_total || 0 },
    wealthLevel() { return this.report?.result?.sec_8_wealth?.wealth_level || '' },
    ck() { return this.report?.result?.sec_8_wealth?.cai_ku || {} },
    caiDetails() { return this.report?.result?.sec_8_wealth?.cai_xing_details || null },
    levelDesc() { return {'巨富':'亿万级别','大富':'数千万至亿级','中富':'百万至千万级','小富':'小康以上','一般':'普通水平'} },

    riskLevel() {
      const mf = this.report?.result?.sec_5_zai_huo?.misfortune_full || {}
      return mf.risk_level || ''
    },
    chongList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_chong || [] },
    xingList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_xing || [] },
    haiList() { return this.report?.result?.sec_5_zai_huo?.shen_sha_hai || [] },
    remissionAdvice() {
      const rm = this.report?.result?.sec_5_zai_huo?.remission_advice || {}
      return typeof rm === 'object' ? (rm.advice || '') : rm
    },

    riZhuBase() {
      const v = this.report?.result?.sec_6_character?.ri_zhu_base
      if (!v) return ''
      if (typeof v === 'object') return v.desc || v.base || ''
      return String(v)
    },
    personalityType() { return this.report?.result?.sec_6_character?.personality_type || '' },
    keyTraits() { return this.report?.result?.sec_6_character?.key_traits || [] },
    talents() { return this.report?.result?.sec_6_character?.talents || [] },

    riZhuAppearance() { return this.report?.result?.sec_7_appearance?.ri_zhu_appearance || '' },
    buildText() { const s7=this.report?.result?.sec_7_appearance||{}; return [s7.build, s7.height_estimate].filter(Boolean).join('，') },
    styleText() { return this.report?.result?.sec_7_appearance?.style || '' },
    weightTendency() { return this.report?.result?.sec_7_appearance?.weight_tendency || '' },

    careerDir() { return this.report?.result?.sec_10_career?.career_direction || '' },
    careerGrade() { return this.report?.result?.sec_10_career?.career_grade || '' },
    industry() { return this.report?.result?.sec_10_career?.recommended_industries || '' },
    ent() { return this.report?.result?.sec_10_career?.entrepreneurship || '' },
    bestPath() { return this.report?.result?.sec_10_career?.best_path || '' },

    eduLevel() { return this.report?.result?.sec_11_education?.display || this.report?.result?.sec_11_education?.school_level || '' },
    eduDetail() { const s11=this.report?.result?.sec_11_education||{}; return s11.year_pillar_check?.detail || s11.analysis || '' },
    ncShiShen() { const s11=this.report?.result?.sec_11_education||{}; return s11.nian_gan_check?.shi_shen || '' },

    marQuality() { return this.report?.result?.sec_12_marriage?.quality || '' },
    marScore() { return this.report?.result?.sec_12_marriage?.quality_score || '' },
    marWindow() { return this.report?.result?.sec_12_marriage?.best_window_age || '' },
    spouseTrait() { return this.report?.result?.sec_12_marriage?.spouse_trait || '' },

    childText() {
      const s13=this.report?.result?.sec_13_children||{}
      const c=s13.child_count_estimate
      return c ? (typeof c === 'object' ? (c.text || c.数量 || JSON.stringify(c)) : c) : ''
    },
    childAch() {
      const v = this.report?.result?.sec_13_children?.child_achievement
      if (!v) return ''
      if (typeof v === 'object') {
        const parts = []
        // 尝试提取关键信息
        if (v.子女方向) parts.push(v.子女方向)
        if (v.藏干信息 && Array.isArray(v.藏干信息)) {
          v.藏干信息.forEach(c => {
            if (c.含义) parts.push(c.含义)
          })
        }
        return parts.join('；') || JSON.stringify(v)
      }
      return String(v)
    },

    constitution() { return this.report?.result?.sec_14_health?.constitution || '' },
    wxOverThree() { return this.report?.result?.sec_14_health?.wu_xing_over_three || [] },

    familySummary() { const s15=this.report?.result?.sec_15_family||{}; return s15.summary || '' },
    familyEco() { const s15=this.report?.result?.sec_15_family||{}; return s15.family_economy || '' },
    familyPressure() { const s15=this.report?.result?.sec_15_family||{}; return s15.family_pressure || '' },

    eventsList() {
      const s16=this.report?.result?.sec_16_events||{}
      const ke=s16.key_events||{}
      const out=[]
      Object.entries(ke).forEach(([type,evts])=>{
        if(Array.isArray(evts)) evts.forEach(e=>{ if(e.year&&e.description) out.push(e) })
      })
      return out.sort((a,b)=>a.year-b.year)
    },

    dyList() {
      const list = this.report?.result?.sec_17_da_yun_detail?.list || []
      return list.map(d => ({...d, score: d.score || 5}))
    },
    bestDaYun() { return this.report?.result?.sec_1_overview?.best_da_yun || '' },
    bestDaYunLabel() { return this.report?.result?.sec_1_overview?.best_da_yun_label || '' },
    worstDaYun() { return this.report?.result?.sec_1_overview?.worst_da_yun || '' },
    worstDaYunLabel() { return this.report?.result?.sec_1_overview?.worst_da_yun_label || '' },

    verdicts() {
      const v = this.report?.result?.sec_18_verdicts
      if (Array.isArray(v)) return v
      if (v && Array.isArray(v.verdicts)) return v.verdicts
      return []
    },

    wxS20() { return this.report?.result?.sec_20_wu_xing_advice || {} },
    wxColors() { return this.wxS20.colors || '' },
    wxDirs() { return this.wxS20.directions || '' },
    wxJewel() { return this.wxS20.jewellery || '' },
    wxDiet() { return this.wxS20.diet || '' },
    wxNumbers() { return this.wxS20.lucky_numbers || '' },
    wxAdvice() { return this.wxS20.advice || '' },

    adviceItems() {
      const s21 = this.report?.result?.sec_21_advice || {}
      const items = []
      if(s21.career?.advice) items.push({icon:'🏢', label:'事业', text: s21.career.advice})
      if(s21.wealth?.advice) items.push({icon:'💰', label:'财富', text: s21.wealth.advice})
      if(s21.health?.advice) items.push({icon:'🏥', label:'健康', text: s21.health.advice})
      if(s21.marriage?.advice) items.push({icon:'💑', label:'婚姻', text: s21.marriage.advice})
      if(s21.life?.advice) items.push({icon:'🌟', label:'人生', text: s21.life.advice})
      return items
    },
  },
  methods: {
    ganWx(g) { return TIAN_GAN_WX[g] || '' },
    zhiWx(z) { return DI_ZHI_WX[z] || '' },
    formatCangGan(cg) {
      if (!cg) return ''
      if (typeof cg === 'string') return cg
      return cg.map(x => typeof x === 'object' ? (x.gan || x[0] || '') : x).join(' ')
    },
    ssClass(ss) {
      const xi = ['正印','偏印','比肩','劫财']
      const ji = ['七杀','伤官']
      if (xi.includes(ss)) return 'ss-xi'
      if (ji.includes(ss)) return 'ss-ji'
      if (ss === '正官') return 'ss-guan'
      if (ss === '正财' || ss === '偏财') return 'ss-cai'
      return ''
    },
    wxBarWidth(k) {
      const max = Math.max(...Object.values(this.wxEnergy), 1)
      return (this.wxEnergy[k] / max) * 100
    },
    wxColor(k) { return WU_XING_COLORS[k] || '#666' },
    dyClass(score) {
      if (!score) return ''
      if (score >= 8) return 'dy-gold'
      if (score >= 6) return 'dy-green'
      if (score >= 4) return 'dy-yellow'
      return 'dy-red'
    },
    dyTagClass(dy) {
      if (!dy.label) return ''
      if (dy.label.includes('🏆') || dy.label.includes('纯喜')) return 'tag-best'
      if (dy.label.includes('⚠️') || dy.label.includes('纯忌')) return 'tag-worst'
      if (dy.label.includes('天喜地忌') || dy.label.includes('天忌地喜')) return 'tag-mix'
      return 'tag-mid'
    },
    riskClass() {
      if (this.riskLevel.includes('高')) return 'risk-high'
      if (this.riskLevel.includes('中')) return 'risk-mid'
      return 'risk-low'
    },
    caiDetailLabel(k) {
      const map = { 'nian':'年','yue':'月','ri':'日','sg':'时干','sz':'时支' }
      return map[k] || k
    },
    toggleSec(sec) {
      this.expandedSec = this.expandedSec === sec ? '' : sec
    },
    async doDownloadPDF() {
      this.showToast('正在生成PDF...', 'info')
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
        this.showToast('PDF下载成功！', 'success')
      } catch (e) {
        console.error('PDF生成失败:', e)
        this.showToast('PDF生成失败: ' + e.message, 'error')
      }
    },
  },
}
</script>

<style scoped>
.report-page { padding-top: 4px; padding-bottom: 20px; }

.report-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; gap: 8px; flex-wrap: wrap;
}
.toolbar-right { display: flex; gap: 6px; align-items: center; }

.profile-card { background: linear-gradient(135deg,#1a1a35,#25254a); padding: 0; }
.profile-header { padding: 20px; text-align: center; }
.profile-name { font-size: 22px; font-weight: 700; letter-spacing: 1px; margin-bottom: 4px; }
.profile-meta { font-size: 12px; color: var(--m); display: flex; align-items: center; justify-content: center; gap: 2px; flex-wrap: wrap; }
.tag-gender { background: rgba(201,168,76,0.15); color: var(--g); padding: 1px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; }
.dot { color: rgba(255,255,255,0.12); margin: 0 4px; }
.bazi-display {
  font-size: 32px; font-weight: 700; color: var(--g); letter-spacing: 8px;
  padding: 12px 20px 14px; background: rgba(0,0,0,0.15); text-align: center;
  font-family: 'Noto Sans SC', serif;
}

.title-icon { opacity: 0.8; }
.title-badge { font-size: 10px; color: var(--m); font-weight: 400; margin-left: 6px; }

.pillar-table-wrap { overflow-x: auto; }
.pillar-table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 320px; }
.pillar-table thead th { padding: 8px 4px 6px; border-bottom: 1px solid rgba(201,168,76,0.15); }
.pillar-order { color: var(--g); font-size: 12px; font-weight: 600; }
.th-label { width: 40px; }
.td-label { color: var(--m); font-size: 10px; text-align: left; padding: 5px 4px 5px 6px; width: 40px; white-space: nowrap; border-bottom: 1px solid rgba(255,255,255,0.03); }
.pillar-table td { padding: 5px 4px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.03); }
.cell-tg { color: var(--g); font-weight: 700; font-size: 18px; }
.cell-dz { color: var(--g-light); font-weight: 700; font-size: 18px; }
.wx-sub { font-size: 9px; color: var(--m); font-weight: 400; display: block; margin-top: -2px; }
.cell-cg { font-size: 11px; color: var(--t); }
.cell-ny { font-size: 11px; color: rgba(232,212,139,0.7); }
.cell-kw { font-size: 11px; color: rgba(232,212,139,0.5); }
.cell-ss { font-size: 12px; font-weight: 600; }
.ss-xi { color: #4caf50; }
.ss-ji { color: #ff5722; }
.ss-guan { color: #2196f3; }
.ss-cai { color: var(--g); }

.core-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.core-item { background: rgba(0,0,0,0.15); border-radius: 8px; padding: 12px 8px; text-align: center; }
.core-item.wide { grid-column: span 1; }
.core-label { font-size: 10px; color: var(--m); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; }
.core-val { font-size: 18px; font-weight: 700; line-height: 1.2; }
.core-val.gold { color: var(--g); }
.core-val.sm { font-size: 13px; }
.core-val.danger { color: #ff5722; }
.score-sub { font-size: 11px; font-weight: 400; color: var(--m); margin-left: 2px; }
.color-gold { color: var(--g); }
.color-green { color: var(--green); }
.color-blue { color: #42a5f5; }
.color-yellow { color: var(--yellow); }

.wx-bars { display: flex; flex-direction: column; gap: 8px; }
.wx-bar-row { display: flex; align-items: center; gap: 8px; }
.wx-bar-label { width: 28px; font-size: 13px; font-weight: 600; color: var(--t); text-align: right; }
.wx-bar-track { flex: 1; height: 10px; background: rgba(255,255,255,0.06); border-radius: 5px; overflow: hidden; }
.wx-bar-fill { height: 100%; border-radius: 5px; transition: width 0.6s ease; }
.wx-bar-val { width: 24px; font-size: 11px; color: var(--m); text-align: right; }

.dy-timeline { display: flex; flex-direction: column; gap: 6px; }
.dy-seg { display: flex; align-items: stretch; gap: 8px; background: rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
.dy-indicator { width: 4px; min-height: 48px; border-radius: 2px; }
.dy-seg.dy-gold .dy-indicator { background: var(--g); }
.dy-seg.dy-green .dy-indicator { background: var(--green); }
.dy-seg.dy-yellow .dy-indicator { background: var(--yellow); }
.dy-seg.dy-red .dy-indicator { background: var(--red); }
.dy-body { flex: 1; padding: 8px 10px 8px 4px; }
.dy-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.dy-ganzhi { font-size: 16px; font-weight: 700; color: var(--g); }
.dy-label-tag { font-size: 9px; padding: 1px 6px; border-radius: 8px; white-space: nowrap; }
.tag-best { background: rgba(201,168,76,0.2); color: var(--g); }
.tag-worst { background: rgba(192,57,43,0.2); color: var(--red); }
.tag-mix { background: rgba(255,152,0,0.15); color: var(--yellow); }
.tag-mid { background: rgba(255,255,255,0.06); color: var(--m); }
.dy-bottom { display: flex; gap: 10px; margin-top: 2px; font-size: 10px; color: var(--m); }
.dy-score { margin-left: auto; font-weight: 600; color: var(--g); }

.dy-highlights { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; font-size: 12px; }
.dy-best { background: rgba(201,168,76,0.08); border-radius: 6px; padding: 6px 10px; color: var(--g); }
.dy-worst { background: rgba(192,57,43,0.08); border-radius: 6px; padding: 6px 10px; color: var(--red); }
.hl-icon { margin-right: 4px; }

.events-list { display: flex; flex-direction: column; gap: 6px; }
.event-item { display: flex; gap: 10px; background: rgba(0,0,0,0.08); border-radius: 6px; padding: 6px 10px; font-size: 13px; }
.event-year { color: var(--g); font-weight: 700; white-space: nowrap; min-width: 48px; }
.event-desc { color: var(--t); }

.report-body { display: flex; flex-direction: column; gap: 0; }
.sec-block { border-bottom: 1px solid rgba(255,255,255,0.04); }
.sec-block:last-child { border-bottom: none; }
.sec-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 0; cursor: pointer; user-select: none;
  font-size: 14px; font-weight: 600; color: var(--g);
  transition: color 0.2s;
}
.sec-header:hover { color: var(--g-light); }
.sec-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(201,168,76,0.1); color: var(--g);
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.sec-toggle { margin-left: auto; font-size: 12px; color: var(--m); }
.sec-content { padding: 0 0 12px; line-height: 2; font-size: 14px; }
.sec-content p { margin-bottom: 6px; }

.score-badge {
  display: inline-block; padding: 4px 14px; border-radius: 16px;
  font-size: 16px; font-weight: 700; margin-bottom: 8px;
}
.score-badge.color-gold { background: rgba(201,168,76,0.15); border: 1px solid var(--g); }
.score-badge.color-green { background: rgba(76,175,80,0.1); border: 1px solid var(--green); }
.score-badge.color-yellow { background: rgba(255,152,0,0.1); border: 1px solid var(--yellow); }
.score-badge.color-blue { background: rgba(66,165,245,0.1); border: 1px solid #42a5f5; }

.sqr-detail-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
.sqr-detail-item { background: rgba(0,0,0,0.08); border-radius: 6px; padding: 6px 8px; text-align: center; }
.sqr-detail-item.total { grid-column: 1/-1; background: rgba(201,168,76,0.08); }
.sqr-d-label { display: block; font-size: 9px; color: var(--m); }
.sqr-d-val { font-size: 16px; font-weight: 700; color: var(--t); }
.sqr-detail-item.total .sqr-d-val { color: var(--g); }

.xy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
.xy-item { border-radius: 8px; padding: 10px; text-align: center; }
.xi-box { background: rgba(76,175,80,0.08); border: 1px solid rgba(76,175,80,0.2); }
.ji-box { background: rgba(255,87,34,0.08); border: 1px solid rgba(255,87,34,0.2); }
.xy-label { font-size: 10px; color: var(--m); margin-bottom: 4px; }
.xy-val { font-size: 18px; font-weight: 700; }
.xi-box .xy-val { color: #4caf50; }
.ji-box .xy-val { color: #ff5722; }

.risk-badge { display: inline-block; padding: 3px 12px; border-radius: 12px; font-size: 12px; font-weight: 700; margin-bottom: 6px; }
.risk-high { background: rgba(192,57,43,0.2); color: var(--red); }
.risk-mid { background: rgba(255,152,0,0.15); color: var(--yellow); }
.risk-low { background: rgba(76,175,80,0.1); color: var(--green); }
.dz-rel-grid { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 4px; }
.rel-item { font-size: 12px; background: rgba(0,0,0,0.06); padding: 3px 10px; border-radius: 6px; }
.rel-icon { margin-right: 3px; }

.tag-list { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }
.tag { background: rgba(201,168,76,0.1); color: var(--g); padding: 2px 10px; border-radius: 10px; font-size: 11px; }
.talent-list { margin-bottom: 6px; font-size: 13px; }

.wealth-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 4px; }
.wealth-score { font-size: 32px; font-weight: 700; color: var(--g); }
.ws-unit { font-size: 14px; font-weight: 400; color: var(--m); }
.wealth-level { font-size: 16px; color: var(--g-light); }
.ck-box { background: rgba(201,168,76,0.08); border-radius: 6px; padding: 6px 10px; font-size: 12px; margin: 6px 0; }
.cai-detail-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 4px; margin: 6px 0; }
.cai-d-item { background: rgba(0,0,0,0.06); border-radius: 4px; padding: 4px; text-align: center; }
.cai-d-label { display: block; font-size: 9px; color: var(--m); }
.cai-d-val { font-size: 14px; font-weight: 600; color: var(--g); }

.ent-box { background: rgba(255,152,0,0.06); border-radius: 6px; padding: 6px 10px; font-size: 13px; }
.path-box { background: rgba(201,168,76,0.06); border-radius: 6px; padding: 6px 10px; font-size: 13px; }

.edu-badge { display: inline-block; background: rgba(76,175,80,0.12); color: #4caf50; padding: 3px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-bottom: 6px; }

.mar-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.mar-badge { background: rgba(201,168,76,0.12); color: var(--g); padding: 3px 12px; border-radius: 12px; font-weight: 600; font-size: 14px; }
.mar-score { font-size: 12px; color: var(--m); }

.health-warn { background: rgba(192,57,43,0.06); border-radius: 6px; padding: 6px 10px; font-size: 12px; margin-bottom: 4px; }

.dy-detail-row { display: flex; padding: 6px 10px; border-radius: 6px; margin-bottom: 3px; font-size: 13px; }
.dy-detail-row.dy-gold { background: rgba(201,168,76,0.08); }
.dy-detail-row.dy-green { background: rgba(76,175,80,0.06); }
.dy-detail-row.dy-yellow { background: rgba(255,152,0,0.05); }
.dy-detail-row.dy-red { background: rgba(192,57,43,0.04); }
.dd-top { display: flex; align-items: center; gap: 8px; width: 100%; }
.dd-ganzhi { font-weight: 700; color: var(--g); min-width: 52px; }
.dd-age { font-size: 11px; color: var(--m); }
.dd-score { font-size: 11px; font-weight: 600; color: var(--t); margin-left: auto; }
.dd-label-tag { font-size: 9px; padding: 1px 6px; border-radius: 8px; }

.verdict-card { background: rgba(0,0,0,0.06); border-radius: 6px; padding: 8px 12px; margin-bottom: 4px; }
.vd-title { font-size: 12px; color: var(--g); font-weight: 600; }
.vd-body { font-size: 13px; line-height: 1.6; }

.wx-adv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.wa-item { display: flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.06); border-radius: 6px; padding: 6px 10px; font-size: 13px; }
.wa-item.full { grid-column: 1/3; }
.wa-icon { font-size: 14px; }
.wa-label { font-size: 10px; color: var(--m); flex-shrink: 0; }
.wa-val { color: var(--t); }

.advice-card { background: linear-gradient(135deg,rgba(201,168,76,0.04),rgba(201,168,76,0.01)); border: 1px solid rgba(201,168,76,0.08); }
.advice-list { display: flex; flex-direction: column; gap: 8px; }
.advice-item { display: flex; gap: 10px; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 10px 12px; }
.advice-icon { font-size: 20px; width: 28px; text-align: center; flex-shrink: 0; }
.advice-label { font-size: 11px; color: var(--g); font-weight: 600; margin-bottom: 2px; }
.advice-text { font-size: 13px; line-height: 1.6; color: var(--t); }

.report-footer { text-align: center; padding: 20px 0 8px; font-size: 11px; color: var(--m); }
.footer-time { font-size: 10px; color: rgba(138,128,112,0.4); margin-top: 2px; }

.raw-data {
  background: #0a0a12; border-radius: 8px; padding: 14px; margin-top: 12px;
  font-family: monospace; font-size: 10px; color: #666; white-space: pre-wrap;
  max-height: 400px; overflow: auto;
}

@media print {
  .report-toolbar, .raw-data { display: none!important; }
  body { background: #fff!important; color: #222!important; }
  .card { background: #fff!important; border: 1px solid #ddd!important; break-inside: avoid; }
  .profile-card { background: #f8f6f0!important; }
  .core-item { background: #f5f5f5!important; }
  .wx-bar-track { background: #eee!important; }
}

@media (max-width: 480px) {
  .core-grid { grid-template-columns: 1fr 1fr; }
  .core-item.wide { grid-column: 1/3; }
  .xy-grid { grid-template-columns: 1fr; }
  .sqr-detail-grid { grid-template-columns: 1fr 1fr; }
  .cai-detail-grid { grid-template-columns: repeat(3,1fr); }
  .wx-adv-grid { grid-template-columns: 1fr; }
  .wa-item.full { grid-column: 1; }
  .dy-bottom { flex-wrap: wrap; gap: 4px; }
  .cell-tg, .cell-dz { font-size: 16px; }
}
</style>
