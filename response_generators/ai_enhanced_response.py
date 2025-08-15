#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI增强响应生成器
AI-Enhanced Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List, Optional
from openai import AzureOpenAI
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入知识库模块
try:
    from retrieval_system import retrieval_system
    KNOWLEDGE_ENABLED = True
except ImportError:
    KNOWLEDGE_ENABLED = False
    print("⚠️ 知识库模块未找到，将使用基础响应生成")

class AIEnhancedResponseGenerator(BaseResponseGenerator):
    """AI增强的响应生成器"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = None
        self.setup_ai_client()
        
    def setup_ai_client(self):
        """设置AI客户端"""
        try:
            self.ai_client = AzureOpenAI(
                api_key="27d207295cf547959521bd46c91c8ee7",
                api_version="2024-02-15-preview",
                azure_endpoint="https://rj-llm-us-east-2.openai.azure.com/",
                azure_deployment="SL-Azure-gpt-4.1"
            )
            print("✅ AI增强响应生成器已初始化")
        except Exception as e:
            print(f"⚠️ AI客户端设置失败: {e}")
            self.ai_client = None
    
    def setup_generator(self):
        """设置生成器"""
        # 支持所有意图，因为AI可以处理任何类型
        self.supported_intents = [
            "health_tracking", "exercise_recording", "diet_management", "sleep_analysis", "mood_tracking",
            "expense_recording", "budget_management", "investment_tracking", "financial_analysis",
            "learning_planning", "progress_tracking", "knowledge_organization", "skill_assessment",
            "contact_management", "social_activity", "relationship_maintenance",
            "task_creation", "schedule_management", "information_query", "file_management", "note_taking",
            "shopping_list", "weather_query", "transportation_info", "entertainment_recommendation",
            "emotion_support", "stress_analysis", "motivation_boost",
            "general_chat"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """使用AI生成个性化响应"""
        if not self.ai_client:
            return self._generate_fallback_response(understanding, context)
        
        try:
            # 构建个性化提示
            prompt = self._build_personalized_prompt(understanding, context)
            
            # 调用AI生成响应
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 记录响应生成
            self.log_response_generation(understanding.get("intent", ""), ai_response, context)
            
            return ai_response
            
        except Exception as e:
            print(f"❌ AI响应生成失败: {e}")
            return self._generate_fallback_response(understanding, context)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个名为"贾维斯"的智能生活助手，专门帮助用户管理生活的各个方面。

你的特点：
1. 专业高效 - 提供准确、实用的建议和解决方案
2. 逻辑清晰 - 分析问题有条理，建议具体可行
3. 个性化 - 根据用户的具体情况和偏好给出建议
4. 简洁直接 - 回答简洁明了，直击要点
5. 客观理性 - 基于事实和逻辑，避免过度情感化

你的能力范围：
- 健康管理：运动计划、饮食建议、睡眠优化、健康监测
- 财务管理：消费分析、预算规划、投资建议、财务优化
- 学习成长：学习规划、进度跟踪、知识整理、技能提升
- 社交关系：人际关系管理、社交活动规划、沟通技巧
- 工作管理：任务规划、时间管理、效率提升、项目管理
- 生活服务：购物建议、天气信息、交通规划、生活便利
- 情感支持：理性分析、实用建议、压力管理

请根据用户的具体情况，提供专业、实用、高效的回应。"""
    
    def _build_personalized_prompt(self, understanding: Dict, context: Dict) -> str:
        """构建个性化提示"""
        intent = understanding.get("intent", "")
        entities = understanding.get("entities", {})
        original_text = understanding.get("original_text", "")
        confidence = understanding.get("confidence", 0)
        multiple_intents = understanding.get("multiple_intents", [])
        session_id = context.get("session_id", "unknown")
        
        # 获取用户历史信息
        user_preferences = context.get("user_preferences", {})
        conversation_history = context.get("conversation_history", [])
        active_topics = context.get("active_topics", {})
        topic_history = context.get("topic_history", [])
        
        # 分析用户模式
        user_patterns = self._analyze_user_patterns(conversation_history, user_preferences)
        
        # 知识库检索
        knowledge_context = ""
        if KNOWLEDGE_ENABLED:
            try:
                knowledge_results = retrieval_system.retrieve_knowledge(
                    original_text, session_id, understanding, context
                )
                
                if knowledge_results and not knowledge_results.get("error"):
                    top_results = knowledge_results.get("top_results", [])
                    if top_results:
                        knowledge_context = "相关知识:\n"
                        for i, result in enumerate(top_results[:3]):
                            knowledge_context += f"{i+1}. {result.get('document', '')}\n"
                        knowledge_context += "\n"
                        
                        # 添加知识建议
                        suggestions = retrieval_system.get_knowledge_suggestions(session_id, 2)
                        if suggestions:
                            knowledge_context += "建议:\n"
                            for suggestion in suggestions:
                                knowledge_context += f"- {suggestion}\n"
                            knowledge_context += "\n"
            except Exception as e:
                print(f"⚠️ 知识库检索失败: {e}")
        
        # 构建提示
        prompt_parts = []
        
        # 1. 当前输入信息
        prompt_parts.append(f"用户当前输入：{original_text}")
        prompt_parts.append(f"主要意图：{intent} (置信度：{confidence:.2f})")
        
        # 2. 多意图信息
        if multiple_intents:
            intent_info = []
            for intent_data in multiple_intents:
                intent_info.append(f"{intent_data['text']} -> {intent_data['intent']}")
            prompt_parts.append(f"识别到的多个意图：{'; '.join(intent_info)}")
        
        # 3. 提取的实体信息
        if entities:
            entity_info = []
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entity_info.append(f"{entity_type}: {', '.join(entity_list)}")
            if entity_info:
                prompt_parts.append(f"提取信息：{'; '.join(entity_info)}")
        
        # 4. 知识库上下文
        if knowledge_context:
            prompt_parts.append(knowledge_context)
        
        # 5. 活跃话题信息
        if active_topics:
            topic_info = []
            for topic, data in active_topics.items():
                topic_info.append(f"{topic}({data['turn_count']}轮): {', '.join(data['intents'])}")
            prompt_parts.append(f"当前活跃话题：{'; '.join(topic_info)}")
        
        # 6. 话题历史
        if topic_history:
            recent_topics = [record["topic"] for record in topic_history[-3:]]
            prompt_parts.append(f"最近话题：{', '.join(recent_topics)}")
        
        # 7. 用户历史模式
        if user_patterns:
            pattern_info = []
            for pattern, details in user_patterns.items():
                pattern_info.append(f"{pattern}: {details}")
            prompt_parts.append(f"用户模式：{'; '.join(pattern_info)}")
        
        # 8. 用户偏好
        if user_preferences:
            pref_info = []
            for pref_type, pref_value in user_preferences.items():
                if pref_type != "conversation_history":
                    pref_info.append(f"{pref_type}: {pref_value}")
            if pref_info:
                prompt_parts.append(f"用户偏好：{'; '.join(pref_info)}")
        
        # 9. 主动建议（如果有）
        proactive_suggestions = context.get("proactive_suggestions", [])
        if proactive_suggestions:
            suggestion_text = "主动建议:\n"
            for i, suggestion in enumerate(proactive_suggestions[:2]):  # 只显示前2个建议
                suggestion_text += f"{i+1}. [{suggestion.get('priority', 3)}] {suggestion.get('title', '')}: {suggestion.get('content', '')}\n"
            prompt_parts.append(suggestion_text)
        
        # 10. 生成要求
        if len(multiple_intents) > 1:
            prompt_parts.append("用户输入包含多个意图，请分别回应每个意图，并给出综合建议。")
        else:
            if knowledge_context:
                prompt_parts.append("请根据以上信息，结合相关知识，生成一个专业、实用、高效的回应。")
            else:
                prompt_parts.append("请根据以上信息，生成一个专业、实用、高效的回应。")
        
        # 如果有主动建议，要求AI在回应中提及
        if proactive_suggestions:
            prompt_parts.append("如果提供了主动建议，请在回应中适当提及这些建议，让用户知道您注意到了他们的使用模式。")
        
        return "\n".join(prompt_parts)
    
    def _analyze_user_patterns(self, conversation_history: List[Dict], user_preferences: Dict) -> Dict:
        """分析用户模式"""
        patterns = {}
        
        if not conversation_history:
            return patterns
        
        # 分析意图偏好
        intent_counts = {}
        for turn in conversation_history:
            intent = turn.get("understanding", {}).get("intent", "")
            if intent:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        if intent_counts:
            most_common_intent = max(intent_counts, key=intent_counts.get)
            patterns["常用意图"] = f"{most_common_intent} ({intent_counts[most_common_intent]}次)"
        
        # 分析情感状态
        emotion_states = []
        for turn in conversation_history:
            emotion = turn.get("understanding", {}).get("context_understanding", {}).get("emotion", "")
            if emotion:
                emotion_states.append(emotion)
        
        if emotion_states:
            positive_count = emotion_states.count("positive")
            negative_count = emotion_states.count("negative")
            if positive_count > negative_count:
                patterns["情感倾向"] = "积极乐观"
            elif negative_count > positive_count:
                patterns["情感倾向"] = "需要更多支持"
            else:
                patterns["情感倾向"] = "情感稳定"
        
        # 分析时间模式
        time_preferences = user_preferences.get("time_preferences", [])
        if time_preferences:
            patterns["时间偏好"] = f"常用时间：{', '.join(time_preferences[:3])}"
        
        return patterns
    
    def _get_recent_topics(self, conversation_history: List[Dict], count: int = 3) -> List[str]:
        """获取最近的话题"""
        recent_topics = []
        for turn in reversed(conversation_history[-count:]):
            intent = turn.get("understanding", {}).get("intent", "")
            if intent and intent not in recent_topics:
                recent_topics.append(intent)
        return recent_topics
    
    def _generate_fallback_response(self, understanding: Dict, context: Dict) -> str:
        """生成后备响应"""
        intent = understanding.get("intent", "")
        original_text = understanding.get("original_text", "")
        
        # 简单的后备响应
        fallback_responses = {
            "health_tracking": "💪 我理解您要记录健康信息，请告诉我具体的情况。",
            "expense_recording": "💰 我理解您要记录消费，请告诉我具体的金额和项目。",
            "learning_planning": "📚 我理解您要制定学习计划，请告诉我具体的学习内容。",
            "social_activity": "👥 我理解您要记录社交活动，请告诉我具体的人和活动。",
            "task_creation": "📋 我理解您要创建任务，请告诉我具体的任务内容。",
            "emotion_support": "❤️ 我理解您的感受，如果需要倾诉，我随时在这里。"
        }
        
        return fallback_responses.get(intent, f"我理解您的意思：{original_text}。有什么我可以帮助您的吗？")
