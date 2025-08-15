#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务响应生成器
Finance Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class FinanceResponseGenerator(BaseResponseGenerator):
    """财务相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "expense_recording",
            "budget_management",
            "investment_tracking",
            "financial_analysis"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成财务相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["numbers", "items", "time"])
        
        if intent == "expense_recording":
            return self._generate_expense_response(entities, context)
        elif intent == "budget_management":
            return "📊 我会帮您管理预算。建议制定月度预算计划，合理分配各项支出。"
        elif intent == "investment_tracking":
            return "📈 投资需要谨慎。建议分散投资，定期评估投资组合。"
        elif intent == "financial_analysis":
            return "📊 我会为您分析财务状况。建议定期查看消费记录，合理规划支出。"
        else:
            return "💰 财务管理很重要，我会帮您记录和分析财务数据。"
    
    def _generate_expense_response(self, entities: Dict, context: Dict) -> str:
        """生成消费记录响应"""
        numbers = entities.get("numbers", [])
        items = entities.get("items", [])
        
        if numbers and items:
            amount = self._get_entity_text(entities, "numbers")
            item = self._get_entity_text(entities, "items")
            return f"💰 记录消费：{item} {amount}。建议合理控制支出，保持预算平衡。"
        elif numbers:
            amount = self._get_entity_text(entities, "numbers")
            return f"💰 记录消费：{amount}。记得定期查看消费记录，合理规划支出。"
        else:
            return "💰 我理解您要记录消费，请告诉我具体的金额和项目。"
