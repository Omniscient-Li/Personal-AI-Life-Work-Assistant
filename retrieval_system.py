"""
智能检索系统
结合知识库、向量存储和对话历史，提供上下文感知的知识检索
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from datetime import datetime
from knowledge_base import knowledge_base
from vector_store import vector_store

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievalSystem:
    """智能检索系统"""
    
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.vector_store = vector_store
        logger.info("✅ 智能检索系统初始化完成")
    
    def retrieve_knowledge(self, user_input: str, session_id: str, 
                          understanding: Dict, context: Dict = None) -> Dict[str, Any]:
        """智能知识检索主函数"""
        try:
            # 1. 获取用户偏好和对话历史
            user_preferences = self.knowledge_base.get_user_preferences(session_id)
            conversation_history = self.knowledge_base.get_conversation_history(session_id, limit=5)
            behavior_patterns = self.knowledge_base.get_behavior_patterns(session_id)
            
            # 2. 分析检索需求
            retrieval_needs = self._analyze_retrieval_needs(user_input, understanding, user_preferences)
            
            # 3. 执行多策略检索
            retrieval_results = self._multi_strategy_retrieval(
                user_input, understanding, retrieval_needs, conversation_history
            )
            
            # 4. 融合和排序结果
            final_results = self._merge_and_rank_results(
                retrieval_results, user_preferences, behavior_patterns
            )
            
            # 5. 构建检索摘要
            retrieval_summary = self._build_retrieval_summary(
                final_results, user_preferences, behavior_patterns
            )
            
            logger.info(f"✅ 知识检索完成: 找到 {len(final_results)} 条相关知识")
            return retrieval_summary
            
        except Exception as e:
            logger.error(f"❌ 知识检索失败: {e}")
            return {"error": str(e), "results": []}
    
    def _analyze_retrieval_needs(self, user_input: str, understanding: Dict, 
                                user_preferences: List) -> Dict[str, Any]:
        """分析检索需求"""
        try:
            intent = understanding.get("intent", "")
            entities = understanding.get("entities", {})
            topic_analysis = understanding.get("life_context", {}).get("topic_analysis", {})
            primary_topic = topic_analysis.get("primary_topic", "general")
            
            # 确定需要检索的知识类型
            knowledge_types = []
            
            # 基于意图确定知识类型
            intent_to_knowledge = {
                "health_tracking": ["health_knowledge"],
                "exercise_recording": ["health_knowledge"],
                "diet_management": ["health_knowledge"],
                "sleep_analysis": ["health_knowledge"],
                "mood_tracking": ["emotion_knowledge", "health_knowledge"],
                "expense_recording": ["finance_knowledge"],
                "budget_management": ["finance_knowledge"],
                "investment_tracking": ["finance_knowledge"],
                "learning_planning": ["learning_knowledge"],
                "progress_tracking": ["learning_knowledge"],
                "task_creation": ["work_knowledge"],
                "schedule_management": ["work_knowledge"],
                "contact_management": ["social_knowledge"],
                "social_activity": ["social_knowledge"],
                "shopping_list": ["life_knowledge"],
                "weather_query": ["life_knowledge"],
                "emotion_support": ["emotion_knowledge"]
            }
            
            if intent in intent_to_knowledge:
                knowledge_types.extend(intent_to_knowledge[intent])
            
            # 基于话题确定知识类型
            topic_to_knowledge = {
                "health": ["health_knowledge"],
                "finance": ["finance_knowledge"],
                "learning": ["learning_knowledge"],
                "work": ["work_knowledge"],
                "social": ["social_knowledge"],
                "life": ["life_knowledge"],
                "emotion": ["emotion_knowledge"]
            }
            
            if primary_topic in topic_to_knowledge:
                knowledge_types.extend(topic_to_knowledge[primary_topic])
            
            # 去重
            knowledge_types = list(set(knowledge_types))
            
            # 如果没有明确的知识类型，使用用户偏好
            if not knowledge_types and user_preferences:
                top_preferences = [p.intent_type for p in user_preferences[:3]]
                for pref in top_preferences:
                    if pref in intent_to_knowledge:
                        knowledge_types.extend(intent_to_knowledge[pref])
                knowledge_types = list(set(knowledge_types))
            
            # 如果还是没有，使用通用知识
            if not knowledge_types:
                knowledge_types = ["life_knowledge", "work_knowledge"]
            
            return {
                "knowledge_types": knowledge_types,
                "intent": intent,
                "primary_topic": primary_topic,
                "entities": entities,
                "confidence": understanding.get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"❌ 检索需求分析失败: {e}")
            return {"knowledge_types": ["life_knowledge"], "intent": "", "primary_topic": "general"}
    
    def _multi_strategy_retrieval(self, user_input: str, understanding: Dict, 
                                 retrieval_needs: Dict, conversation_history: List) -> Dict[str, List]:
        """多策略检索"""
        try:
            results = {}
            
            # 1. 语义检索（向量相似度）
            semantic_results = self._semantic_retrieval(user_input, retrieval_needs)
            results["semantic"] = semantic_results
            
            # 2. 关键词检索（精确匹配）
            keyword_results = self._keyword_retrieval(user_input, retrieval_needs)
            results["keyword"] = keyword_results
            
            # 3. 上下文检索（基于对话历史）
            context_results = self._context_retrieval(user_input, conversation_history, retrieval_needs)
            results["context"] = context_results
            
            # 4. 偏好检索（基于用户偏好）
            preference_results = self._preference_retrieval(retrieval_needs)
            results["preference"] = preference_results
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 多策略检索失败: {e}")
            return {}
    
    def _semantic_retrieval(self, user_input: str, retrieval_needs: Dict) -> List[Dict]:
        """语义检索"""
        try:
            knowledge_types = retrieval_needs.get("knowledge_types", [])
            all_results = []
            
            for knowledge_type in knowledge_types:
                results = self.vector_store.search_knowledge(
                    knowledge_type, user_input, n_results=3, threshold=0.4
                )
                for result in results:
                    result["source"] = "semantic"
                    result["knowledge_type"] = knowledge_type
                    all_results.append(result)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 语义检索失败: {e}")
            return []
    
    def _keyword_retrieval(self, user_input: str, retrieval_needs: Dict) -> List[Dict]:
        """关键词检索"""
        try:
            # 提取关键词
            keywords = self._extract_keywords(user_input)
            knowledge_types = retrieval_needs.get("knowledge_types", [])
            all_results = []
            
            for knowledge_type in knowledge_types:
                for keyword in keywords:
                    results = self.vector_store.search_knowledge(
                        knowledge_type, keyword, n_results=2, threshold=0.6
                    )
                    for result in results:
                        result["source"] = "keyword"
                        result["keyword"] = keyword
                        result["knowledge_type"] = knowledge_type
                        all_results.append(result)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 关键词检索失败: {e}")
            return []
    
    def _context_retrieval(self, user_input: str, conversation_history: List, 
                          retrieval_needs: Dict) -> List[Dict]:
        """上下文检索"""
        try:
            if not conversation_history:
                return []
            
            # 从对话历史中提取相关话题
            context_topics = []
            for record in conversation_history[:3]:  # 最近3轮对话
                if record.topic and record.topic != "general":
                    context_topics.append(record.topic)
            
            if not context_topics:
                return []
            
            # 基于上下文话题检索
            all_results = []
            for topic in context_topics:
                topic_knowledge_type = f"{topic}_knowledge"
                if hasattr(self.vector_store, 'collections') and topic_knowledge_type in self.vector_store.collections:
                    results = self.vector_store.search_knowledge(
                        topic_knowledge_type, user_input, n_results=2, threshold=0.5
                    )
                    for result in results:
                        result["source"] = "context"
                        result["context_topic"] = topic
                        result["knowledge_type"] = topic_knowledge_type
                        all_results.append(result)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 上下文检索失败: {e}")
            return []
    
    def _preference_retrieval(self, retrieval_needs: Dict) -> List[Dict]:
        """偏好检索"""
        try:
            intent = retrieval_needs.get("intent", "")
            if not intent:
                return []
            
            # 基于用户意图检索相关知识
            all_results = []
            knowledge_types = retrieval_needs.get("knowledge_types", [])
            
            for knowledge_type in knowledge_types:
                # 使用意图作为查询词
                results = self.vector_store.search_knowledge(
                    knowledge_type, intent, n_results=2, threshold=0.5
                )
                for result in results:
                    result["source"] = "preference"
                    result["intent"] = intent
                    result["knowledge_type"] = knowledge_type
                    all_results.append(result)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 偏好检索失败: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        try:
            # 简单的关键词提取（可以后续优化）
            keywords = []
            
            # 健康相关关键词
            health_keywords = ["健康", "运动", "饮食", "睡眠", "体检", "锻炼", "营养"]
            # 财务相关关键词
            finance_keywords = ["理财", "投资", "预算", "消费", "储蓄", "基金", "股票"]
            # 学习相关关键词
            learning_keywords = ["学习", "知识", "技能", "培训", "课程", "考试", "复习"]
            # 工作相关关键词
            work_keywords = ["工作", "任务", "项目", "会议", "报告", "效率", "时间"]
            
            all_keywords = health_keywords + finance_keywords + learning_keywords + work_keywords
            
            for keyword in all_keywords:
                if keyword in text:
                    keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"❌ 关键词提取失败: {e}")
            return []
    
    def _merge_and_rank_results(self, retrieval_results: Dict, user_preferences: List, 
                               behavior_patterns: List) -> List[Dict]:
        """融合和排序结果"""
        try:
            all_results = []
            
            # 收集所有结果
            for strategy, results in retrieval_results.items():
                for result in results:
                    # 添加策略权重
                    strategy_weights = {
                        "semantic": 1.0,
                        "keyword": 0.8,
                        "context": 0.9,
                        "preference": 0.7
                    }
                    result["strategy_weight"] = strategy_weights.get(strategy, 0.5)
                    all_results.append(result)
            
            # 去重（基于文档内容）
            unique_results = []
            seen_docs = set()
            for result in all_results:
                doc_content = result.get("document", "")
                if doc_content and doc_content not in seen_docs:
                    seen_docs.add(doc_content)
                    unique_results.append(result)
            
            # 计算综合分数
            for result in unique_results:
                base_score = result.get("similarity_score", 0.0)
                strategy_weight = result.get("strategy_weight", 0.5)
                
                # 综合分数 = 基础相似度 × 策略权重
                result["final_score"] = base_score * strategy_weight
            
            # 按综合分数排序
            unique_results.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
            
            # 返回前10个结果
            return unique_results[:10]
            
        except Exception as e:
            logger.error(f"❌ 结果融合排序失败: {e}")
            return []
    
    def _build_retrieval_summary(self, final_results: List[Dict], user_preferences: List, 
                                behavior_patterns: List) -> Dict[str, Any]:
        """构建检索摘要"""
        try:
            # 统计信息
            total_results = len(final_results)
            knowledge_types = list(set([r.get("knowledge_type", "") for r in final_results]))
            strategies = list(set([r.get("source", "") for r in final_results]))
            
            # 用户偏好摘要
            preference_summary = []
            for pref in user_preferences[:3]:
                preference_summary.append({
                    "intent": pref.intent_type,
                    "frequency": pref.frequency,
                    "score": pref.preference_score
                })
            
            # 行为模式摘要
            behavior_summary = {}
            for pattern in behavior_patterns:
                pattern_type = pattern.pattern_type
                if pattern_type not in behavior_summary:
                    behavior_summary[pattern_type] = []
                behavior_summary[pattern_type].append({
                    "data": pattern.pattern_data,
                    "frequency": pattern.frequency
                })
            
            # 构建最终摘要
            summary = {
                "total_results": total_results,
                "knowledge_types": knowledge_types,
                "strategies_used": strategies,
                "top_results": final_results[:5],  # 前5个结果
                "user_preferences": preference_summary,
                "behavior_patterns": behavior_summary,
                "retrieval_timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 检索摘要构建失败: {e}")
            return {"error": str(e), "results": []}
    
    def get_knowledge_suggestions(self, session_id: str, limit: int = 5) -> List[str]:
        """获取知识建议"""
        try:
            # 获取用户偏好
            preferences = self.knowledge_base.get_user_preferences(session_id)
            if not preferences:
                return []
            
            # 基于用户偏好生成建议
            suggestions = []
            for pref in preferences[:3]:
                intent = pref.intent_type
                if intent:
                    # 根据意图生成建议
                    intent_suggestions = self._generate_intent_suggestions(intent)
                    suggestions.extend(intent_suggestions)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"❌ 获取知识建议失败: {e}")
            return []
    
    def _generate_intent_suggestions(self, intent: str) -> List[str]:
        """根据意图生成建议"""
        suggestions_map = {
            "health_tracking": [
                "建议您记录今天的运动情况",
                "可以设置健康目标来跟踪进度",
                "定期体检有助于健康管理"
            ],
            "finance_management": [
                "建议制定月度预算计划",
                "可以记录日常消费情况",
                "考虑建立应急基金"
            ],
            "learning_planning": [
                "建议制定学习计划和时间表",
                "可以使用番茄工作法提高效率",
                "定期复习有助于知识巩固"
            ],
            "task_creation": [
                "建议将任务分解为小步骤",
                "可以设置任务优先级",
                "使用时间管理工具提高效率"
            ]
        }
        
        return suggestions_map.get(intent, [])


# 全局检索系统实例
retrieval_system = RetrievalSystem()

if __name__ == "__main__":
    # 测试智能检索系统
    print("🧠 智能检索系统测试开始...")
    
    # 模拟用户输入和理解结果
    test_user_input = "如何保持健康"
    test_understanding = {
        "intent": "health_tracking",
        "entities": {"health_goal": "保持健康"},
        "confidence": 0.85,
        "life_context": {
            "topic_analysis": {
                "primary_topic": "health",
                "is_topic_switch": False
            }
        }
    }
    
    # 执行检索
    results = retrieval_system.retrieve_knowledge(
        test_user_input, "test_session_002", test_understanding
    )
    
    print(f"📊 检索结果摘要:")
    print(f"  总结果数: {results.get('total_results', 0)}")
    print(f"  知识类型: {results.get('knowledge_types', [])}")
    print(f"  使用策略: {results.get('strategies_used', [])}")
    
    print(f"\n🔍 前3个结果:")
    for i, result in enumerate(results.get('top_results', [])[:3]):
        print(f"  {i+1}. 相似度: {result.get('final_score', 0):.3f}")
        print(f"     内容: {result.get('document', '')}")
        print(f"     来源: {result.get('source', '')}")
        print()
    
    print(f"🎯 用户偏好:")
    for pref in results.get('user_preferences', []):
        print(f"  - {pref.get('intent', '')}: 频率={pref.get('frequency', 0)}, 分数={pref.get('score', 0):.2f}")
    
    # 测试知识建议
    suggestions = retrieval_system.get_knowledge_suggestions("test_session_002", 3)
    print(f"\n💡 知识建议:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
