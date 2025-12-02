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




def filter_empty_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    过滤掉数据中的空值字段
    
    Args:
        data: 输入的字典数据
        
    Returns:
        过滤掉空值字段后的字典
    """
    if not isinstance(data, dict):
        return data
    
    filtered_data = {}
    for key, value in data.items():
        if value is not None and value != "" and value != [] and value != {}:
            # 递归处理嵌套字典
            if isinstance(value, dict):
                filtered_value = filter_empty_data(value)
                if filtered_value:  # 只有非空字典才添加
                    filtered_data[key] = filtered_value
            # 递归处理嵌套列表
            elif isinstance(value, list):
                filtered_list = []
                for item in value:
                    if isinstance(item, dict):
                        filtered_item = filter_empty_data(item)
                        if filtered_item:  # 只有非空字典才添加
                            filtered_list.append(filtered_item)
                    elif item is not None and item != "" and item != [] and item != {}:
                        filtered_list.append(item)
                if filtered_list:  # 只有非空列表才添加
                    filtered_data[key] = filtered_list
            else:
                filtered_data[key] = value
                
    return filtered_data


async def single_alert(request:SecurityEventData):
    request.flowAlarmDetail = [FlowAlarmDetailItem(**item) for item in request.flowAlarmDetail]


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
        
        # 过滤掉空数据
        filtered_alert_dict = filter_empty_data(alert_dict)
        
        # 如果过滤后没有有效数据，返回错误
        if not filtered_alert_dict:
            raise HTTPException(
                status_code=400, 
                detail="告警数据为空或全部字段为空"
            )
        
        markdown_report = await system.eval_result(filtered_alert_dict)

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