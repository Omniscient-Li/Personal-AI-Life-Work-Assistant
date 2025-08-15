#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础响应生成器
Base Response Generator
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

class BaseResponseGenerator(ABC):
    """响应生成器基类"""
    
    def __init__(self):
        self.generator_name = self.__class__.__name__
        self.supported_intents = []
        self.response_templates = {}
        self.setup_generator()
    
    @abstractmethod
    def setup_generator(self):
        """设置生成器，定义支持的意图和响应模板"""
        pass
    
    def can_handle(self, intent: str) -> bool:
        """检查是否可以处理该意图"""
        return intent in self.supported_intents
    
    def generate_response(self, understanding: Dict, context: Dict) -> str:
        """
        生成响应
        
        Args:
            understanding: 理解结果
            context: 对话上下文
            
        Returns:
            生成的响应文本
        """
        intent = understanding.get("intent", "")
        
        if not self.can_handle(intent):
            return self._generate_fallback_response(understanding, context)
        
        # 添加个性化元素
        response = self._generate_core_response(understanding, context)
        response = self._add_personalization(response, context)
        
        return response
    
    @abstractmethod
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成核心响应"""
        pass
    
    def _generate_fallback_response(self, understanding: Dict, context: Dict) -> str:
        """生成后备响应"""
        return f"我理解您的意思，但我在{self.generator_name}中还没有针对这个意图的专门处理。"
    
    def _add_personalization(self, response: str, context: Dict) -> str:
        """添加个性化元素"""
        user_preferences = context.get("user_preferences", {})
        
        # 根据用户偏好调整响应风格
        if user_preferences.get("preferred_style") == "formal":
            response = self._make_formal(response)
        elif user_preferences.get("preferred_style") == "casual":
            response = self._make_casual(response)
        
        return response
    
    def _make_formal(self, response: str) -> str:
        """使响应更正式"""
        # 可以添加正式化的逻辑
        return response
    
    def _make_casual(self, response: str) -> str:
        """使响应更随意"""
        # 可以添加随意化的逻辑
        return response
    
    def _extract_entities(self, understanding: Dict, entity_types: List[str]) -> Dict[str, List[str]]:
        """提取指定类型的实体"""
        entities = understanding.get("entities", {})
        result = {}
        
        for entity_type in entity_types:
            if entity_type in entities:
                entity_list = entities[entity_type]
                # 确保返回字符串列表
                string_entities = []
                for entity in entity_list:
                    if isinstance(entity, str):
                        string_entities.append(entity)
                    elif isinstance(entity, dict):
                        if "text" in entity:
                            string_entities.append(entity["text"])
                        elif "value" in entity:
                            string_entities.append(str(entity["value"]))
                result[entity_type] = string_entities
        
        return result
    
    def _get_entity_text(self, entities: Dict[str, List[str]], entity_type: str, default: str = "") -> str:
        """获取实体文本"""
        if entity_type in entities and entities[entity_type]:
            return entities[entity_type][0]
        return default
    
    def _format_entity_list(self, entities: List[str], separator: str = "、") -> str:
        """格式化实体列表"""
        if not entities:
            return ""
        return separator.join(entities)
    
    def _get_user_preference(self, context: Dict, preference_key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        user_preferences = context.get("user_preferences", {})
        return user_preferences.get(preference_key, default)
    
    def _get_conversation_history(self, context: Dict, turns: int = 3) -> List[Dict]:
        """获取对话历史"""
        conversation_history = context.get("conversation_history", [])
        return conversation_history[-turns:] if conversation_history else []
    
    def _is_first_time_topic(self, context: Dict, topic: str) -> bool:
        """检查是否是首次讨论该话题"""
        conversation_history = context.get("conversation_history", [])
        for turn in conversation_history:
            if turn.get("understanding", {}).get("intent") == topic:
                return False
        return True
    
    def _get_response_template(self, template_key: str, **kwargs) -> str:
        """获取响应模板"""
        template = self.response_templates.get(template_key, "")
        return template.format(**kwargs) if template else ""
    
    def log_response_generation(self, intent: str, response: str, context: Dict):
        """记录响应生成日志"""
        print(f"🎯 {self.generator_name} 生成响应:")
        print(f"   意图: {intent}")
        print(f"   响应: {response[:50]}...")
        print(f"   时间: {datetime.now().strftime('%H:%M:%S')}")
