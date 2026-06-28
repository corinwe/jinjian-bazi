<template>
  <span>{{ description }}</span>
</template>

<script>
export default {
  name: 'NatureText',
  props: { gan: { type: String, default: '' } },
  computed: {
    description() {
      const map = {
        '甲':'正直担当，有领导风范，如参天大树',
        '乙':'柔韧灵活，善于适应环境，如藤萝花草',
        '丙':'热情开朗，光明磊落，如太阳之火',
        '丁':'温文尔雅，内心细腻，如灯烛之火',
        '戊':'稳重诚信，厚德载物，如泰山之土',
        '己':'包容柔和，善于协调，如田园之土',
        '庚':'刚毅果断，有进取精神，如刀剑之金',
        '辛':'精致优雅，追求完美，如珠玉之金',
        '壬':'智慧灵动，胸怀宽广，如江河之水',
        '癸':'含蓄深沉，心思缜密，如雨露之水',
      }
      return map[this.gan] || '特质鲜明'
    }
  }
}
</script>
