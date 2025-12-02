import os
from typing import List

import bs4
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    JSONLoader,
    BSHTMLLoader,
    WebBaseLoader
)
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from safeAgent.model.QwenModel import QwenModel

class FileHandler:
    """
    文档加载和分片处理类
    支持txt、pdf、json、html等文件格式的加载和分片处理
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文件处理器
        
        Args:
            chunk_size: 分片大小
            chunk_overlap: 分片重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def initialize_vector_store(self, sample_text=None):
        """
        初始化向量存储
        
        Args:
            sample_text: 用于确定嵌入维度的示例文本，如果未提供则使用默认文本
            
        Returns:
            FAISS: 初始化的FAISS向量存储实例
        """
        # 初始化Qwen模型以获取嵌入模型
        qwen_model = QwenModel()
        embeddings = qwen_model.get_embedding_model()
        
        # 获取嵌入维度
        if sample_text is None:
            sample_text = "This is a sample text to determine embedding dimensions."
            
        # 如果传入的是文档列表，则提取第一段文本
        if isinstance(sample_text, list) and len(sample_text) > 0:
            if hasattr(sample_text[0], 'page_content'):
                sample_text = sample_text[0].page_content
            else:
                sample_text = str(sample_text[0])
        
        embedding_dim = len(embeddings.embed_query(sample_text))
        index = faiss.IndexFlatL2(embedding_dim)
        
        # 创建向量存储
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        
        return vector_store
    
    def load_txt_file(self, file_path: str) -> List[Document]:
        """
        加载txt文件
        
        Args:
            file_path: txt文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()
    
    def load_pdf_file(self, file_path: str) -> List[Document]:
        """
        加载pdf文件
        
        Args:
            file_path: pdf文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        loader = PyPDFLoader(file_path)
        return loader.load()
    
    def load_json_file(self, file_path: str, jq_schema: str = '.', content_key: str = None) -> List[Document]:
        """
        加载json文件
        
        Args:
            file_path: json文件路径
            jq_schema: jq模式字符串，用于提取特定字段
            content_key: 内容键名
            
        Returns:
            List[Document]: 文档列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        loader = JSONLoader(
            file_path=file_path,
            jq_schema=jq_schema,
            content_key=content_key,
            is_content_key_jq_parsable=True if content_key else False
        )
        return loader.load()
    
    def load_html_file(self, file_path: str) -> List[Document]:
        """
        加载html文件
        
        Args:
            file_path: html文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        loader = BSHTMLLoader(file_path, open_encoding='utf-8')
        return loader.load()
    
    def load_web_page(self, url: str) -> List[Document]:
        """
        加载网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            List[Document]: 文档列表
        """
        bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))

        loader = WebBaseLoader(url,bs_kwargs={"parse_only": bs4_strainer},)
        return loader.load()
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        根据文件扩展名自动加载文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.txt':
            return self.load_txt_file(file_path)
        elif ext == '.pdf':
            return self.load_pdf_file(file_path)
        elif ext == '.json':
            return self.load_json_file(file_path)
        elif ext in ['.html', '.htm']:
            return self.load_html_file(file_path)
        else:
            # 默认使用文本加载器
            return self.load_txt_file(file_path)
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        对文档进行分片处理
        
        Args:
            documents: 文档列表
            
        Returns:
            List[Document]: 分片后的文档列表
        """
        return self.text_splitter.split_documents(documents)
    
    def load_and_split(self, file_path: str) -> List[Document]:
        """
        加载文件并进行分片处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Document]: 分片后的文档列表
        """
        documents = self.load_file(file_path)
        all_splits = self.split_documents(documents)
        vector_store = self.initialize_vector_store(all_splits)
        document_ids = vector_store.add_documents(documents=all_splits)

        print(document_ids[:3])
        return all_splits
    
    def vector_store(self, documents: List[Document], rag_instance, category: str = "文档知识"):
        """
        将文档添加到向量存储中
        
        Args:
            documents: 文档列表
            rag_instance: RAG实例，用于添加知识
            category: 知识类别
        """
        # 将文档转换为知识条目格式并添加到向量存储
        for i, doc in enumerate(documents):
            knowledge_item = {
                "id": f"doc_{id(doc)}_{i}",  # 生成唯一ID
                "title": doc.metadata.get("source", f"文档片段 {i}"),
                "category": category,
                "content": doc.page_content,
                "tags": ["文档导入", category.lower()]
            }
            rag_instance.add_knowledge(knowledge_item)

if __name__ == "__main__":
    handle= FileHandler ()
    documents = handle.load_and_split(r"D:\CodeProject\NetSafe\safeAgent\prompt\evalPrompt.txt")
    # 创建一个模拟的RAG实例用于测试
    class MockRAG:
        def add_knowledge(self, item):
            print(f"添加知识项: {item['title']}")
    
    rag_instance = MockRAG()
    handle.vector_store(documents, rag_instance)
