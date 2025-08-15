#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康响应生成器
Health Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class HealthResponseGenerator(BaseResponseGenerator):
    """健康相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "health_tracking",
            "exercise_recording", 
            "diet_management",
            "sleep_analysis",
            "mood_tracking"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成健康相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["activities", "numbers", "items"])
        
        if intent == "health_tracking" or intent == "exercise_recording":
            return self._generate_exercise_response(entities, context)
        elif intent == "diet_management":
            return self._generate_diet_response(entities, context)
        elif intent == "sleep_analysis":
            return self._generate_sleep_response(entities, context)
        elif intent == "mood_tracking":
            return "😊 我理解您的心情。记住，情绪是正常的，如果需要倾诉，我随时在这里。"
        else:
            return "💪 健康是人生最重要的财富，我会帮您记录和关注健康数据。"
    
    def _generate_exercise_response(self, entities: Dict, context: Dict) -> str:
        """生成运动相关响应"""
        activities = entities.get("activities", [])
        numbers = entities.get("numbers", [])
        
        if activities and numbers:
            activity = self._get_entity_text(entities, "activities")
            duration = self._get_entity_text(entities, "numbers")
            return f"🏃‍♂️ 太棒了！记录您的{activity}：{duration}。继续保持运动习惯，这对健康很有益！"
        elif activities:
            activity = self._get_entity_text(entities, "activities")
            return f"💪 好的，记录您的{activity}活动。建议您保持规律运动，每周3-5次。"
        else:
            return "💪 我理解您要记录运动，请告诉我具体的运动类型和时长。"
    
    def _generate_diet_response(self, entities: Dict, context: Dict) -> str:
        """生成饮食相关响应"""
        items = entities.get("items", [])
        
        if items:
            food = self._get_entity_text(entities, "items")
            return f"🍽️ 记录您的饮食：{food}。建议保持均衡饮食，多吃蔬菜水果。"
        else:
            return "🍽️ 我理解您要记录饮食，请告诉我您吃了什么。"
    
    def _generate_sleep_response(self, entities: Dict, context: Dict) -> str:
        """生成睡眠相关响应"""
        numbers = entities.get("numbers", [])
        
        if numbers:
            hours = self._get_entity_text(entities, "numbers")
            return f"😴 记录您的睡眠：{hours}。建议保持7-8小时的充足睡眠。"
        else:
            return "😴 我理解您要记录睡眠，请告诉我您的睡眠时长。"
