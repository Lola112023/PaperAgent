from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()


class Settings(BaseModel):
    """
    项目全局配置类。
    后续所有路径、模型名称、API Key 都建议统一从这里读取。
    """

    project_name: str = "PaperAgent"

    # 项目根目录
    base_dir: Path = Path(__file__).resolve().parent

    # 数据目录
    data_dir: Path = base_dir / "data"
    upload_dir: Path = data_dir / "uploaded"

    # 输出目录
    output_dir: Path = base_dir / "outputs"
    report_dir: Path = output_dir / "reports"

    # 日志目录
    log_dir: Path = base_dir / "logs"

    # API Key，今天可以先为空
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    # 后续可以改成你实际使用的模型
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Agent 最大循环步数
    max_agent_steps: int = 5


settings = Settings()