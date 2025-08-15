#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感支持响应生成器
Emotion Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class EmotionResponseGenerator(BaseResponseGenerator):
    """情感支持相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "emotion_support",
            "stress_analysis",
            "motivation_boost"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成情感支持相关响应"""
        intent = understanding.get("intent", "")
        
        if intent == "emotion_support":
            return "❤️ 我理解您的感受。记住，情绪是正常的，如果需要倾诉，我随时在这里。"
        elif intent == "stress_analysis":
            return "😌 压力是生活的一部分。建议您：\n1. 适当休息和放松\n2. 寻求朋友和家人的支持\n3. 保持积极的心态"
        elif intent == "motivation_boost":
            return "💪 加油！您很棒！记住：\n1. 每个人都有自己的节奏\n2. 失败是成功的一部分\n3. 坚持就是胜利"
        else:
            return "❤️ 情感健康同样重要，我会一直支持您。"
