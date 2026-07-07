# xing_chong_he_hua.py v2.0 引擎扩展（2026-07-05）

## 变更内容

在 `xing_chong_he_hua.py` 新增：

1. **TIAN_GAN_HE** 天干五合表 + `check_tian_gan_he()` / `check_all_tian_gan_he()`
2. **SAN_HUI** 三会局表 + `check_san_hui()` (能量20.0)
3. **GONG_HE** 拱合12组 + `check_gong_he()` (含missing字段)
4. **AN_HE** 暗合3组 + `check_an_he()` (能量0.5)
5. **NENG_LIANG** 新增 `天干五合: 10.0` 和 `三会: 20.0`
6. **check_all_relations_v2()** — 全量API，含合化优先级规则

## 优先级规则

三会(20倍) > 三合(15倍) > 六合/半合/拱合(10倍) > 暗合(0.5倍)
只保留最高优先级的合化关系。

## 向后兼容

- `check_all_relations()` v1 保持不变
- v2 新增函数不影响现有调用方
- 引擎其他模块无需修改

## 相关文件

- `projects/bazi-platform/engine/xing_chong_he_hua.py`
