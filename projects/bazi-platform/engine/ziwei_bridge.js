#!/usr/bin/env node
/**
 * 金鉴真人 · 紫微斗数桥接层 v1.0
 * =================================
 * 直接调用 iztro（MIT）生成紫微斗数命盘，输出完整 JSON（含命主/身主/12宫/长生博士12神）。
 * 不依赖第三方 CLI 的字段裁剪；第三方 skill 仅作交叉参考。
 *
 * 用法: node ziwei_bridge.js <公历YYYY-M-D> <时辰索引0-12> <男|女>
 *   时辰索引: 0早子 1丑 2寅 3卯 4辰 5巳 6午 7未 8申 9酉 10戌 11亥 12晚子
 */
const path = require('path');

function loadIztro() {
  const candidates = [
    path.resolve(__dirname, '../../skills/bazi/bazi-ziwei/scripts/node_modules/iztro'),
    '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-ziwei/scripts/node_modules/iztro',
    'iztro',
  ];
  for (const c of candidates) {
    try { return require(c); } catch (e) { /* next */ }
  }
  throw new Error('未能加载 iztro，请先执行: cd skills/bazi/bazi-ziwei/scripts && npm install');
}

const { astro } = loadIztro();
const [dateStr, timeIdx, gender] = process.argv.slice(2);
if (!dateStr || timeIdx === undefined || !gender) {
  console.error('用法: node ziwei_bridge.js <公历YYYY-M-D> <时辰索引0-12> <男|女>');
  process.exit(1);
}

const a = astro.bySolar(dateStr, Number(timeIdx), gender, true, 'zh-CN');

const palaces = a.palaces.map((p) => ({
  name: p.name,
  heavenlyStem: p.heavenlyStem,
  earthlyBranch: p.earthlyBranch,
  isBodyPalace: p.isBodyPalace,
  majorStars: (p.majorStars || []).map((s) => ({ name: s.name, brightness: s.brightness, mutagen: s.mutagen })),
  minorStars: (p.minorStars || []).map((s) => ({ name: s.name, brightness: s.brightness, mutagen: s.mutagen })),
  adjectiveStars: (p.adjectiveStars || []).map((s) => (typeof s === 'string' ? s : s.name)),
  decadalRange: p.decadal ? p.decadal.range : null,
  ages: p.ages || null,
  changsheng12: p.changsheng12 || null,
  boshi12: p.boshi12 || null,
  jiangqian12: p.jiangqian12 || null,
  suiqian12: p.suiqian12 || null,
}));

console.log(JSON.stringify({
  soul: a.soul,
  body: a.body,
  fiveElementsClass: a.fiveElementsClass,
  lunarDate: a.lunarDate,
  chineseDate: a.chineseDate,
  solarDate: a.solarDate,
  time: a.time,
  timeRange: a.timeRange,
  zodiac: a.zodiac,
  sign: a.sign,
  palaces,
}, null, 1));
