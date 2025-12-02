from langchain.tools import tool
from langchain.agents import create_agent
from safeAgent.utils.config import *
from safeAgent.model.QwenModel import *
import json
import asyncio
from typing import List, Dict, Any


class MutiAgentSystem:
    def __init__(self):
        self.model = QwenModel()

        self.flowAnaAgent = create_agent(
            model=self.model.get_model(),
            system_prompt=ANA_PROMPT
        )
        self.flowRiskAnaAgent = create_agent(
            model=self.model.get_model(),
            system_prompt=FLOW_RISK_PROMPT
        )
        self.HostAnaAgent = create_agent(
            model=self.model.get_model(),
            system_prompt=HOST_PROMPT
        )
        self.HoneyAnaAgent = create_agent(
            model=self.model.get_model(),
            system_prompt=HONEY_PROMPT
        )
        self.evalAgent = create_agent(
            model=self.model.get_model(),
            system_prompt=EVAL_PROMPT
        )

    def _invoke_agent(self, agent, data: dict) -> str:
        query_str = json.dumps(data, ensure_ascii=False, indent=2)
        result = agent.invoke({
            "messages": [{"role": "user", "content": query_str}]
        })
        return result["messages"][-1].content

    @tool
    def anal_result(self, query: str) -> str:
        """分析智能体

        Args:
            query: 用户查询内容

        Returns:
            str: 分析结果
        """
        result = self.anaAgent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        # print(result)
        return result["messages"][-1].content

    async def eval_result(self, alert_data=dict) -> str:
        """评估智能体

        Args:
            query: 用户查询内容（可以是字典或字符串）

        Returns:
            str: 评估结果
        """

        flow_analysis = self._invoke_agent(self.flowAnaAgent, alert_data)
        all_analyses = [flow_analysis]

        # if "需要Host信息" in flow_analysis:
        if flow_analysis is not None:
            print(1)
            host_analysis = self._invoke_agent(self.HostAnaAgent, alert_data)
            all_analyses.append(host_analysis)

        # if "【需要: flowrisk】" in flow_analysis:
        if flow_analysis is not None:
            print(2)
            flowrisk_analysis = self._invoke_agent(self.flowRiskAnaAgent, alert_data)
            all_analyses.append(flowrisk_analysis)

        # if "【需要: honeypot】" in flow_analysis:
        if flow_analysis is not None:
            print(3)
            honeypot_analysis = self._invoke_agent(self.HoneyAnaAgent, alert_data)
            all_analyses.append(honeypot_analysis)

        full_analysis = "\n\n".join(all_analyses)


        eval_result = self.evalAgent.invoke({
            "messages": [{"role": "user", "content": full_analysis}]
        })
        evaluation_content = eval_result["messages"][-1].content

        return self.format_markdown_output(full_analysis, evaluation_content)


    def format_markdown_output(self, analysis: str, evaluation: str) -> str:
        """
        将分析和评估结果格式化为Markdown格式

        Args:
            analysis: 分析专家的输出
            evaluation: 评估专家的输出

        Returns:
            str: 格式化的Markdown输出
        """
        markdown_output = f"""# 安全分析报告


{analysis}


{evaluation}

"""
        return markdown_output

    async def process_security_analysis(self, query) -> str:
        """
        处理安全分析请求的主入口函数

        Args:
            query: 安全分析请求内容

        Returns:
            str: 格式化的安全分析报告
        """
        return await self.eval_result(query)

    async def process_batch_security_analysis(self, queries: List) -> List[str]:
        """
        处理批量安全分析请求的主入口函数

        Args:
            queries: 安全分析请求内容列表

        Returns:
            List[str]: 格式化的安全分析报告列表
        """
        return await self.eval_batch_result(queries)