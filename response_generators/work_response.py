#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作响应生成器
Work Response Generator
"""

from .base_response import BaseResponseGenerator
from typing import Dict, List

class WorkResponseGenerator(BaseResponseGenerator):
    """工作相关响应生成器"""
    
    def setup_generator(self):
        """设置生成器"""
        self.supported_intents = [
            "task_creation",
            "schedule_management",
            "information_query",
            "file_management",
            "note_taking"
        ]
    
    def _generate_core_response(self, understanding: Dict, context: Dict) -> str:
        """生成工作相关响应"""
        intent = understanding.get("intent", "")
        entities = self._extract_entities(understanding, ["task", "time", "persons"])
        
        if intent == "task_creation":
            return self._generate_task_response(entities, context)
        elif intent == "schedule_management":
            return self._generate_schedule_response(entities, context)
        elif intent == "information_query":
            return "🔍 我正在为您查找相关信息，请稍等..."
        elif intent == "file_management":
            return "📁 我会帮您管理文件。建议定期整理和备份重要文件。"
        elif intent == "note_taking":
            return "📝 我会帮您记录重要信息。建议及时整理笔记。"
        else:
            return "💼 工作管理很重要，我会帮您提高工作效率。"
    
    def _generate_task_response(self, entities: Dict, context: Dict) -> str:
        """生成任务相关响应"""
        tasks = entities.get("task", [])
        time_entities = entities.get("time", [])
        
        if tasks:
            task_text = self._format_entity_list(tasks)
            response = f"好的，我已经记录下任务：{task_text}"
            
            if time_entities:
                time_text = self._format_entity_list(time_entities)
                response += f"，时间安排：{time_text}"
            
            response += "。我会提醒您按时完成。"
            return response
        else:
            return "我理解您想要创建任务，请告诉我具体的任务内容。"
    
    def _generate_schedule_response(self, entities: Dict, context: Dict) -> str:
        """生成日程相关响应"""
        time_entities = entities.get("time", [])
        tasks = entities.get("task", [])
        
        if time_entities and tasks:
            time_text = self._format_entity_list(time_entities)
            task_text = self._format_entity_list(tasks)
            return f"我已经为您安排了{time_text}的{task_text}。"
        elif time_entities:
            time_text = self._format_entity_list(time_entities)
            return f"好的，{time_text}的时间已经安排。"
        else:
            return "我理解您要安排日程，请告诉我具体的时间。"
