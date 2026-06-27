"""应用配置"""
import os


class Settings:
    app_name: str = "金鉴真人·八字命理分析API"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库 — MVP用SQLite
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jinjian.db")

    # 服务端口
    host: str = "0.0.0.0"
    port: int = 9000

    # 报告输出
    report_min_lines: int = 1500
    pdf_output_dir: str = "/root/jinjian/backend/reports"

    # 免费版限制
    free_report_sections_limit: int = 5
    free_monthly_limit: int = 3


settings = Settings()
