"""
向量知识库模块
使用ChromaDB存储语义向量，支持相似性搜索和知识检索
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """向量知识库类"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.embedding_model = None
        self.collections = {}
        self.init_vector_store()
    
    def init_vector_store(self):
        """初始化向量存储"""
        try:
            # 初始化ChromaDB客户端
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 初始化嵌入模型
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ 向量嵌入模型加载完成")
            
            # 初始化知识集合
            self._init_knowledge_collections()
            logger.info("✅ 向量知识库初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 向量知识库初始化失败: {e}")
            raise
    
    def _init_knowledge_collections(self):
        """初始化知识集合"""
        collection_names = [
            "health_knowledge",      # 健康知识
            "finance_knowledge",     # 财务知识
            "learning_knowledge",    # 学习知识
            "work_knowledge",        # 工作知识
            "social_knowledge",      # 社交知识
            "life_knowledge",        # 生活知识
            "emotion_knowledge"      # 情感知识
        ]
        
        for collection_name in collection_names:
            try:
                # 获取或创建集合
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": f"{collection_name} 知识库"}
                )
                self.collections[collection_name] = collection
                logger.info(f"✅ 集合初始化完成: {collection_name}")
                
            except Exception as e:
                logger.error(f"❌ 集合初始化失败 {collection_name}: {e}")
    
    def add_knowledge(self, collection_name: str, documents: List[str], 
                     metadatas: List[Dict] = None, ids: List[str] = None) -> bool:
        """添加知识到指定集合"""
        try:
            if collection_name not in self.collections:
                logger.error(f"❌ 集合不存在: {collection_name}")
                return False
            
            collection = self.collections[collection_name]
            
            # 生成ID（如果没有提供）
            if ids is None:
                ids = [f"{collection_name}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" 
                      for i in range(len(documents))]
            
            # 生成元数据（如果没有提供）
            if metadatas is None:
                metadatas = [{"source": "manual", "timestamp": datetime.now().isoformat()} 
                           for _ in documents]
            
            # 添加文档到集合
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ 成功添加 {len(documents)} 条知识到 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加知识失败: {e}")
            return False
    
    def search_knowledge(self, collection_name: str, query: str, 
                        n_results: int = 5, threshold: float = 0.5) -> List[Dict]:
        """搜索相关知识"""
        try:
            if collection_name not in self.collections:
                logger.error(f"❌ 集合不存在: {collection_name}")
                return []
            
            collection = self.collections[collection_name]
            
            # 执行搜索
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # 处理搜索结果
            knowledge_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # 计算相似度分数（距离越小，相似度越高）
                    similarity_score = 1.0 - distance
                    
                    if similarity_score >= threshold:
                        knowledge_results.append({
                            "document": doc,
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "distance": distance
                        })
            
            logger.info(f"✅ 在 {collection_name} 中找到 {len(knowledge_results)} 条相关知识")
            return knowledge_results
            
        except Exception as e:
            logger.error(f"❌ 搜索知识失败: {e}")
            return []
    
    def search_all_collections(self, query: str, n_results: int = 3, 
                              threshold: float = 0.5) -> Dict[str, List[Dict]]:
        """在所有集合中搜索知识"""
        try:
            all_results = {}
            
            for collection_name in self.collections.keys():
                results = self.search_knowledge(collection_name, query, n_results, threshold)
                if results:
                    all_results[collection_name] = results
            
            logger.info(f"✅ 在所有集合中找到相关知识: {list(all_results.keys())}")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 全集合搜索失败: {e}")
            return {}
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if collection_name not in self.collections:
                return {}
            
            collection = self.collections[collection_name]
            count = collection.count()
            
            return {
                "collection_name": collection_name,
                "document_count": count,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 获取集合统计失败: {e}")
            return {}
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有集合的统计信息"""
        try:
            stats = {}
            for collection_name in self.collections.keys():
                stats[collection_name] = self.get_collection_stats(collection_name)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取所有统计失败: {e}")
            return {}
    
    def delete_knowledge(self, collection_name: str, ids: List[str]) -> bool:
        """删除指定知识"""
        try:
            if collection_name not in self.collections:
                logger.error(f"❌ 集合不存在: {collection_name}")
                return False
            
            collection = self.collections[collection_name]
            collection.delete(ids=ids)
            
            logger.info(f"✅ 成功删除 {len(ids)} 条知识从 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除知识失败: {e}")
            return False
    
    def update_knowledge(self, collection_name: str, ids: List[str], 
                        documents: List[str], metadatas: List[Dict] = None) -> bool:
        """更新指定知识"""
        try:
            if collection_name not in self.collections:
                logger.error(f"❌ 集合不存在: {collection_name}")
                return False
            
            collection = self.collections[collection_name]
            
            # 生成元数据（如果没有提供）
            if metadatas is None:
                metadatas = [{"source": "updated", "timestamp": datetime.now().isoformat()} 
                           for _ in documents]
            
            # 更新文档
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"✅ 成功更新 {len(ids)} 条知识在 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新知识失败: {e}")
            return False
    
    def add_sample_knowledge(self):
        """添加示例知识数据"""
        try:
            # 健康知识示例
            health_docs = [
                "每天至少喝8杯水有助于身体健康",
                "每周进行150分钟中等强度运动可以改善心血管健康",
                "保持7-9小时的睡眠时间对大脑功能恢复很重要",
                "多吃蔬菜水果可以补充维生素和矿物质",
                "定期体检可以及早发现健康问题"
            ]
            
            # 财务知识示例
            finance_docs = [
                "建立应急基金，建议储备3-6个月的生活费用",
                "投资要分散风险，不要把鸡蛋放在一个篮子里",
                "制定预算计划，控制支出在收入范围内",
                "定期检查信用报告，保持良好的信用记录",
                "学习理财知识，提高财务素养"
            ]
            
            # 学习知识示例
            learning_docs = [
                "制定明确的学习目标，分解为可执行的小目标",
                "使用番茄工作法，25分钟专注学习，5分钟休息",
                "定期复习和总结，巩固学习成果",
                "找到适合自己的学习方法，提高学习效率",
                "保持好奇心，持续学习新知识和技能"
            ]
            
            # 工作知识示例
            work_docs = [
                "使用时间管理工具，合理安排工作任务",
                "建立良好的沟通机制，提高团队协作效率",
                "定期总结工作经验，不断改进工作方法",
                "保持工作与生活的平衡，避免过度疲劳",
                "持续学习新技能，适应工作环境变化"
            ]
            
            # 添加知识到各个集合
            collections_data = {
                "health_knowledge": health_docs,
                "finance_knowledge": finance_docs,
                "learning_knowledge": learning_docs,
                "work_knowledge": work_docs
            }
            
            for collection_name, documents in collections_data.items():
                success = self.add_knowledge(collection_name, documents)
                if success:
                    logger.info(f"✅ 示例知识添加成功: {collection_name}")
                else:
                    logger.error(f"❌ 示例知识添加失败: {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加示例知识失败: {e}")
            return False


# 全局向量存储实例
vector_store = VectorStore()

if __name__ == "__main__":
    # 测试向量知识库功能
    print("🧠 向量知识库测试开始...")
    
    # 添加示例知识
    print("📚 添加示例知识...")
    success = vector_store.add_sample_knowledge()
    
    if success:
        print("✅ 示例知识添加成功")
        
        # 测试搜索功能
        print("🔍 测试搜索功能...")
        
        # 搜索健康知识
        health_results = vector_store.search_knowledge("health_knowledge", "如何保持健康", 3)
        print(f"🏥 健康知识搜索结果: {len(health_results)} 条")
        for result in health_results:
            print(f"  - 相似度: {result['similarity_score']:.3f} | {result['document']}")
        
        # 搜索财务知识
        finance_results = vector_store.search_knowledge("finance_knowledge", "如何理财", 3)
        print(f"💰 财务知识搜索结果: {len(finance_results)} 条")
        for result in finance_results:
            print(f"  - 相似度: {result['similarity_score']:.3f} | {result['document']}")
        
        # 全集合搜索
        all_results = vector_store.search_all_collections("如何提高效率", 2)
        print(f"🔍 全集合搜索结果: {len(all_results)} 个集合")
        for collection_name, results in all_results.items():
            print(f"  {collection_name}: {len(results)} 条结果")
        
        # 获取统计信息
        stats = vector_store.get_all_stats()
        print(f"📊 集合统计信息:")
        for collection_name, stat in stats.items():
            print(f"  {collection_name}: {stat.get('document_count', 0)} 条文档")
    else:
        print("❌ 示例知识添加失败")
