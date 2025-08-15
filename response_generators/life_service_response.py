#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生活服务响应生成器
Life Service Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class LifeServiceResponseGenerator(BaseResponseGenerator):
    """生活服务相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "shopping_list",
            "weather_query",
            "transportation_info",
            "entertainment_recommendation"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成生活服务相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["items", "locations"])
        
        if intent == "shopping_list":
            return self._generate_shopping_response(entities, context)
        elif intent == "weather_query":
            return "🌤️ 我会为您查询天气信息。建议根据天气情况合理安排出行。"
        elif intent == "transportation_info":
            return "🚗 我会为您提供交通信息。建议提前规划路线，合理安排时间。"
        elif intent == "entertainment_recommendation":
            return "🎬 我会为您推荐娱乐活动。建议根据个人喜好和时间安排选择。"
        else:
            return "🏠 生活服务很重要，我会帮您管理日常生活的各个方面。"
    
    def _generate_shopping_response(self, entities: Dict, context: Dict) -> str:
        """生成购物清单响应"""
        items = entities.get("items", [])
        
        if items:
            item_list = self._format_entity_list(items)
            return f"🛒 添加到购物清单：{item_list}。建议制定购物计划，避免冲动消费。"
        else:
            return "🛒 我理解您要添加购物清单，请告诉我需要购买的物品。"
