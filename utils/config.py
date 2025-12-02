import os
from dotenv import load_dotenv

# 加载safeAgent目录下的.env文件
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

EMBEDDING_NAME = os.getenv("EMBEDDING_NAME", "text-embedding-v4")
RERANK_NAME = os.getenv("RERANK_NAME", "gte-rerank-v2")
OPENAI_API_KEY = os.getenv("DASHSCOPE_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_API_KEY = os.getenv("DASHSCOPE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")

VT_API_KEY = os.getenv("VT_API_KEY")

def load_prompt(file_path):
    """加载提示词文件内容"""
    full_path = os.path.join(os.path.dirname(__file__), '..', 'prompt', file_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()
    
# 从文件加载提示词
ANA_PROMPT = load_prompt('anaPrompt.txt')
EVAL_PROMPT = load_prompt('evalPrompt.txt')
FLOW_PROMPT = load_prompt('flow.txt')
FLOW_RISK_PROMPT = load_prompt('flowrisk.txt')
HOST_PROMPT = load_prompt('host.txt')
HONEY_PROMPT = load_prompt('honeypot.txt')

