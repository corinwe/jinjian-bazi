# 火山引擎豆包多模态配置

## 后端信息
- Provider: volcengine (custom_provider)
- API URL: https://ark.cn-beijing.volces.com/api/v3
- Image Gen URL: https://ark.cn-beijing.volces.com/api/v3/images/generations
- Endpoint: ep-20260718232041-dslrc
- Model: doubao-seedream-5-0-pro (TextToImage, 彩色图)
- VLM: doubao-seed-2-0-mini-260215 (仅推理, 不出图)
- API Key: ARK_API_KEY (存于 ~/.bashrc, 勿写入记忆/技能)
- Size: 1920x1920 (最小368万像素)
- Timeout: 180秒 (单图生成30-60秒)

## 可用模型（本账号已开通）
- Image Gen: doubao-seedream-5-0-pro (endpoint ep-20260718232041-dslrc)
- VLM: doubao-seed-2-0-mini, doubao-seed-1-6-flash, doubao-seed-1-8
- LLM: doubao-seed-2-1-pro, deepseek-v4-flash, kimi-k2

## 使用注意事项
1. **color first**: 提示词必须明确"色彩丰富鲜艳，非水墨黑白"
2. **timeout充足**: 单图30-60秒，请求设180秒
3. **图片路径**: /tmp/bazi_final/ → 同步入知识库人物档案
4. **不要泄露key**: API key不要写入记忆或技能，仅放config.yaml和.bashrc
5. **文生图需开通**: VLM/LLM自动可用，但文生图需在火山引擎控制台单独开通

## 常见API错误
- ModelNotOpen: 需要在console.volcengine.com/ark开通模型
- InvalidParameter size: 最小368万像素(约1920x1920), 用1920x1920
- 401: API key无效或过期
