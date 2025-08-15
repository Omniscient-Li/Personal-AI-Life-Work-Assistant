#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习响应生成器
Learning Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class LearningResponseGenerator(BaseResponseGenerator):
    """学习相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "learning_planning",
            "progress_tracking",
            "knowledge_organization",
            "skill_assessment"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成学习相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["activities", "items", "time"])
        
        if intent == "learning_planning":
            return self._generate_planning_response(entities, context)
        elif intent == "progress_tracking":
            return "📈 学习进度追踪很重要。建议定期回顾和总结学习成果。"
        elif intent == "knowledge_organization":
            return "📚 知识整理是学习的重要环节。建议建立知识体系，定期复习。"
        elif intent == "skill_assessment":
            return "🎯 技能评估有助于了解学习效果。建议定期进行自我评估。"
        else:
            return "📚 终身学习是人生的重要部分，我会帮您规划和管理学习。"
    
    def _generate_planning_response(self, entities: Dict, context: Dict) -> str:
        """生成学习规划响应"""
        activities = entities.get("activities", [])
        
        if activities:
            activity = self._get_entity_text(entities, "activities")
            return f"📚 好的，安排学习计划：{activity}。建议制定具体的学习目标和时间安排。"
        else:
            return "📚 我理解您要制定学习计划，请告诉我具体的学习内容。"
