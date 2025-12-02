# main.py
from typing import List
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agents import MultiAgentSystem
import asyncio
import uvicorn

load_dotenv()

app = FastAPI(
    title="网络安全多智能体分析服务",
    description="接收网络告警数据，返回多智能体协同分析结果"
)

# 修改路径解析为基于当前脚本目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, os.getenv("PROMPT_PATH", "model/prompt.txt"))
DECISION_PATH = os.path.join(BASE_DIR, os.getenv("DECISION_PATH", "model/decision.txt"))


class AlertRequest(BaseModel):
    sourceIp: str
    sourcePort: int
    dstIp: str
    dstPort: int
    payload: str = Field(default="")
    alarmTime: str






class BatchAlertRequest(BaseModel):
    alerts: List[AlertRequest]


@app.post("/analyze")
async def analyze_alert(request: BatchAlertRequest):
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY 未配置")

    try:
        system = MultiAgentSystem(PROMPT_PATH, DECISION_PATH)
        alert_dict = request.alerts[0].dict() if request.alerts else {}
        markdown_report = await system.run_conversation(alert_dict)

        if not isinstance(markdown_report, str):
            raise ValueError("未返回Markdown")

        return {
            "report": markdown_report
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"提示词文件未找到: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": True}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=6006, log_level="info")