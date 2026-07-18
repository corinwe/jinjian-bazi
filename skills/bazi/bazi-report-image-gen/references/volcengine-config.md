# 火山引擎豆包多模态配置

## 后端信息
- Provider: volcengine (custom_provider)
- API URL: https://ark.cn-beijing.volces.com/api/v3
- Image Gen URL: https://ark.cn-beijing.volces.com/api/v3/images/generations
- Endpoint: ep-20260718232041-dslrc
- Model: doubao-seedream-5-0-pro-260628 (ImageGeneration, TextToImage)
- VLM: doubao-seed-2-0-mini-260215 (VisualQuestionAnswering, 不出图)
- API Key: ARK_API_KEY (存于 ~/.bashrc, 勿写入记忆/技能)
- Size: 1920x1920 (最小368万像素)
- Timeout: 180秒

## 模型列表（本账号可用）
- Image: doubao-seedream-4-0/4.0-pro/5.0/5.0-pro (需在火山引擎控制台开通)
- 已开通: doubao-seedream-5-0-pro (endpoint: ep-20260718232041-dslrc)
- VLM: doubao-seed-2-0-mini, doubao-seed-1-6-flash, doubao-seed-1-8 等
- LLM: doubao-seed-2-1-pro, deepseek-v4-flash 等

## 生成脚本
- 路径: `engine/gen_report_images.py`
- 自动调用: gen_full_report.py 报告生成后自动触发
- 输出: /tmp/bazi_report_images_v3/ 同时入知识库人物档案

## 注意事项
- seedream-5-0生成速度较慢，单图30-60秒，timeout设180秒
- 文生图模型需在火山引擎控制台单独开通（LLM/VLM模型自动可用）
- API key放在memory中会泄露，只放config.yaml
- 图片不要放/tmp，要同步入知识库人物档案目录
