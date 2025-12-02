from click import prompt
from langchain_community.document_compressors import DashScopeRerank
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
from safeAgent.utils.config import *
import os


class QwenModel:
    """
    Qwen模型封装类，包含语言模型、嵌入模型和重排序模型。
    
    该类封装了通义千问系列模型，包括文本生成、嵌入表示和重排序功能，
    以及针对安全分析场景的专用模型。
    """
    
    def __init__(self, temperature=0.7, top_p=0.7, embedding_dimension=1024, rerank_top_n=10):
        """
        初始化Qwen模型实例。
        
        Args:
            temperature (float): 控制生成文本的随机性，值越高越随机。
            top_p (float): nucleus sampling参数，控制生成质量。
            embedding_dimension (int): 嵌入模型输出向量的维度。
            rerank_top_n (int): 重排序模型返回的最相关文档数量。
        """
        # 确保API密钥存在
        if not OPENAI_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
            
        # 设置USER_AGENT以避免警告
        if not os.environ.get('USER_AGENT'):
            os.environ['USER_AGENT'] = 'NetSafe-Agent/1.0'
            
        self.model = ChatOpenAI(
            model=MODEL_NAME,
            temperature=temperature,
            top_p=top_p,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )

        # DashScopeEmbeddings 不接受 openai_api_key 和 openai_api_base 参数
        self.embedding_model = DashScopeEmbeddings(
            model=EMBEDDING_NAME,
            dashscope_api_key=OPENAI_API_KEY
        )

        self.rerank_model = DashScopeRerank(
            model=RERANK_NAME,
            top_n=rerank_top_n,
            dashscope_api_key=OPENAI_API_KEY
        )

    def get_model(self):
        """
        获取语言模型实例。
        
        Returns:
            ChatOpenAI: 语言模型实例。
        """
        return self.model

    def get_embedding_model(self):
        """
        获取嵌入模型实例。
        
        Returns:
            DashScopeEmbeddings: 嵌入模型实例。
        """
        return self.embedding_model
    
    def get_rerank_model(self):
        """
        获取重排序模型实例。
        
        Returns:
            DashScopeRerank: 重排序模型实例。
        """
        return self.rerank_model

# 仅在直接运行此脚本时才执行以下代码
if __name__ == "__main__":
    try:
        qwen_model = QwenModel()
        prompt = '你可以做什么'
        # 使用 invoke 方法替代已弃用的 predict 方法
        response = qwen_model.get_model().invoke(prompt)
        print("模型初始化成功:")
        print(f"语言模型: {qwen_model.get_model()}")
        print(f"语言模型响应: {response.content}")
        
        # 获取嵌入向量
        embed = qwen_model.get_embedding_model().embed_query(prompt)
        print(f"嵌入向量维度: {len(embed) if embed else 0}")
        print(f"嵌入向量(前10维): {embed[:10] if embed else []}")
        
        # 测试重排序功能
        from langchain_core.documents import Document
        docs = [
            Document(page_content="通义千问是一款强大的语言模型"),
            Document(page_content="通义万相是强大的图像生成模型")
        ]
        rerank_result = qwen_model.get_rerank_model().compress_documents(docs, prompt)
        print(f"重排序模型: {qwen_model.get_rerank_model()}")
        print(f"重排序结果数量: {len(rerank_result)}")
        for i, doc in enumerate(rerank_result):
            print(f"  文档 {i+1}: {doc.page_content} (相关性得分: {doc.metadata.get('relevance_score', 'N/A')})")
        
    except Exception as e:
        print(f"模型初始化失败: {e}")
        import traceback
        traceback.print_exc()