# ── 金鉴真人·八字命理引擎 — 生产部署镜像 ──
FROM python:3.11-slim

LABEL maintainer="金鉴真人"
LABEL description="确定性规则驱动的八字命理分析引擎，21§完整输出"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r api/requirements.txt

# 验证引擎
RUN cd engine && python3 -c "
import sys; sys.path.insert(0, '.')
from pipeline_v5 import run_pipeline
from constants import BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
bazi = BaZi(year=Pillar('庚','申'), month=Pillar('癸','未'), day=Pillar('辛','亥'), hour=Pillar('辛','卯'), gender='男')
s, l, _ = compute_shen_qiang_ruo(bazi)
assert abs(s - 64.0) < 0.5, f'身强{s} != 64.0'
print(f'引擎验证通过: {l}{s}分')
" && \
cd ..

# 运行测试
RUN cd engine && python3 tests/test_full_suite.py && cd ..

# 暴露端口
EXPOSE 8000

# 启动
ENV PYTHONPATH=/app
CMD ["python3", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
