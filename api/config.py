"""API服务配置"""

import os

# 服务配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# 规则引擎路径
ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "engine"))
ENGINE_PIPELINE = os.path.join(ENGINE_DIR, "pipeline_v5.py")
BAZI_ENGINE = "/root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py"

# 如果bazi-engine.py在其他路径，自动查找
if not os.path.exists(BAZI_ENGINE):
    alt_paths = ["/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py"]
    for p in alt_paths:
        if os.path.exists(p):
            BAZI_ENGINE = p
            break

# 引擎超时（秒）
ENGINE_TIMEOUT = 30
