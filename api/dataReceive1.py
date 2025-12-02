# main.py
import os
from fastapi import FastAPI, HTTPException

from dataClass import *
from dotenv import load_dotenv
from safeAgent.service.agent import *
from typing import List, Optional, Dict, Any
import uvicorn

load_dotenv()

app = FastAPI(
    title="网络安全多智能体分析服务",
    description="接收网络告警数据，返回多智能体协同分析结果"
)



def prepare_alert_data(raw_data: dict) -> dict:

    flow_data = {"FlowAlarmDetailItem": raw_data.get("flowAlarmDetail", [])}
    flowrisk_data = {"FlowRiskAssetsItem": raw_data.get("flowRiskAssets", [])}
    host_data = {"HostSecurityEventItem": raw_data.get("hostSecurityEvent", [])}
    honeypot_data = {"HoneypotTimeAxisItem": raw_data.get("honeypotTimeAxis", [])}


    alert_id = raw_data.get('alert_id', 'default_id')
    flow_data["correlation_id"] = f"flow_{alert_id}"
    flowrisk_data["correlation_id"] = f"flowrisk_{alert_id}"
    host_data["correlation_id"] = f"host_{alert_id}"
    honeypot_data["correlation_id"] = f"honeypot_{alert_id}"

    return {
        "flow": flow_data,
        "flowrisk_data": flowrisk_data,
        "host": host_data,
        "honeypot_data":honeypot_data,
        "original_id": alert_id
    }


@app.post("/mutiAnalyze")
async def analyze_alert(request: AnalyzeRequest):
    """
    接收一条完整的多源安全事件数据，返回分析报告
    """
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY 未配置")

    try:
        system = MutiAgentSystem()

        # 将 Pydantic 模型转为 dict（兼容 run_conversation）
        alert_dict = request.alerts.model_dump()  # Pydantic v2 推荐方式
        alert_dict = prepare_alert_data(alert_dict)
        print(alert_dict)

        markdown_report = await system.eval_result(alert_dict)

        if not isinstance(markdown_report, str):
            raise ValueError("分析系统未返回有效的 Markdown 字符串")

        return {
            "report": markdown_report
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"提示词文件未找到: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/analyze")
async def analyze_alert(request: BatchAlertRequest):
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY 未配置")

    try:
        system = MutiAgentSystem()
        alert_dict = request.alerts[0].model_dump() if request.alerts else {}


        # filtered_alert_dict = filter_empty_data(alert_dict)

        # if not filtered_alert_dict:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="告警数据为空或全部字段为空"
        #     )

        markdown_report = await system.eval_result(alert_dict)

        if not isinstance(markdown_report, str):
            raise ValueError("未返回Markdown")

        return {
            "report": markdown_report
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"提示词文件未找到: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/analyze/batch")
async def analyze_batch_alerts(request: BatchAnalyzeRequest):
    if not request.alerts:
        raise HTTPException(status_code=400, detail="alerts 列表不能为空")

    reports = []
    system = MutiAgentSystem()

    for alert in request.alerts:
        try:
            alert_dict = alert.model_dump()
            report = await system.eval_result(alert_dict)
            reports.append({"status": "success", "report": report})
        except Exception as e:
            reports.append({"status": "error", "error": str(e)})

    return {"reports": reports}


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": True}


# ========== 启动 ==========
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=6006, log_level="info")