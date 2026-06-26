/**
 * 金鉴真人·八字平台 v2.0 — 前端应用
 * 用户输入出生日期，前端调用API，引擎内部完成排盘+分析
 */

// 配置
const CONFIG = {
    API_BASE: '/api/v1',
    DEMO_ENABLED: true,
};

// ── 工具 ──
const $ = id => document.getElementById(id);
const qs = sel => document.querySelector(sel);
const qsa = sel => document.querySelectorAll(sel);

// ── API调用 ──
async function apiCall(path, data = null, method = 'GET') {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) opts.body = JSON.stringify(data);
    try {
        const res = await fetch(`${CONFIG.API_BASE}${path}`, opts);
        return await res.json();
    } catch (e) {
        return { error: `网络错误: ${e.message}` };
    }
}

// ── 导航 ──
function navigate(page) {
    qsa('.page').forEach(p => p.classList.remove('active'));
    qsa('.nav-btn').forEach(b => b.classList.remove('active'));
    const el = $(`page-${page}`);
    if (el) el.classList.add('active');
    const btn = qs(`[data-page="${page}"]`);
    if (btn) btn.classList.add('active');
    window.scrollTo(0, 0);
}

// ── 页面初始化 ──
document.addEventListener('DOMContentLoaded', () => {
    // 默认填家主八字示例
    $('name').value = '测试';
    $('gender-male').checked = true;
    $('birth-date').value = '1979-07-15';
    $('birth-hour').value = '4';
    $('birth-minute').value = '0';
});

// ── 提交分析 (核心功能) ──
async function submitAnalyze() {
    const btn = $('btn-analyze');
    const loading = $('loading-analyze');
    const resultDiv = $('result-display');
    const debugDiv = $('debug-json');

    // 收集输入
    const name = $('name').value.trim() || '未知';
    const gender = $('gender-male').checked ? '男' : '女';
    const dateStr = $('birth-date').value;
    const hour = parseInt($('birth-hour').value) || 0;
    const minute = parseInt($('birth-minute').value) || 0;

    if (!dateStr) {
        alert('请选择出生日期');
        return;
    }

    const parts = dateStr.split('-');
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]);
    const day = parseInt(parts[2]);

    // 显示加载
    btn.style.display = 'none';
    loading.style.display = 'inline';
    resultDiv.style.display = 'none';
    debugDiv.style.display = 'none';

    // 调用API
    const data = {
        name, gender,
        birth_year: year, birth_month: month, birth_day: day,
        birth_hour: hour, birth_minute: minute,
    };

    // 先调debug接口看完整JSON
    const raw = await apiCall('/engine/debug', data, 'POST');

    btn.style.display = 'inline';
    loading.style.display = 'none';

    if (raw.error) {
        resultDiv.innerHTML = `<div class="error-box">❌ ${raw.error}</div>`;
        resultDiv.style.display = 'block';
        return;
    }

    // 显示JSON调试
    debugDiv.textContent = JSON.stringify(raw, null, 2);
    debugDiv.style.display = 'block';

    // 渲染报告
    renderReport(raw, resultDiv);
    resultDiv.style.display = 'block';
}

// ── 渲染报告 ──
function renderReport(data, container) {
    const result = data.result || data;
    const basic = data.basic_data || data.paipan || {};
    const analysis = data.analysis || {};

    const s1 = result.sec_1_overview || {};
    const s3 = result.sec_3_shen_qiang_ruo || {};
    const s4 = result.sec_4_xi_yong || {};
    const s8 = result.sec_8_wealth || {};
    const s10 = result.sec_10_career || {};
    const s11 = result.sec_11_education || {};
    const s12 = result.sec_12_marriage || {};
    const s13 = result.sec_13_children || {};
    const s14 = result.sec_14_health || {};
    const s17 = result.sec_17_da_yun_detail || {};
    const s18 = result.sec_18_verdicts || [];
    const s20 = result.sec_20_wu_xing_advice || {};

    // 八字
    const baziStr = s1.bazi || (basic.paipan && basic.paipan.bazi) || '';

    // 身强弱
    const sqrLabel = s3.label || (analysis.shen_qiang_ruo && analysis.shen_qiang_ruo.label) || '';
    const sqrScore = s3.score || (analysis.shen_qiang_ruo && analysis.shen_qiang_ruo.score) || 0;

    // 财星
    const caiTotal = s8.cai_xing_total || (analysis.cai_xing && analysis.cai_xing.total) || 0;
    const wealthLevel = s8.wealth_level || '';

    // 格局
    const geJu = result.sec_2_ge_ju || {};
    const geJuDetail = geJu.detail || (analysis.ge_ju && analysis.ge_ju.detail) || '';

    // 喜用
    const xiArr = s4.xi || (analysis.xi_yong_shen && analysis.xi_yong_shen.xi) || [];
    const jiArr = s4.ji || (analysis.xi_yong_shen && analysis.xi_yong_shen.ji) || [];

    // 大运
    const dyList = s17.list || (analysis.da_yun && analysis.da_yun.list) || [];

    // 维度
    const dims = analysis.dimensions || {};

    // ── 组装HTML ──
    let html = `<div class="report-card">`;

    // §1 总览
    html += `<div class="sec"><h3>📋 八字总览</h3>
        <div class="bazi-large">${baziStr}</div>
        <div class="tags"><span>${sqrLabel}${sqrScore}分</span><span>💰${caiTotal}分</span><span>${geJuDetail}</span></div>
        <div class="info-row">喜用: <strong>${xiArr.join(' ')}</strong> | 忌: <strong>${jiArr.join(' ')}</strong></div>
    </div>`;

    // §8 财富
    html += `<div class="sec"><h3>💰 财富</h3>
        <div class="big-num">${caiTotal}<span class="unit">分</span></div>
        <div class="label">等级: ${wealthLevel}</div>
    </div>`;

    // §10 事业
    const careerDir = s10.career_direction || '';
    const careerGrade = s10.career_grade || '';
    html += `<div class="sec"><h3>🏢 事业</h3>
        <div class="label">方向: ${careerDir}</div>
        <div class="label">等级: ${careerGrade}</div>
        <div class="label">行业: ${s10.recommended_industries || ''}</div>
    </div>`;

    // §11 学历
    const eduDisplay = s11.display || s11.school_level || '';
    html += `<div class="sec"><h3>🎓 学历</h3>
        <div class="label">${eduDisplay}</div>
    </div>`;

    // §12 婚姻
    const marQuality = s12.quality || '';
    const marScore = s12.quality_score || '';
    html += `<div class="sec"><h3>❤️ 婚姻</h3>
        <div class="label">质量: ${marQuality}(${marScore}/10)</div>
        <div class="label">最佳窗口: ${s12.best_window_age || ''}</div>
        <div class="label">配偶: ${s12.spouse_trait || ''}</div>
    </div>`;

    // §13 子女
    html += `<div class="sec"><h3>👶 子女</h3>
        <div class="label">数量: ${s13.child_count_estimate || ''}</div>
        <div class="label">成就: ${s13.child_achievement || ''}</div>
    </div>`;

    // §14 健康
    html += `<div class="sec"><h3>🏥 健康</h3>
        <div class="label">体质: ${s14.constitution || ''}</div>
    </div>`;

    // §17 大运
    if (dyList.length > 0) {
        html += `<div class="sec"><h3>🚀 大运</h3>`;
        dyList.forEach(dy => {
            const star = dy.score >= 8 ? '🏆' : dy.score >= 6 ? '✅' : dy.score >= 4 ? '⚠️' : '❌';
            html += `<div class="dy-row">${star} ${dy.gan_zhi} (${dy.start_age}~${dy.end_age}岁) ${dy.score}/10</div>`;
        });
        html += `</div>`;
    }

    // §18 三决断
    if (s18.length > 0) {
        html += `<div class="sec"><h3>🎯 三决断</h3>`;
        s18.forEach(v => {
            html += `<div class="verdict"><strong>${v.title || ''}</strong>: ${v.event || ''}</div>`;
        });
        html += `</div>`;
    }

    // §20 五行补充
    html += `<div class="sec"><h3>🌈 五行开运</h3>
        <div class="info-row">🎨 颜色: ${s20.colors || ''}</div>
        <div class="info-row">🧭 方向: ${s20.directions || ''}</div>
        <div class="info-row">💎 饰品: ${s20.jewellery || ''}</div>
        <div class="info-row">🥗 饮食: ${s20.diet || ''}</div>
    </div>`;

    // 维度
    if (Object.keys(dims).length > 0) {
        html += `<div class="sec"><h3>📊 八维评分</h3>`;
        Object.entries(dims).forEach(([name, ds]) => {
            const total = ds.total || 0;
            const pct = (total / 10) * 100;
            const color = total >= 7 ? '#4caf50' : total >= 5 ? '#d4a853' : '#e94560';
            html += `<div class="dim-row">
                <div class="dim-name">${name}</div>
                <div class="dim-bar"><div class="dim-fill" style="width:${pct}%;background:${color}"></div></div>
                <div class="dim-score">${total}/10</div>
            </div>`;
        });
        html += `</div>`;
    }

    html += `</div>`;

    container.innerHTML = html;
}

// ── 填充示例 ──
function fillSample(index) {
    const samples = [
        { name: '家主', date: '1979-07-15', hour: '4', gender: '男' },
        { name: '子源', date: '2011-04-25', hour: '10', gender: '男' },
        { name: '立', date: '2011-04-25', hour: '12', gender: '男' },
    ];
    const s = samples[index] || samples[0];
    $('name').value = s.name;
    $('birth-date').value = s.date;
    $('birth-hour').value = s.hour;
    if (s.gender === '男') $('gender-male').checked = true;
    else $('gender-female').checked = true;
}
