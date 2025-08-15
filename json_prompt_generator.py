#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON格式Prompt生成器
将AI生成的Prompt转换为结构化的JSON格式
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PromptContext:
    """Prompt上下文信息"""
    task_type: str
    user_input: str
    conversation_history: List[Dict]
    user_profile: Dict[str, Any]
    current_goals: List[str]
    mood_state: str
    available_time: str = None
    location: str = None
    weather: str = None

class JSONPromptGenerator:
    """JSON格式Prompt生成器"""
    
    def __init__(self):
        self.prompt_templates = {
            "health_advice": self._get_health_advice_template,
            "work_assistant": self._get_work_assistant_template,
            "schedule_assistant": self._get_schedule_assistant_template,
            "learning_coach": self._get_learning_coach_template,
            "conversation": self._get_general_template
        }
    
    def generate_json_prompt(self, context: PromptContext) -> Dict[str, Any]:
        """生成结构化JSON Prompt（字典对象）"""
        template_generator = self.prompt_templates.get(context.task_type, self._get_general_template)
        json_prompt = template_generator(context)
        return {"success": True, "data": json_prompt, "error": None, "meta": {"generator": "JSONPromptGenerator"}}
    
    def _get_health_advice_template(self, context: PromptContext) -> Dict[str, Any]:
        """健康建议的JSON模板"""
        return {
            "role": "health_advisor",
            "user_context": {
                "age": context.user_profile.get("age", "未知"),
                "occupation": context.user_profile.get("occupation", "未知"),
                "health_goals": context.current_goals,
                "mood_state": context.mood_state,
                "available_time": context.available_time,
                "location": context.location,
                "weather": context.weather
            },
            "task_description": "为用户提供个性化的睡眠改善建议",
            "required_outputs": [
                {
                    "type": "sleep_improvement_tips",
                    "description": "具体的睡眠改善建议",
                    "format": "numbered_list",
                    "count": "5-7条",
                    "priority": "high"
                },
                {
                    "type": "stress_management",
                    "description": "工作压力管理方法",
                    "format": "actionable_steps",
                    "count": "3-5条",
                    "priority": "high"
                },
                {
                    "type": "relaxation_techniques",
                    "description": "睡前放松技巧",
                    "format": "detailed_instructions",
                    "count": "3-4种",
                    "priority": "medium"
                },
                {
                    "type": "action_plan",
                    "description": "可执行的行动计划",
                    "format": "timeline_based",
                    "timeframe": "1-2周",
                    "priority": "high"
                },
                {
                    "type": "progress_tracking",
                    "description": "进度跟踪方法",
                    "format": "metrics_and_tools",
                    "tools": ["app", "journal", "checklist"],
                    "priority": "medium"
                }
            ],
            "constraints": [
                "考虑用户的工作压力和时间限制",
                "提供具体可操作的建议",
                "包含时间安排和频率建议",
                "考虑用户的实际情况和偏好",
                "避免过于复杂的建议"
            ],
            "output_format": {
                "structure": "organized_sections",
                "language": "professional_but_friendly",
                "include_emojis": True,
                "include_examples": True,
                "include_timeline": True
            },
            "quality_standards": {
                "clarity": "high",
                "actionability": "high",
                "personalization": "high",
                "scientific_basis": "medium"
            }
        }
    
    def _get_work_assistant_template(self, context: PromptContext) -> Dict[str, Any]:
        """工作助手的JSON模板"""
        return {
            "role": "productivity_consultant",
            "user_context": {
                "age": context.user_profile.get("age", "未知"),
                "occupation": context.user_profile.get("occupation", "未知"),
                "work_style": context.user_profile.get("work_style", "未知"),
                "current_projects": context.user_profile.get("current_projects", []),
                "stress_level": context.user_profile.get("stress_level", "未知"),
                "productivity_patterns": context.user_profile.get("productivity_patterns", [])
            },
            "task_description": "帮助用户提高工作效率和生产力",
            "required_outputs": [
                {
                    "type": "efficiency_strategies",
                    "description": "针对性的效率提升策略",
                    "format": "prioritized_list",
                    "priority_levels": ["high", "medium", "low"],
                    "count": "5-7条"
                },
                {
                    "type": "time_management",
                    "description": "时间管理技巧",
                    "format": "practical_tips",
                    "count": "5-7条",
                    "include_tools": True
                },
                {
                    "type": "stress_relief",
                    "description": "压力缓解方法",
                    "format": "quick_actions",
                    "time_required": "5-15分钟",
                    "count": "3-5种"
                },
                {
                    "type": "project_management",
                    "description": "项目进度管理建议",
                    "format": "framework_based",
                    "tools": ["kanban", "timeline", "checklist"],
                    "include_templates": True
                },
                {
                    "type": "improvement_plan",
                    "description": "可执行的改进计划",
                    "format": "weekly_milestones",
                    "duration": "4-6周",
                    "include_checkpoints": True
                }
            ],
            "constraints": [
                "结合用户的工作风格和当前压力状况",
                "提供切实可行的建议",
                "考虑项目deadline和优先级",
                "平衡效率和压力管理",
                "避免过于激进的改变"
            ],
            "output_format": {
                "structure": "problem_solution_framework",
                "language": "professional_and_encouraging",
                "include_emojis": True,
                "include_timeline": True,
                "include_metrics": True
            },
            "quality_standards": {
                "clarity": "high",
                "actionability": "high",
                "personalization": "high",
                "measurability": "medium"
            }
        }
    
    def _get_schedule_assistant_template(self, context: PromptContext) -> Dict[str, Any]:
        """时间安排的JSON模板"""
        return {
            "role": "time_management_specialist",
            "user_context": {
                "user_input": context.user_input,
                "available_time": context.available_time,
                "current_goals": context.current_goals,
                "location": context.location
            },
            "task_description": "帮助用户合理安排时间和日程",
            "required_outputs": [
                {
                    "type": "time_planning",
                    "description": "时间规划建议",
                    "format": "timeline_based",
                    "include_buffer_time": True,
                    "precision": "30分钟"
                },
                {
                    "type": "time_allocation",
                    "description": "时间分配方案",
                    "format": "detailed_schedule",
                    "precision": "30分钟",
                    "include_transitions": True
                },
                {
                    "type": "optimization_tips",
                    "description": "时间优化建议",
                    "format": "actionable_tips",
                    "count": "3-5条",
                    "focus": "efficiency"
                },
                {
                    "type": "conflict_resolution",
                    "description": "时间冲突解决方案",
                    "format": "if_then_scenarios",
                    "include_alternatives": True,
                    "count": "2-3个"
                },
                {
                    "type": "preparation_checklist",
                    "description": "准备事项清单",
                    "format": "checklist",
                    "categories": ["materials", "time", "location", "backup_plans"],
                    "include_priorities": True
                }
            ],
            "constraints": [
                "考虑用户的具体时间安排",
                "预留足够的缓冲时间",
                "提供备选方案",
                "确保建议的可行性",
                "考虑交通和准备时间"
            ],
            "output_format": {
                "structure": "chronological_order",
                "language": "clear_and_concise",
                "include_emojis": True,
                "include_time_estimates": True,
                "include_visual_elements": True
            },
            "quality_standards": {
                "clarity": "high",
                "actionability": "high",
                "realism": "high",
                "flexibility": "medium"
            }
        }
    
    def _get_learning_coach_template(self, context: PromptContext) -> Dict[str, Any]:
        """学习教练的JSON模板"""
        return {
            "role": "learning_coach",
            "user_context": {
                "age": context.user_profile.get("age", "未知"),
                "occupation": context.user_profile.get("occupation", "未知"),
                "learning_style": context.user_profile.get("learning_style", "未知"),
                "available_time": context.user_profile.get("available_time", "未知"),
                "current_skills": context.user_profile.get("current_skills", []),
                "learning_goals": context.user_profile.get("learning_goals", [])
            },
            "task_description": "帮助用户制定个性化学习计划",
            "required_outputs": [
                {
                    "type": "learning_path",
                    "description": "个性化学习路径规划",
                    "format": "structured_curriculum",
                    "include_milestones": True,
                    "timeframe": "3-6个月"
                },
                {
                    "type": "daily_plan",
                    "description": "每日学习计划",
                    "format": "time_based_schedule",
                    "include_breaks": True,
                    "flexibility": "medium"
                },
                {
                    "type": "practice_projects",
                    "description": "实践项目建议",
                    "format": "project_based_learning",
                    "difficulty_progression": True,
                    "count": "5-8个"
                },
                {
                    "type": "learning_resources",
                    "description": "学习资源推荐",
                    "format": "categorized_resources",
                    "categories": ["books", "videos", "courses", "tools"],
                    "include_free_options": True
                },
                {
                    "type": "progress_assessment",
                    "description": "进度评估方法",
                    "format": "multi_method_evaluation",
                    "methods": ["self_assessment", "project_review", "skill_testing"],
                    "frequency": "weekly"
                }
            ],
            "constraints": [
                "考虑用户的学习风格和可用时间",
                "制定循序渐进的学习计划",
                "平衡理论与实践",
                "提供可执行的行动步骤",
                "考虑学习成本和资源可获得性"
            ],
            "output_format": {
                "structure": "progressive_learning_framework",
                "language": "encouraging_and_clear",
                "include_emojis": True,
                "include_timeline": True,
                "include_resources": True
            },
            "quality_standards": {
                "clarity": "high",
                "actionability": "high",
                "personalization": "high",
                "motivation": "high"
            }
        }
    
    def _get_general_template(self, context: PromptContext) -> Dict[str, Any]:
        """通用助手的JSON模板"""
        return {
            "role": "general_assistant",
            "user_context": {
                "user_input": context.user_input,
                "current_goals": context.current_goals,
                "mood_state": context.mood_state
            },
            "task_description": "根据用户需求提供一般性帮助和建议",
            "required_outputs": [
                {
                    "type": "general_advice",
                    "description": "一般性建议",
                    "format": "friendly_suggestions",
                    "tone": "helpful_and_encouraging",
                    "count": "3-5条"
                },
                {
                    "type": "next_steps",
                    "description": "下一步行动建议",
                    "format": "actionable_steps",
                    "count": "2-3条",
                    "priority": "medium"
                }
            ],
            "constraints": [
                "保持友好和专业的语调",
                "提供有用的建议",
                "鼓励用户进一步说明需求",
                "避免过于复杂的建议"
            ],
            "output_format": {
                "structure": "simple_and_clear",
                "language": "friendly_and_professional",
                "include_emojis": True,
                "include_next_steps": True
            },
            "quality_standards": {
                "clarity": "high",
                "helpfulness": "high",
                "friendliness": "high",
                "simplicity": "medium"
            }
        }

def demo_json_prompt_generation():
    """演示JSON Prompt生成功能"""
    print("🎯 JSON格式Prompt生成器演示")
    print("=" * 60)
    
    generator = JSONPromptGenerator()
    
    # 创建测试上下文
    test_contexts = [
        PromptContext(
            task_type="health_advice",
            user_input="我想提高睡眠质量，最近总是失眠",
            conversation_history=[],
            user_profile={"age": 28, "occupation": "软件工程师"},
            current_goals=["改善睡眠", "减少压力"],
            mood_state="压力较大",
            available_time="晚上9点后",
            location="家里",
            weather="阴天"
        ),
        PromptContext(
            task_type="schedule_assistant",
            user_input="我明天下午三点可能有个会议,然后晚上8点和朋友约好了去打球",
            conversation_history=[],
            user_profile={"age": 30, "occupation": "产品经理"},
            current_goals=["合理安排时间"],
            mood_state="正常",
            available_time="明天全天",
            location="办公室和球场"
        )
    ]
    
    for i, context in enumerate(test_contexts, 1):
        print(f"\n📋 测试场景 {i}: {context.task_type}")
        print("-" * 40)
        print(f"用户输入: {context.user_input}")
        
        # 生成JSON格式的Prompt
        json_prompt = generator.generate_json_prompt(context)
        
        print(f"\n🤖 生成的JSON Prompt:")
        print(json_prompt)
        
        # 解析JSON并显示关键信息
        try:
            prompt_data = json.loads(json_prompt)
            print(f"\n📊 Prompt分析:")
            print(f"  角色: {prompt_data.get('role', '未知')}")
            print(f"  任务描述: {prompt_data.get('task_description', '未知')}")
            print(f"  输出要求数量: {len(prompt_data.get('required_outputs', []))}")
            print(f"  约束条件数量: {len(prompt_data.get('constraints', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")

if __name__ == "__main__":
    demo_json_prompt_generation()
