#!/usr/bin/env node

try {
  require.resolve('lunar-javascript');
  require.resolve('iztro');
} catch (e) {
  console.log("检测到缺少必要依赖，正在自动执行 npm install 安装，请稍候...");
  try {
    const cp = require('child_process');
    cp.execSync('npm install --no-audit --no-fund', { cwd: __dirname, stdio: 'inherit' });
  } catch (err) {
    console.error(JSON.stringify({ 
      error: `依赖自动安装失败。请手动进入目录执行安装命令：\ncd "${__dirname}" && npm install` 
    }));
    process.exit(1);
  }
}

const { Lunar, Solar } = require('lunar-javascript');
const iztro = require('iztro');

// 0. 全国主要省市经度数据库 (用于真太阳时联动)
const PROVINCE_CITY_DB = {
  "北京": { "北京": 120.0 },
  "天津": { "天津": 117.2 },
  "上海": { "上海": 121.47 },
  "重庆": { "重庆": 106.55 },
  "河北": { "石家庄": 114.48, "唐山": 118.02, "秦皇岛": 119.57, "邯郸": 114.47, "邢台": 114.48, "保定": 115.48, "张家口": 114.88, "承德": 117.93, "沧州": 116.83, "廊坊": 116.7, "衡水": 115.68 },
  "山西": { "太原": 112.53, "大同": 113.3, "阳泉": 113.57, "长治": 113.13, "晋城": 112.83, "朔州": 112.43, "晋中": 112.75, "运城": 111.0, "忻州": 112.73, "临汾": 111.52, "吕梁": 111.13 },
  "内蒙古": { "呼和浩特": 111.65, "包头": 109.8, "乌海": 106.82, "赤峰": 118.97, "通辽": 122.27, "鄂尔多斯": 109.98, "呼伦贝尔": 119.77, "巴彦淖尔": 107.42, "乌兰察布": 113.07, "兴安盟": 122.05, "锡林郭勒盟": 116.08, "阿拉善盟": 105.67 },
  "辽宁": { "沈阳": 123.38, "大连": 121.62, "鞍山": 122.98, "抚顺": 123.97, "本溪": 123.77, "丹东": 124.37, "锦州": 121.13, "营口": 122.23, "阜新": 121.65, "辽阳": 123.18, "盘锦": 122.07, "铁岭": 123.85, "朝阳": 120.45, "葫芦岛": 120.83 },
  "吉林": { "长春": 125.35, "吉林": 126.57, "四平": 124.37, "辽源": 125.13, "通化": 125.93, "白山": 126.42, "松原": 124.82, "白城": 122.83, "延边": 129.5 },
  "黑龙江": { "哈尔滨": 126.63, "齐齐哈尔": 123.97, "鸡西": 130.97, "鹤岗": 130.27, "双鸭山": 131.17, "大庆": 125.03, "伊春": 128.9, "佳木斯": 130.35, "七台河": 131.0, "牡丹江": 129.6, "黑河": 127.48, "绥化": 127.0, "大兴安岭": 124.72 },
  "江苏": { "南京": 118.78, "无锡": 120.29, "徐州": 117.2, "常州": 119.95, "苏州": 120.62, "南通": 120.86, "连云港": 119.17, "淮安": 119.15, "盐城": 120.13, "扬州": 119.42, "镇江": 119.44, "泰州": 119.9, "宿迁": 118.3 },
  "浙江": { "杭州": 120.15, "宁波": 121.56, "温州": 120.65, "嘉兴": 120.76, "湖州": 120.1, "绍兴": 120.58, "金华": 119.64, "衢州": 118.88, "舟山": 122.2, "台州": 121.43, "丽水": 119.92 },
  "安徽": { "合肥": 117.27, "芜湖": 118.38, "蚌埠": 117.38, "淮南": 117.0, "马鞍山": 118.48, "淮北": 116.78, "铜陵": 117.82, "安庆": 117.03, "黄山": 118.3, "滁州": 118.3, "阜阳": 115.82, "宿州": 116.98, "六安": 116.5, "亳州": 115.78, "池州": 117.05, "宣城": 118.75 },
  "福建": { "福州": 119.3, "厦门": 118.1, "莆田": 119.0, "三明": 117.63, "泉州": 118.58, "漳州": 117.65, "南平": 118.17, "龙岩": 117.03, "宁德": 119.52 },
  "江西": { "南昌": 115.89, "景德镇": 117.2, "萍乡": 113.85, "九江": 115.97, "新余": 114.93, "鹰潭": 117.02, "赣州": 114.92, "吉安": 114.98, "宜春": 114.38, "抚州": 116.35, "上饶": 117.97 },
  "山东": { "济南": 117.0, "青岛": 120.33, "淄博": 118.05, "枣庄": 117.57, "东营": 118.48, "烟台": 121.4, "潍坊": 119.1, "济宁": 116.58, "泰安": 117.13, "威海": 122.1, "日照": 119.48, "临沂": 118.35, "德州": 116.28, "聊城": 115.98, "滨州": 118.03, "菏泽": 115.48 },
  "河南": { "郑州": 113.65, "开封": 114.35, "洛阳": 112.43, "平顶山": 113.3, "安阳": 114.35, "鹤壁": 114.17, "新乡": 113.85, "焦作": 113.23, "濮阳": 115.02, "许昌": 113.82, "漯河": 114.02, "三门峡": 111.2, "南阳": 112.53, "商丘": 115.65, "信阳": 114.08, "周口": 114.63, "驻马店": 114.02, "济源": 112.6 },
  "湖北": { "武汉": 114.3, "黄石": 115.08, "十堰": 110.78, "宜昌": 111.3, "襄阳": 112.13, "鄂州": 114.88, "荆门": 112.2, "孝感": 113.92, "荆州": 112.23, "黄冈": 114.87, "咸宁": 114.32, "随州": 113.37, "恩施": 109.48, "仙桃": 113.43, "潜江": 112.9, "天门": 113.17, "神农架": 110.67 },
  "湖南": { "长沙": 113.0, "株洲": 113.15, "湘潭": 112.9, "衡阳": 112.6, "邵阳": 111.5, "岳阳": 113.1, "常德": 111.68, "张家界": 110.48, "益阳": 112.33, "郴州": 113.02, "永州": 111.62, "怀化": 110.0, "娄底": 111.98, "湘西": 109.73 },
  "广东": { "广州": 113.26, "深圳": 114.07, "珠海": 113.52, "汕头": 116.68, "韶关": 113.6, "佛山": 113.12, "江门": 113.08, "湛江": 110.3, "湛江廉江": 110.28, "茂名": 110.87, "肇庆": 112.47, "惠州": 114.4, "梅州": 116.12, "汕尾": 115.35, "河源": 114.7, "阳江": 111.95, "清远": 113.03, "东莞": 113.75, "中山": 113.38, "潮州": 116.63, "揭阳": 116.35, "云浮": 112.03 },
  "广西": { "南宁": 108.33, "柳州": 109.4, "桂林": 110.28, "梧州": 111.33, "北海": 109.12, "防城港": 108.35, "钦州": 108.62, "贵港": 109.6, "玉林": 110.15, "百色": 106.62, "贺州": 111.55, "河池": 108.07, "来宾": 109.23, "崇左": 107.38 },
  "海南": { "海口": 110.35, "三亚": 109.5, "三沙": 112.33 },
  "四川": { "成都": 104.06, "自贡": 104.78, "攀枝花": 101.72, "泸州": 105.43, "德阳": 104.38, "绵阳": 104.73, "广元": 105.82, "遂宁": 105.58, "内江": 105.05, "乐山": 103.75, "南充": 106.08, "眉山": 103.83, "宜宾": 104.62, "广安": 106.63, "达州": 107.5, "雅安": 103.0, "巴中": 106.75, "资阳": 104.62, "阿坝": 102.22, "甘孜": 101.95, "凉山": 102.25 },
  "贵州": { "贵阳": 106.7, "六盘水": 104.83, "遵义": 106.9, "安顺": 105.93, "铜仁": 109.2, "黔西南": 104.9, "毕节": 105.28, "黔东南": 107.97, "黔南": 107.52 },
  "云南": { "昆明": 102.73, "曲靖": 103.8, "玉溪": 102.55, "保山": 99.17, "昭通": 103.72, "丽江": 100.23, "普洱": 100.97, "临沧": 100.08, "楚雄": 101.53, "红河": 103.4, "文山": 104.25, "西双版纳": 100.8, "大理": 100.22, "德宏": 98.58, "怒江": 98.85, "迪庆": 99.7 },
  "西藏": { "拉萨": 91.11, "日喀则": 88.88, "昌都": 97.18, "林芝": 94.37, "山南": 91.77, "那曲": 92.05, "阿里": 80.1 },
  "陕西": { "西安": 108.94, "铜川": 109.08, "宝鸡": 107.13, "咸阳": 108.7, "渭南": 109.5, "延安": 109.48, "汉中": 107.02, "榆林": 109.73, "安康": 109.02, "商洛": 109.93 },
  "甘肃": { "兰州": 103.82, "嘉峪关": 98.28, "金昌": 102.18, "白银": 104.18, "天水": 105.72, "武威": 102.63, "张掖": 100.45, "平凉": 106.68, "酒泉": 98.52, "庆阳": 107.63, "定西": 104.62, "陇南": 104.92, "临夏": 103.22, "甘南": 102.92 },
  "青海": { "西宁": 101.77, "海东": 102.1, "海北": 100.9, "黄南": 102.02, "海南州": 100.62, "果洛": 100.22, "玉树": 97.02, "海西": 97.37 },
  "宁夏": { "银川": 106.27, "石嘴山": 106.38, "吴忠": 106.2, "固原": 106.28, "中卫": 105.18 },
  "新疆": { "乌鲁木齐": 87.68, "克拉玛依": 84.88, "吐鲁番": 89.18, "哈密": 93.52, "昌吉": 87.3, "博尔塔拉": 82.08, "巴音郭楞": 86.15, "阿克苏": 80.27, "克孜勒苏": 76.17, "喀什": 75.98, "和田": 79.93, "伊犁": 81.33, "塔城": 82.98, "阿勒泰": 88.13, "石河子": 86.03 },
  "Taiwan": { "台北": 121.5, "高雄": 120.3, "台中": 120.68 },
  "香港": { "香港": 114.17 },
  "澳门": { "澳门": 113.53 }
};

// 1. 五行基础属性字典
const GAN_WUXING = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水'
};

const ZHI_WUXING = {
  '寅': '木', '卯': '木',
  '巳': '火', '午': '火',
  '申': '金', '酉': '金',
  '亥': '水', '子': '水',
  '辰': '土', '戌': '土', '丑': '土', '未': '土'
};

const ZHI_HIDE_GAN = {
  '子': [{ gan: '癸', weight: 10 }],
  '丑': [{ gan: '己', weight: 7 }, { gan: '癸', weight: 2 }, { gan: '辛', weight: 1 }],
  '寅': [{ gan: '甲', weight: 7 }, { gan: '丙', weight: 2 }, { gan: '戊', weight: 1 }],
  '卯': [{ gan: '乙', weight: 10 }],
  '辰': [{ gan: '戊', weight: 7 }, { gan: '乙', weight: 2 }, { gan: '癸', weight: 1 }],
  '巳': [{ gan: '丙', weight: 7 }, { gan: '庚', weight: 2 }, { gan: '戊', weight: 1 }],
  '午': [{ gan: '丁', weight: 7 }, { gan: '己', weight: 3 }],
  '未': [{ gan: '己', weight: 7 }, { gan: '丁', weight: 2 }, { gan: '乙', weight: 1 }],
  '申': [{ gan: '庚', weight: 7 }, { gan: '壬', weight: 2 }, { gan: '戊', weight: 1 }],
  '酉': [{ gan: '辛', weight: 10 }],
  '戌': [{ gan: '戊', weight: 7 }, { gan: '辛', weight: 2 }, { gan: '丁', weight: 1 }],
  '亥': [{ gan: '壬', weight: 7 }, { gan: '甲', weight: 3 }]
};

const STAR_INTERPRETATIONS = {
  '紫微': {
    '命宫': '紫微星入命，代表有帝王之气，自尊心强，稳重高贵。具有卓越的管理和领导才能，但也容易流于独断专行、爱面子、喜好奉承。',
    '夫妻宫': '配偶气质高雅，有责任感，但也带有一定支配欲。感情生活注重体面，容易因为面子或性格刚强产生小摩擦。',
    '财帛宫': '财源稳定，善于经营大额财物，投资稳健，能得贵人相助而进财。',
    '官禄宫': '事业心重，适合担任管理、行政、公职或大型机构骨干，升迁运极佳。'
  },
  '天机': {
    '命宫': '天机星为智多星，聪明伶俐，思维敏捷，善于策划和研究。然而心思较敏感多虑，易神经衰弱、多思失眠。',
    '夫妻宫': '配偶聪明机智，心思细腻。但感情容易多变 or 多思虑，适合年龄有一定差距的结合。',
    '财帛宫': '财运多变动，属于劳心赚取“智力财”的命格，适合做设计、创意或咨询顾问得财。',
    '官禄宫': '适合从事脑力劳动、企划、高新科技或媒体行业，不宜死板工作，事业多变动发展。'
  },
  '太阳': {
    '命宫': '太阳代表光明、博爱、奉献。性格开朗大方，乐于助人，但有时过于爱出风头，一生奔波操劳。',
    '夫妻宫': '配偶性格开朗外向，做事积极。男命易得贤妻，女命则需防丈夫脾气稍显急躁。',
    '财帛宫': '财源广进，但开销也大，喜面子，花钱慷慨，宜防财来财去，多做固定资产投资。',
    '官禄宫': '适合从事外交、销售、政治、教育等需要公众曝光或服务大众的行业，事业名大于利。'
  },
  '武曲': {
    '命宫': '武曲为正财星、将星。性格刚毅刚直，作风果断，执行力极强。但人际交往中略嫌严厉，女命则易显得过于刚强。',
    '夫妻宫': '感情偏于理智、冷淡。配偶性格刚毅、重实际。宜多沟通，减少争执。',
    '财帛宫': '财运极旺！正财星落本位，善于理财、投资及白手起家。适合经商或金融、制造行业. ',
    '官禄宫': '事业稳健，适合金融、军事、警察、五金制造或实体企业经营，做事铁面无私。'
  },
  '天同': {
    '命宫': '天同为福星，性格温和谦逊，知足常乐，人缘极佳，追求精神享受。但有时缺乏进取心，易流于懒散。',
    '夫妻宫': '夫妻感情深厚甜蜜。配偶性格温和体贴，懂得生活情趣，家庭氛围温馨谐和。',
    '财帛宫': '财源平稳，多为“白手起家”或“晚发”之财。不宜过度投机，安稳打工亦能衣食无忧。',
    '官禄宫': '适合从事服务业、文教、艺术、休闲或公关等行业，工作环境通常比较轻松愉快。'
  },
  '廉贞': {
    '命宫': '廉贞是次桃花、囚星。性格多面，有野心、有才华、重感情，但脾气傲慢，容易偏执，带有一股邪气与叛逆。',
    '夫妻宫': '感情生活多姿多彩，配偶多才多艺、风趣幽默，但也需防防范婚姻外的桃花困扰。',
    '财帛宫': '财运起伏较大，善于以偏门、交际或演艺创意得财，需防因官非或人际纠纷破财。',
    '官禄宫': '适合军警、公职、电子科技、公关或艺术时尚行业，工作表现积极，竞争心强。'
  },
  '天府': {
    '命宫': '天府为库星，温和儒雅，注重物质享受，做事稳扎稳打，极具包容力，但容易安于现状。',
    '夫妻宫': '配偶能力强，善于理财，家庭生活安定踏实，多能得配偶助力。',
    '财帛宫': '财运亨通，善于储蓄和守财，一生衣食无忧，多为中产以上富足生活。',
    '官禄宫': '事业稳定，适合在大型企业、银行或政府机关负责资产管理、行政后勤等稳健工作。'
  },
  '太阴': {
    '命宫': '太阴代表月亮，温柔内敛，心思细腻，注重生活品质与精神修养，人缘极好，但略显多愁善感。',
    '夫妻宫': '男命易娶贤惠美丽的妻子，女命则易嫁温文尔雅、体贴温柔的丈夫，感情深厚。',
    '财帛宫': '财源细水长流，偏财运佳，善于以不动产、理财 or 文创行业进财，一生财务状况安稳。',
    '官禄宫': '适合从事房地产、财务、行政、文教或夜间性质行业，工作表现有条不紊。'
  },
  '贪狼': {
    '命宫': '贪狼为正桃花星，欲望之神。交际手腕圆滑，多才多艺，喜好交友与享乐，对玄学宗教亦有独特天赋，但需防博而不精。',
    '夫妻宫': '感情生活多姿多彩，配偶多才多艺、风趣幽默，但也需防防范婚姻外的桃花困扰。',
    '财帛宫': '财运波动，多为偏财、交际财。善于应酬，容易在娱乐、公关、投资等领域暴发，但花钱也大方。',
    '官禄宫': '适合从事公关、娱乐、艺术、餐饮旅游、或者偏门行业，事业具有开拓性。'
  },
  '巨门': {
    '命宫': '巨门为暗曜，主口舌是非。心思细腻，观察力敏锐，辩才无碍。但也容易多疑、言多必失，招惹人际摩擦。',
    '夫妻宫': '夫妻容易因口舌、意见不合产生争执。配偶多言善辩，宜相敬如宾，多包容。',
    '财帛宫': '凭口才、技术或智力进财（如律师、教师、销售、演艺等），属于“劳神费口”得财。',
    '官禄宫': '适合法律、教育、策划、科研、新闻传播等需要深度思考和表达的行业。'
  },
  '天相': {
    '命宫': '天相为印星，性格敦厚，做事循规蹈矩，乐于助人，极具正义感，善于调解纠纷。但缺乏自主决断力，易受他人影响。',
    '夫妻宫': '配偶多为同事、同学或经由亲友介绍，性格贤良，感情基础稳固踏实。',
    '财帛宫': '财源稳定，多为薪水及理财所得。适合做代理、服务或协助他人经营得财，一生衣食丰足。',
    '官禄宫': '适合担任秘书、行政助理、公职或中介顾问等辅助性、协调性强的职业。'
  },
  '天梁': {
    '命宫': '天梁为荫星、老人星。性格成熟稳重，热心公益，具有长者风范和极强的逢凶化吉能力。但有时说教味重，略嫌固执。',
    '夫妻宫': '感情多带有一点坎坷，但最终都能化解。配偶成熟稳重，容易有年龄差距较大的恋情。',
    '财帛宫': '财运平稳，多得长辈荫庇或遗产，亦适合以名声、技术、教职等清高职业赚取稳健收入。',
    '官禄宫': '适合从事医疗、教育、慈善、法律、宗教哲学或公务监察等行业，事业名声极佳。'
  },
  '七杀': {
    '命宫': '七杀为将星。性格刚强，充满干劲，喜欢冒险与挑战，做事雷厉风行。但脾气急躁，一生运势多起伏与成败变动。',
    '夫妻宫': '夫妻关系多具挑战，容易因为性格同样刚强而产生冲突。建议晚婚，或与性格温和之人结合。',
    '财帛宫': '财运起伏极大，一生中多有暴发暴败的经历，适合白手起家、冒险性投资，但不宜孤注一掷。',
    '官禄宫': '适合开创性、冒险性的行业，如军事、体育、建筑工程、开创性销售或自由职业。'
  },
  '破军': {
    '命宫': '破军为消耗之星，主破坏与重组。性格敢作敢当，反叛性强，勇于打破旧习气、开创新局面。但性格有些任性喜变动。',
    '夫妻宫': '感情生活多波折，容易经历闪婚或多次变动。配偶个性鲜明，宜晚婚并保持彼此空间。',
    '财帛宫': '财来财去，善于在破旧立新、改革中赚取横财，但财库难守，需注意理财规划。',
    '官禄宫': '适合从事制造业、技术研发、贸易开创或自由职业等需要不断自我革新的事业。'
  }
};

const DEFAULT_INTERPRETATION = '星曜吉凶参半，此宫位代表的领域运势稳健。若逢吉星（如文昌、左辅）则锦上添花，可成大器；若遇凶星（如火星、地劫）则需防波折与阻碍，修身养性方能逢凶化吉。';

// 均时差与真太阳时计算
function getEquationOfTime(date) {
  const year = date.getFullYear();
  const start = new Date(Date.UTC(year, 0, 0));
  const current = new Date(Date.UTC(year, date.getMonth(), date.getDate()));
  const diff = current - start;
  const oneDay = 1000 * 60 * 60 * 24;
  const d = Math.round(diff / oneDay);
  const B = 2 * Math.PI * (d - 81) / 365.24;
  return 9.87 * Math.sin(2 * B) - 7.53 * Math.cos(B) - 1.5 * Math.sin(B);
}

function getTrueSolarTime(date, longitude) {
  const longitudeDiffMinutes = (longitude - 120.0) * 4.0;
  const eotMinutes = getEquationOfTime(date);
  const totalOffsetMinutes = longitudeDiffMinutes + eotMinutes;
  const trueTime = new Date(date.getTime() + totalOffsetMinutes * 60 * 1000);
  return {
    trueTime: trueTime,
    longitudeDiff: longitudeDiffMinutes,
    eot: eotMinutes,
    totalOffset: totalOffsetMinutes
  };
}

// 五行力量加权量化
function calculateWuxingWeights(bazi) {
  const score = { '金': 0, '木': 0, '水': 0, '火': 0, '土': 0 };

  const addScore = (char, weight) => {
    let wx = GAN_WUXING[char] || ZHI_WUXING[char];
    if (wx) score[wx] += weight;
  };

  // 1. 计算天干五行
  addScore(bazi.year.gan, 10);
  addScore(bazi.month.gan, 10);
  addScore(bazi.day.gan, 10);
  addScore(bazi.time.gan, 10);

  // 2. 计算地支五行
  const addZhiScore = (zhi) => {
    const hides = ZHI_HIDE_GAN[zhi];
    if (hides) {
      hides.forEach(h => {
        let wx = GAN_WUXING[h.gan];
        if (wx) score[wx] += h.weight;
      });
    }
  };

  addZhiScore(bazi.year.zhi);
  addZhiScore(bazi.month.zhi);
  addZhiScore(bazi.day.zhi);
  addZhiScore(bazi.time.zhi);

  const total = score['金'] + score['木'] + score['水'] + score['火'] + score['土'];
  const percentage = {};
  for (let key in score) {
    percentage[key] = Math.round((score[key] / (total || 1)) * 100);
  }
  return percentage;
}

// 依据地点名称模糊匹配经度
function findLongitude(locationStr) {
  if (!locationStr) return 120.0;
  
  // 清理非必要字词
  const cleanStr = locationStr.replace(/(省|市|区|县|特别行政区|壮族自治区|回族自治区|维吾尔自治区|自治州)/g, '');
  
  // 1. 尝试全词或者局部包含匹配城市名
  for (const province in PROVINCE_CITY_DB) {
    const cities = PROVINCE_CITY_DB[province];
    for (const city in cities) {
      if (cleanStr.includes(city) || city.includes(cleanStr)) {
        return cities[city];
      }
    }
  }
  
  // 2. 尝试匹配省份，并返回省会（或数据库中该省的第一个城市）
  for (const province in PROVINCE_CITY_DB) {
    if (cleanStr.includes(province) || province.includes(cleanStr)) {
      const cities = PROVINCE_CITY_DB[province];
      const firstCity = Object.keys(cities)[0];
      return cities[firstCity];
    }
  }
  
  return 120.0; // 默认北京时间经度
}

// 解析命令行参数
const args = {};
process.argv.slice(2).forEach((val, index, array) => {
  if (val.startsWith('--')) {
    const key = val.slice(2);
    const nextVal = array[index + 1];
    if (nextVal && !nextVal.startsWith('--')) {
      args[key] = nextVal;
    } else {
      args[key] = true;
    }
  }
});

function getArg(name, defaultValue) {
  const val = args[name];
  if (val === undefined) return defaultValue;
  if (val === 'true') return true;
  if (val === 'false') return false;
  if (val === true) return true;
  if (!isNaN(val) && val.toString().trim() !== '') return Number(val);
  return val;
}

// 主入口
function main() {
  const name = getArg('name', '有缘人');
  const gender = getArg('gender', '男');
  const type = getArg('type', 'solar');
  const dateStr = getArg('date');
  const timeStr = getArg('time', '09:00');
  const location = getArg('location');
  const baziCalib = getArg('bazi-calib', true);
  const ziweiCalib = getArg('ziwei-calib', true);
  const leapMonth = getArg('leap-month', false);

  if (!dateStr) {
    console.error(JSON.stringify({ error: "Missing required parameter: --date (format: YYYY-MM-DD)" }));
    process.exit(1);
  }

  // 匹配/设置经度
  let longitude = getArg('longitude');
  if (longitude === undefined) {
    if (location) {
      longitude = findLongitude(location);
    } else {
      longitude = 120.0;
    }
  }

  const [y, m, d] = dateStr.split('-').map(Number);
  const [hour, minute] = timeStr.split(':').map(Number);
  
  if (isNaN(y) || isNaN(m) || isNaN(d) || isNaN(hour) || isNaN(minute)) {
    console.error(JSON.stringify({ error: "Invalid date or time format. --date: YYYY-MM-DD, --time: HH:mm" }));
    process.exit(1);
  }

  let baseDate;
  if (type === 'lunar') {
    // 阴历转阳历
    const flatLunar = Lunar.fromYmd(y, leapMonth ? -m : m, d);
    const flatSolar = flatLunar.getSolar();
    baseDate = new Date(flatSolar.getYear(), flatSolar.getMonth() - 1, flatSolar.getDay(), hour, minute, 0);
  } else {
    baseDate = new Date(y, m - 1, d, hour, minute, 0);
  }

  // 计算真太阳时
  const calib = getTrueSolarTime(baseDate, longitude);
  const trueTime = calib.trueTime;

  // 根据配置进行时间校准
  let baziCalcTime = new Date(baziCalib ? trueTime.getTime() : baseDate.getTime());
  let ziweiCalcTime = new Date(ziweiCalib ? trueTime.getTime() : baseDate.getTime());

  // 早晚子时：23:00 起算作次日
  if (baziCalcTime.getHours() >= 23) {
    baziCalcTime.setHours(baziCalcTime.getHours() + 1);
  }
  if (ziweiCalcTime.getHours() >= 23) {
    ziweiCalcTime.setHours(ziweiCalcTime.getHours() + 1);
  }

  // 实例化八字历法
  const baziSolarObj = Solar.fromYmdHms(
    baziCalcTime.getFullYear(),
    baziCalcTime.getMonth() + 1,
    baziCalcTime.getDate(),
    baziCalcTime.getHours(),
    baziCalcTime.getMinutes(),
    0
  );
  const baziLunarObj = baziSolarObj.getLunar();
  const eightChar = baziLunarObj.getEightChar();

  // 实例化紫微历法
  const ziweiSolarObj = Solar.fromYmdHms(
    ziweiCalcTime.getFullYear(),
    ziweiCalcTime.getMonth() + 1,
    ziweiCalcTime.getDate(),
    ziweiCalcTime.getHours(),
    ziweiCalcTime.getMinutes(),
    0
  );

  const baziHour = baziCalib ? trueTime.getHours() : baseDate.getHours();
  const baziTimeIndex = Math.floor(((baziHour + 1) % 24) / 2);

  const ziweiHour = ziweiCalib ? trueTime.getHours() : baseDate.getHours();
  const ziweiTimeIndex = Math.floor(((ziweiHour + 1) % 24) / 2);

  const ziweiDateStr = `${ziweiSolarObj.getYear()}-${ziweiSolarObj.getMonth()}-${ziweiSolarObj.getDay()}`;
  const genderKey = (gender === '男' || gender === '乾造' || gender === 'M') ? 'M' : 'F';
  
  // 计算紫微星盘
  const astrolabe = iztro.astro.bySolar(ziweiDateStr, ziweiTimeIndex, genderKey, true, 'zh-CN');

  // ========== 组装八字数据 ==========
  const baziData = {
    year: {
      gan: eightChar.getYearGan(),
      zhi: eightChar.getYearZhi(),
      hideGan: eightChar.getYearHideGan(),
      shishenGan: eightChar.getYearShiShenGan(),
      shishenZhi: eightChar.getYearShiShenZhi(),
      nayin: eightChar.getYearNaYin(),
      xunkong: eightChar.getYearXunKong()
    },
    month: {
      gan: eightChar.getMonthGan(),
      zhi: eightChar.getMonthZhi(),
      hideGan: eightChar.getMonthHideGan(),
      shishenGan: eightChar.getMonthShiShenGan(),
      shishenZhi: eightChar.getMonthShiShenZhi(),
      nayin: eightChar.getMonthNaYin(),
      xunkong: eightChar.getMonthXunKong()
    },
    day: {
      gan: eightChar.getDayGan(),
      zhi: eightChar.getDayZhi(),
      hideGan: eightChar.getDayHideGan(),
      shishenGan: '日主',
      shishenZhi: eightChar.getDayShiShenZhi(),
      nayin: eightChar.getDayNaYin(),
      xunkong: eightChar.getDayXunKong()
    },
    time: {
      gan: eightChar.getTimeGan(),
      zhi: eightChar.getTimeZhi(),
      hideGan: eightChar.getTimeHideGan(),
      shishenGan: eightChar.getTimeShiShenGan(),
      shishenZhi: eightChar.getTimeShiShenZhi(),
      nayin: eightChar.getTimeNaYin(),
      xunkong: eightChar.getTimeXunKong()
    }
  };

  const wuxingWeights = calculateWuxingWeights(baziData);

  // 大运提取
  const yun = eightChar.getYun(genderKey === 'M' ? 1 : 0);
  const startAge = typeof yun.getStartAge === 'function' ? yun.getStartAge() : yun.getStartYear();
  const daYunList = yun.getDaYun();
  let dayunTextList = [];
  daYunList.forEach(dy => {
    if (dy.getGanZhi()) {
      dayunTextList.push({
        ganzhi: dy.getGanZhi(),
        startAge: dy.getStartAge(),
        endAge: dy.getEndAge()
      });
    }
  });

  const isYangGan = ['甲', '丙', '戊', '庚', '壬'].includes(baziData.year.gan);
  const isForwardYun = (isYangGan && genderKey === 'M') || (!isYangGan && genderKey !== 'M');
  const yunOrderText = isForwardYun ? '顺排' : '逆排';

  const currentLunarObj = Lunar.fromDate(new Date());

  // ========== 组装紫微数据 ==========
  let shengnianSihua = [];
  astrolabe.palaces.forEach(p => {
    if (p.majorStars) {
      p.majorStars.forEach(s => {
        if (s.mutagen) {
          shengnianSihua.push(`${s.name}化${s.mutagen}`);
        }
      });
    }
  });

  const bodyPalace = astrolabe.palaces.find(p => p.isBodyPalace);
  const nominalAge = new Date().getFullYear() - baziLunarObj.getYear() + 1;
  const currentDaxianPalace = astrolabe.palaces.find(p => {
    if (p.decadal && p.decadal.range) {
      return nominalAge >= p.decadal.range[0] && nominalAge <= p.decadal.range[1];
    }
    return false;
  });

  const liunianPalace = astrolabe.palaces.find(p => p.earthlyBranch === currentLunarObj.getYearZhi());
  const liunianSihuaStr = {
    '丙': '天同化禄、天机化权、文昌化科、廉贞化忌',
    '丁': '太阴化禄、天同化权、天府化科、巨门化忌',
    '戊': '贪狼化禄、太阴化权、右弼化科、天机化忌',
    '己': '武曲化禄、贪狼化权、天梁化科、文曲化忌',
    '庚': '太阳化禄、武曲化权、太阴化科、天同化忌',
    '辛': '巨门化禄、太阳化权、文曲化科、文昌化忌',
    '壬': '天梁化禄、紫微化权、左辅化科、武曲化忌',
    '癸': '破军化禄、巨门化权、太阴化科、贪狼化忌',
    '甲': '廉贞化禄、破军化权、武曲化科、太阳化忌',
    '乙': '天机化禄、天梁化权、紫微化科、太阴化忌'
  }[currentLunarObj.getYearGan()] || '无';

  const ZHI_LIST = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
  const birthZhi = baziData.year.zhi;
  const isMale = genderKey === 'M';

  const detailedPalaces = astrolabe.palaces.map(p => {
    const branch = p.earthlyBranch;
    const range = p.decadal ? p.decadal.range : null;
    
    // 计算流年虚岁
    const birthZhiIdx = ZHI_LIST.indexOf(birthZhi);
    const palaceZhiIdx = ZHI_LIST.indexOf(branch);
    const liuNianStep = (palaceZhiIdx - birthZhiIdx + 12) % 12;
    const liuNianStart = liuNianStep + 1;
    const liuNianAges = [];
    for (let k = 0; k < 6; k++) {
      liuNianAges.push(liuNianStart + k * 12);
    }

    // 计算小限虚岁
    let xiaoXianStartZhi = '';
    const group1 = ['寅', '午', '戌'];
    const group2 = ['申', '子', '辰'];
    const group3 = ['巳', '酉', '丑'];
    const group4 = ['亥', '卯', '未'];

    if (isMale) {
      if (group1.includes(birthZhi)) xiaoXianStartZhi = '辰';
      else if (group2.includes(birthZhi)) xiaoXianStartZhi = '戌';
      else if (group3.includes(birthZhi)) xiaoXianStartZhi = '未';
      else if (group4.includes(birthZhi)) xiaoXianStartZhi = '丑';
    } else {
      if (group1.includes(birthZhi)) xiaoXianStartZhi = '戌';
      else if (group2.includes(birthZhi)) xiaoXianStartZhi = '辰';
      else if (group3.includes(birthZhi)) xiaoXianStartZhi = '丑';
      else if (group4.includes(birthZhi)) xiaoXianStartZhi = '未';
    }
    const sIdx = ZHI_LIST.indexOf(xiaoXianStartZhi);
    let xiaoXianStep = 0;
    if (isMale) {
      xiaoXianStep = (palaceZhiIdx - sIdx + 12) % 12;
    } else {
      xiaoXianStep = (sIdx - palaceZhiIdx + 12) % 12;
    }
    const xiaoXianStart = xiaoXianStep + 1;
    const xiaoXianAges = [];
    for (let k = 0; k < 6; k++) {
      xiaoXianAges.push(xiaoXianStart + k * 12);
    }

    // 宫内神煞与长生
    const doctor = p.doctorStar ? (p.doctorStar.name || p.doctorStar) : '';
    const preheaven = p.preheavenStar ? (p.preheavenStar.name || p.preheavenStar) : '';
    const travel = p.travelStar ? (p.travelStar.name || p.travelStar) : '';
    const changsheng = p.changsheng12 || (p.changshengStar ? (p.changshengStar.name || p.changshengStar) : '');

    // 离线解释提取
    const offlineInterpretations = [];
    if (p.majorStars) {
      p.majorStars.forEach(s => {
        const desc = (STAR_INTERPRETATIONS[s.name] && STAR_INTERPRETATIONS[s.name][p.name]) || '';
        if (desc) {
          offlineInterpretations.push({ star: s.name, desc });
        }
      });
    }

    return {
      name: p.name,
      heavenlyStem: p.heavenlyStem,
      earthlyBranch: p.earthlyBranch,
      isBodyPalace: p.isBodyPalace,
      decadalRange: range,
      liuNianAges,
      xiaoXianAges,
      changsheng,
      shensha: [doctor, preheaven, travel].filter(Boolean),
      majorStars: p.majorStars ? p.majorStars.map(s => ({ name: s.name, mutagen: s.mutagen || null, brightness: s.brightness || '' })) : [],
      minorStars: p.minorStars ? p.minorStars.map(s => ({ name: s.name, type: s.type })) : [],
      badStars: p.badStars ? p.badStars.map(s => ({ name: s.name, type: s.type })) : [],
      adjectiveStars: p.adjectiveStars ? p.adjectiveStars.map(s => s.name) : [],
      yearlyStars: p.yearlyStars ? p.yearlyStars.map(s => s.name) : [],
      offlineInterpretations
    };
  });

  const output = {
    meta: {
      name,
      gender,
      genderKey,
      inputTime: `${dateStr} ${timeStr}`,
      calendarType: type,
      location: location || '未指定',
      longitude: Number(longitude.toFixed(2)),
      calibration: {
        longitudeDiffMinutes: Number(calib.longitudeDiff.toFixed(1)),
        eotMinutes: Number(calib.eot.toFixed(1)),
        totalOffsetMinutes: Number(calib.totalOffset.toFixed(1)),
        trueTime: `${trueTime.getFullYear()}-${(trueTime.getMonth()+1).toString().padStart(2, '0')}-${trueTime.getDate().toString().padStart(2, '0')} ${trueTime.getHours().toString().padStart(2, '0')}:${trueTime.getMinutes().toString().padStart(2, '0')}`
      }
    },
    bazi: {
      pillars: baziData,
      wuxing: wuxingWeights,
      mingGong: eightChar.getMingGong(),
      taiYuan: eightChar.getTaiYuan(),
      yun: {
        order: yunOrderText,
        startAge,
        list: dayunTextList
      },
      currentFlowYear: currentLunarObj.getYearInGanZhi()
    },
    ziwei: {
      lordOfLife: astrolabe.lordOfLife,
      lordOfBody: astrolabe.lordOfBody,
      fiveElementsClass: astrolabe.fiveElementsClass,
      comingPalace: astrolabe.comingPalace,
      shengnianSihua,
      nominalAge,
      currentDaxian: currentDaxianPalace ? {
        palace: currentDaxianPalace.name,
        stars: currentDaxianPalace.majorStars ? currentDaxianPalace.majorStars.map(s => s.name) : [],
        range: currentDaxianPalace.decadal.range
      } : null,
      currentLiunian: {
        flowYear: currentLunarObj.getYearInGanZhi(),
        palaceName: liunianPalace ? liunianPalace.name : '',
        sihua: liunianSihuaStr
      },
      palaces: detailedPalaces
    }
  };

  console.log(JSON.stringify(output, null, 2));
}

main();
