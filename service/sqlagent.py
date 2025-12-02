from typing import List, Dict, Any
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy import create_engine, text
from safeAgent.model.QwenModel import QwenModel

class SqlAgentSystem:
    def __init__(self, database_uri: str = None):
        """
        初始化SQL Agent系统
        
        Args:
            database_uri: 数据库连接URI，默认为None
        """
        self.model = QwenModel()
        self.llm = self.model.get_model()
        
        # 如果提供了数据库URI，则初始化数据库引擎
        self.engine = None
        if database_uri:
            self.engine = create_engine(database_uri)
        
        # 创建SQL执行工具
        self.sql_tools = [self.execute_sql_tool()]
        
        # 创建agent
        self.sql_agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.sql_tools,
            prompt=PromptTemplate.from_template("""
您是一个SQL专家助手，能够将自然语言转换为SQL查询并在数据库上执行。

当用户提出问题时，请按照以下步骤操作：
1. 理解用户的需求
2. 构造合适的SQL查询语句
3. 使用execute_sql工具执行SQL查询
4. 分析查询结果并以友好的方式呈现给用户

请注意：
- 只使用必要的列，避免使用SELECT *
- 确保查询语法正确
- 如果遇到错误，尝试修正查询语句

以下是数据库的上下文信息：
{context}

您可以使用的工具:
{tools}

工具调用格式: