#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交响应生成器
Social Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class SocialResponseGenerator(BaseResponseGenerator):
    """社交相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "contact_management",
            "social_activity",
            "relationship_maintenance"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成社交相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["persons", "activities", "time"])
        
        if intent == "social_activity":
            return self._generate_activity_response(entities, context)
        elif intent == "contact_management":
            return "👥 我会帮您管理联系人信息。建议定期更新联系人资料。"
        elif intent == "relationship_maintenance":
            return "💝 关系维护很重要。建议定期联系朋友和家人。"
        else:
            return "👥 人际关系是生活的重要组成部分，我会帮您管理社交关系。"
    
    def _generate_activity_response(self, entities: Dict, context: Dict) -> str:
        """生成社交活动响应"""
        persons = entities.get("persons", [])
        activities = entities.get("activities", [])
        
        if persons and activities:
            person = self._get_entity_text(entities, "persons")
            activity = self._get_entity_text(entities, "activities")
            return f"👥 好的，记录社交活动：和{person}一起{activity}。人际关系很重要，保持联系。"
        elif persons:
            person = self._get_entity_text(entities, "persons")
            return f"👥 好的，记录与{person}的社交活动。记得保持联系，维护人际关系。"
        else:
            return "👥 我理解您要记录社交活动，请告诉我具体的人和活动。"
