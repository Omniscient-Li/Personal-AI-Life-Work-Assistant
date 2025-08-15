#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt生成器系统 - 主程序
专门用于测试和演示AI自动生成Prompt的功能
"""

import sys
import os
import json
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_prompt_generator import AIPromptGenerator, PromptContext, GeneratedPrompt, PromptManager
from config import Config
from orchestrator import PromptOrchestrator, OrchestratorContext

class AIPromptSystem:
    """AI Prompt生成器系统主类"""
    
    def __init__(self):
        self.config = Config()
        self.prompt_generator = None
        self.prompt_manager = PromptManager()
        
        # 初始化AI Prompt生成器
        self._initialize_ai_generator()
    
    def _initialize_ai_generator(self):
        """初始化AI Prompt生成器"""
        try:
            # 检查是否有Azure OpenAI配置
            if self.config.is_azure_configured():
                print("✅ 使用Azure OpenAI配置")
                # 这里可以创建Azure OpenAI客户端
                # 暂时使用模拟模式
                self.prompt_generator = None
            else:
                print("ℹ️ 使用模拟模式（需要配置Azure OpenAI）")
                self.prompt_generator = None
                
        except Exception as e:
            print(f"⚠️ AI生成器初始化失败: {e}")
            self.prompt_generator = None
    
    def demo_basic_functionality(self, output_mode: str = "text"):
        """演示基础功能（支持结构化输出）"""
        header = {"type": "demo_basic", "title": "AI Prompt生成器基础功能演示"}
        if output_mode == "text":
            print("🚀 AI Prompt生成器基础功能演示")
            print("=" * 60)
        
        # 创建示例上下文
        context = PromptContext(
            task_type="health_advice",
            user_input="我想提高睡眠质量，最近总是失眠",
            conversation_history=[
                {"user_input": "最近工作压力很大", "assistant_response": "我理解你的感受..."},
                {"user_input": "晚上总是睡不着", "assistant_response": "睡眠问题确实很常见..."}
            ],
            user_profile={"age": 28, "occupation": "软件工程师", "health_goals": ["改善睡眠", "减少压力"]},
            current_goals=["改善睡眠质量", "提高工作效率"],
            mood_state="压力较大，有些焦虑",
            available_time="晚上9点后",
            location="家里",
            weather="阴天"
        )
        
        if output_mode == "text":
            print(f"任务类型: {context.task_type}")
            print(f"用户输入: {context.user_input}")
            print(f"用户目标: {', '.join(context.current_goals)}")
            print(f"心情状态: {context.mood_state}")
            print(f"可用时间: {context.available_time}")
        
        # 生成Prompt（模拟模式）
        if self.prompt_generator:
            result = self.prompt_generator.generate_prompt_structured(context)
            if output_mode == "json":
                print(json.dumps({**header, **result}, ensure_ascii=False))
            else:
                print("\n🤖 使用AI生成Prompt...")
                print(result.get("data", {}).get("prompt_text", ""))
        else:
            mock_prompt = self._generate_mock_prompt(context)
            advice = self._generate_actual_advice(context, mock_prompt)
            result = {
                "success": True,
                "data": {
                    "prompt_text": mock_prompt,
                    "confidence_score": 0.6,
                    "reasoning": "mock_mode",
                    "optimization_suggestions": ["可增加输出格式要求"],
                    "context_used": {
                        "task_type": context.task_type,
                        "user_input": context.user_input
                    },
                    "advice_text": advice
                },
                "error": None,
                "meta": {"mode": "mock"}
            }
            if output_mode == "json":
                print(json.dumps({**header, **result}, ensure_ascii=False))
            else:
                print("\n🤖 模拟模式 - 生成个性化Prompt...")
                print(mock_prompt)
                print("\n💡 基于Prompt生成的建议:")
                print(advice)
        
        if output_mode == "text":
            print("\n💡 这个系统可以：")
            print("1. 自动生成个性化的Prompt")
            print("2. 基于用户反馈优化Prompt")
            print("3. 评估Prompt质量")
            print("4. 管理Prompt历史")
            print("5. 提供性能统计")
    
    def _generate_mock_prompt(self, context: PromptContext) -> str:
        """生成模拟的Prompt（用于演示）"""
        if context.task_type == "health_advice":
            return f"""你是一个专业的健康顾问，专门帮助{context.user_profile.get('age', '年轻')}岁的{context.user_profile.get('occupation', '职场人士')}改善睡眠质量。

基于用户信息：
- 当前目标：{', '.join(context.current_goals)}
- 工作状态：{context.user_profile.get('work_schedule', '标准工作时间')}
- 运动频率：{context.user_profile.get('exercise_frequency', '偶尔运动')}
- 睡眠时间：{context.user_profile.get('sleep_time', '标准睡眠时间')}

请提供：
1. 个性化的睡眠改善建议
2. 工作压力管理方法
3. 具体的睡前放松技巧
4. 可执行的行动计划
5. 进度跟踪方法

注意：考虑用户的工作压力和可用时间，提供实用的建议。"""
        
        elif context.task_type == "work_assistant":
            return f"""你是一个专业的工作效率顾问，专门帮助{context.user_profile.get('occupation', '职场人士')}提高工作效率。

基于用户信息：
- 工作风格：{context.user_profile.get('work_style', '标准工作风格')}
- 当前项目：{', '.join(context.user_profile.get('current_projects', ['一般项目']))}
- 压力水平：{context.user_profile.get('stress_level', '中等')}
- 效率模式：{', '.join(context.user_profile.get('productivity_patterns', ['标准模式']))}

请提供：
1. 针对性的效率提升策略
2. 时间管理技巧
3. 压力缓解方法
4. 项目进度管理建议
5. 可执行的改进计划

注意：结合用户的工作风格和当前压力状况，提供切实可行的建议。"""
        
        elif context.task_type == "schedule_assistant":
            return f"""你是一个专业的时间管理顾问，专门帮助用户合理安排日程。

基于用户信息：
- 用户需求：{context.user_input}
- 可用时间：{context.available_time or '灵活时间'}
- 当前目标：{', '.join(context.current_goals)}

请提供：
1. 时间安排建议
2. 优先级排序
3. 冲突解决方案
4. 时间管理技巧
5. 可执行的行动计划

注意：考虑用户的具体时间安排和需求，提供实用的建议。"""
        
        else:
            return "你是一个智能助手，请根据用户需求提供帮助。"
    
    def _generate_actual_advice(self, context: PromptContext, prompt: str) -> str:
        """基于Prompt生成实际的建议"""
        if context.task_type == "health_advice":
            return f"""基于你的情况（{context.user_profile.get('age', '年轻')}岁{context.user_profile.get('occupation', '职场人士')}），我建议：

1. 🕐 固定作息时间
   - 每天23:00前上床，07:00起床
   - 周末也要保持规律，避免生物钟紊乱

2. 🧘‍♀️ 睡前放松技巧
   - 21:00后避免使用电子设备
   - 尝试冥想或深呼吸练习（10-15分钟）
   - 温水泡脚或泡澡（20分钟）

3. 🏃‍♂️ 运动建议
   - 每周3-4次有氧运动（快走、慢跑）
   - 避免睡前2小时剧烈运动
   - 可以尝试瑜伽或太极

4. 💼 工作压力管理
   - 使用番茄工作法（25分钟专注+5分钟休息）
   - 下班前1小时整理第二天的工作计划
   - 学会说"不"，避免过度承诺

5. 📊 进度跟踪
   - 使用睡眠追踪App记录睡眠质量
   - 每周评估改善效果
   - 根据反馈调整策略

记住：改善睡眠是一个渐进的过程，需要耐心和坚持！"""
        
        elif context.task_type == "work_assistant":
            return f"""针对你的工作效率问题，我建议：

1. 📋 任务管理
   - 使用四象限法则（重要+紧急、重要+不紧急、不重要+紧急、不重要+不紧急）
   - 每天只设定3个最重要的任务
   - 将大任务拆分为可执行的小步骤

2. ⏰ 时间管理
   - 上午9:00-11:00处理最重要的工作（精力最充沛）
   - 下午2:00-4:00处理需要创造力的任务
   - 使用番茄工作法，25分钟专注+5分钟休息

3. 🎯 目标设定
   - 设定SMART目标（具体、可测量、可达成、相关、有时限）
   - 每周回顾和调整目标
   - 庆祝小成就，保持动力

4. 🚫 减少干扰
   - 关闭社交媒体通知
   - 使用"勿扰模式"
   - 设定"深度工作"时间段

5. 📈 持续改进
   - 每周五回顾本周工作
   - 记录效率提升的方法
   - 学习新的时间管理技巧"""
        
        elif context.task_type == "schedule_assistant":
            return f"""基于你的时间安排，我建议：

1. 📅 时间规划
   - 下午3点的会议：提前15分钟准备，确保准时参加
   - 晚上8点打球：合理安排会议结束后的时间
   - 建议会议控制在1小时内，避免影响后续安排

2. ⏱️ 时间分配
   - 会议前准备时间：14:30-15:00（30分钟）
   - 会议时间：15:00-16:00（1小时）
   - 会议后整理：16:00-16:30（30分钟）
   - 休息和准备：16:30-17:30（1小时）
   - 晚餐时间：17:30-18:30（1小时）
   - 前往球场：18:30-19:00（30分钟）
   - 热身时间：19:00-20:00（1小时）

3. 💡 优化建议
   - 如果会议可能超时，提前告知朋友调整打球时间
   - 准备会议材料，提高会议效率
   - 考虑带运动装备到公司，节省回家换装时间

4. 🚨 注意事项
   - 会议前确认议程和时间安排
   - 准备会议记录工具
   - 设定会议结束提醒
   - 预留缓冲时间应对意外情况"""
        
        else:
            return f"""我理解你的需求：{context.user_input}

作为你的智能助手，我建议：
1. 明确你的具体目标
2. 分析当前的情况和限制
3. 制定可执行的行动计划
4. 定期评估和调整策略

如果你有具体的问题或需求，请告诉我，我会为你提供更详细的建议！"""

    def _generate_json_prompt(self, context: PromptContext) -> str:
        """生成JSON格式的结构化Prompt"""
        import json
        
        if context.task_type == "health_advice":
            json_prompt = {
                "role": "health_advisor",
                "user_context": {
                    "age": context.user_profile.get("age", "未知"),
                    "occupation": context.user_profile.get("occupation", "未知"),
                    "health_goals": context.current_goals,
                    "mood_state": context.mood_state,
                    "available_time": context.available_time
                },
                "task_description": "为用户提供个性化的睡眠改善建议",
                "required_outputs": [
                    {
                        "type": "sleep_improvement_tips",
                        "description": "具体的睡眠改善建议",
                        "format": "numbered_list",
                        "count": "5-7条"
                    },
                    {
                        "type": "stress_management",
                        "description": "工作压力管理方法",
                        "format": "actionable_steps",
                        "count": "3-5条"
                    },
                    {
                        "type": "relaxation_techniques",
                        "description": "睡前放松技巧",
                        "format": "detailed_instructions",
                        "count": "3-4种"
                    },
                    {
                        "type": "action_plan",
                        "description": "可执行的行动计划",
                        "format": "timeline_based",
                        "timeframe": "1-2周"
                    },
                    {
                        "type": "progress_tracking",
                        "description": "进度跟踪方法",
                        "format": "metrics_and_tools",
                        "tools": ["app", "journal", "checklist"]
                    }
                ],
                "constraints": [
                    "考虑用户的工作压力和时间限制",
                    "提供具体可操作的建议",
                    "包含时间安排和频率建议",
                    "考虑用户的实际情况和偏好"
                ],
                "output_format": {
                    "structure": "organized_sections",
                    "language": "professional_but_friendly",
                    "include_emojis": True,
                    "include_examples": True
                }
            }
        
        elif context.task_type == "work_assistant":
            json_prompt = {
                "role": "productivity_consultant",
                "user_context": {
                    "age": context.user_profile.get("age", "未知"),
                    "occupation": context.user_profile.get("occupation", "未知"),
                    "work_style": context.user_profile.get("work_style", "未知"),
                    "current_projects": context.user_profile.get("current_projects", []),
                    "stress_level": context.user_profile.get("stress_level", "未知")
                },
                "task_description": "帮助用户提高工作效率和生产力",
                "required_outputs": [
                    {
                        "type": "efficiency_strategies",
                        "description": "针对性的效率提升策略",
                        "format": "prioritized_list",
                        "priority_levels": ["high", "medium", "low"]
                    },
                    {
                        "type": "time_management",
                        "description": "时间管理技巧",
                        "format": "practical_tips",
                        "count": "5-7条"
                    },
                    {
                        "type": "stress_relief",
                        "description": "压力缓解方法",
                        "format": "quick_actions",
                        "time_required": "5-15分钟"
                    },
                    {
                        "type": "project_management",
                        "description": "项目进度管理建议",
                        "format": "framework_based",
                        "tools": ["kanban", "timeline", "checklist"]
                    },
                    {
                        "type": "improvement_plan",
                        "description": "可执行的改进计划",
                        "format": "weekly_milestones",
                        "duration": "4-6周"
                    }
                ],
                "constraints": [
                    "结合用户的工作风格和当前压力状况",
                    "提供切实可行的建议",
                    "考虑项目deadline和优先级",
                    "平衡效率和压力管理"
                ],
                "output_format": {
                    "structure": "problem_solution_framework",
                    "language": "professional_and_encouraging",
                    "include_emojis": True,
                    "include_timeline": True
                }
            }
        
        elif context.task_type == "schedule_assistant":
            json_prompt = {
                "role": "time_management_specialist",
                "user_context": {
                    "user_input": context.user_input,
                    "available_time": context.available_time,
                    "current_goals": context.current_goals
                },
                "task_description": "帮助用户合理安排时间和日程",
                "required_outputs": [
                    {
                        "type": "time_planning",
                        "description": "时间规划建议",
                        "format": "timeline_based",
                        "include_buffer_time": True
                    },
                    {
                        "type": "time_allocation",
                        "description": "时间分配方案",
                        "format": "detailed_schedule",
                        "precision": "30分钟"
                    },
                    {
                        "type": "optimization_tips",
                        "description": "时间优化建议",
                        "format": "actionable_tips",
                        "count": "3-5条"
                    },
                    {
                        "type": "conflict_resolution",
                        "description": "时间冲突解决方案",
                        "format": "if_then_scenarios",
                        "include_alternatives": True
                    },
                    {
                        "type": "preparation_checklist",
                        "description": "准备事项清单",
                        "format": "checklist",
                        "categories": ["materials", "time", "location"]
                    }
                ],
                "constraints": [
                    "考虑用户的具体时间安排",
                    "预留足够的缓冲时间",
                    "提供备选方案",
                    "确保建议的可行性"
                ],
                "output_format": {
                    "structure": "chronological_order",
                    "language": "clear_and_concise",
                    "include_emojis": True,
                    "include_time_estimates": True
                }
            }
        
        else:
            json_prompt = {
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
                        "tone": "helpful_and_encouraging"
                    }
                ],
                "constraints": [
                    "保持友好和专业的语调",
                    "提供有用的建议",
                    "鼓励用户进一步说明需求"
                ],
                "output_format": {
                    "structure": "simple_and_clear",
                    "language": "friendly_and_professional",
                    "include_emojis": True,
                    "include_next_steps": True
                }
            }
        
        return json.dumps(json_prompt, ensure_ascii=False, indent=2)
    
    def demo_prompt_optimization(self):
        """演示Prompt优化功能"""
        print("\n🔄 Prompt优化功能演示")
        print("=" * 60)
        
        # 模拟原始Prompt
        original_prompt = """你是一个健康顾问，请帮助用户改善睡眠。"""
        
        print(f"原始Prompt：{original_prompt}")
        
        # 模拟用户反馈
        user_feedback = "这个建议太笼统了，我需要更具体的行动步骤"
        
        print(f"用户反馈：{user_feedback}")
        
        # 模拟优化后的Prompt
        optimized_prompt = """你是一个专业的健康顾问，专门帮助用户改善睡眠质量。

请基于用户的健康状况、工作压力、生活习惯等信息，提供：

1. 具体的睡前放松技巧（如呼吸练习、冥想方法）
2. 详细的睡眠环境优化建议（温度、光线、噪音控制）
3. 可执行的睡前仪式（具体的时间安排和活动）
4. 压力管理方法（工作压力、情绪调节技巧）
5. 进度跟踪表格（睡眠质量记录、改善效果评估）

要求：
- 每个建议都要具体可操作
- 提供时间安排和频率建议
- 包含成功案例和预期效果
- 考虑用户的实际情况和限制

请以结构化的方式组织回答，确保用户能够立即开始执行。"""
        
        print(f"\n优化后的Prompt：")
        print(optimized_prompt)
        
        print(f"\n✅ 优化效果：")
        print("- 增加了具体的行动步骤")
        print("- 提供了详细的操作指南")
        print("- 包含了进度跟踪方法")
        print("- 考虑了用户的实际限制")
    
    def demo_prompt_management(self):
        """演示Prompt管理功能"""
        print("\n📊 Prompt管理功能演示")
        print("=" * 60)
        
        # 模拟存储一些Prompt
        mock_prompts = [
            GeneratedPrompt(
                prompt_text="健康顾问Prompt 1",
                confidence_score=0.85,
                reasoning="基于用户健康需求生成",
                optimization_suggestions=["增加具体步骤"],
                created_at=datetime.now(),
                context_used={"task_type": "health_advice", "user_input": "改善睡眠"}
            ),
            GeneratedPrompt(
                prompt_text="工作助手Prompt 1",
                confidence_score=0.78,
                reasoning="针对工作效率问题",
                optimization_suggestions=["优化时间管理建议"],
                created_at=datetime.now(),
                context_used={"task_type": "work_assistant", "user_input": "提高效率"}
            ),
            GeneratedPrompt(
                prompt_text="学习教练Prompt 1",
                confidence_score=0.92,
                reasoning="个性化学习计划",
                optimization_suggestions=["增加实践项目"],
                created_at=datetime.now(),
                context_used={"task_type": "learning_coach", "user_input": "学习Python"}
            )
        ]
        
        # 存储Prompt
        for prompt in mock_prompts:
            self.prompt_manager.store_prompt(prompt)
        
        # 获取性能统计
        stats = self.prompt_manager.get_performance_stats()
        
        print(f"📈 性能统计：")
        print(f"总Prompt数量：{stats['total_prompts']}")
        print(f"平均置信度：{stats['avg_confidence']:.2f}")
        print(f"最近7天Prompt：{stats['recent_prompts']}")
        
        print(f"\n📊 按任务类型统计：")
        for task_type, avg_score in stats['task_type_stats'].items():
            print(f"  {task_type}: {avg_score:.2f}")
    
    def interactive_demo(self):
        """交互式演示"""
        print("\n🎮 交互式演示模式")
        print("=" * 60)
        print("💡 输入 'quit' 退出，输入 'help' 查看帮助")
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                if user_input.lower() in ['help', '帮助']:
                    print_help()
                    continue
                
                if not user_input:
                    continue
                
                # 分析用户输入并生成相应的Prompt
                task_type = self._classify_task(user_input)
                print(f"🎯 识别任务类型: {task_type}")
                
                # 生成模拟Prompt
                mock_context = PromptContext(
                    task_type=task_type,
                    user_input=user_input,
                    conversation_history=[],
                    user_profile={"age": 30, "occupation": "用户"},
                    current_goals=["提升效率"],
                    mood_state="正常"
                )
                
                mock_prompt = self._generate_mock_prompt(mock_context)
                print(f"\n🤖 生成的Prompt:")
                print(mock_prompt)
                
                # 生成实际建议
                print(f"\n💡 基于Prompt生成的建议:")
                actual_advice = self._generate_actual_advice(mock_context, mock_prompt)
                print(actual_advice)
                
            except KeyboardInterrupt:
                print("\n👋 程序被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 处理过程中出现错误: {e}")
    
    def _classify_task(self, user_input: str) -> str:
        """分类用户输入的任务类型"""
        input_lower = user_input.lower()
        
        # 健康相关关键词
        health_keywords = ["健康", "睡眠", "运动", "饮食", "压力", "疲劳", "精力", "身体"]
        if any(keyword in input_lower for keyword in health_keywords):
            return "health_advice"
        
        # 工作相关关键词
        work_keywords = ["工作", "效率", "项目", "任务", "时间", "管理", "压力", "加班"]
        if any(keyword in input_lower for keyword in work_keywords):
            return "work_assistant"
        
        # 学习相关关键词
        learning_keywords = ["学习", "技能", "课程", "计划", "提升", "知识", "编程", "语言"]
        if any(keyword in input_lower for keyword in learning_keywords):
            return "learning_coach"
        
        # 时间安排相关关键词
        schedule_keywords = ["会议", "打球", "约会", "安排", "时间", "日程", "计划", "明天", "下午", "晚上"]
        if any(keyword in input_lower for keyword in schedule_keywords):
            return "schedule_assistant"
        
        return "conversation"
    
    def run(self):
        """运行主程序（支持结构化输出）"""
        output_mode = os.getenv("AIPS_OUTPUT", "text").lower()
        if output_mode == "text":
            print("🎯 AI Prompt生成器系统")
            print("=" * 80)
            print(self.config.get_config_summary())
        else:
            # 结构化输出配置摘要
            config_summary = self.config.get_config_summary().splitlines()
            print(json.dumps({"type": "config", "lines": config_summary}, ensure_ascii=False))

        # 1. 基础功能演示
        self.demo_basic_functionality(output_mode=output_mode)

        # 2. 两段式链路演示（设计 → 执行）
        orch = PromptOrchestrator()
        octx = OrchestratorContext(
            task_type="schedule_assistant",
            user_input="我明天下午三点可能有个会议,然后晚上8点和朋友约好了去打球",
            conversation_history=[],
            user_profile={"age": 30, "occupation": "产品经理"},
            current_goals=["合理安排时间"],
            mood_state="正常",
            available_time="明天全天",
            location="办公室和球场",
        )
        design = orch.design_prompt(octx)
        execute = orch.execute_prompt(design.get("data", {})) if design.get("success") else {"success": False, "error": design.get("error")}
        if output_mode == "json":
            print(json.dumps({"type": "orchestrator_design", **design}, ensure_ascii=False))
            print(json.dumps({"type": "orchestrator_execute", **execute}, ensure_ascii=False))
        else:
            print("\n🧩 两段式链路演示（设计 → 执行）")
            print("-" * 60)
            print("[设计] 结构化 JSON Prompt 预览：")
            print(json.dumps(design.get("data", {}), ensure_ascii=False, indent=2))
            print("\n[执行] 最终回复：")
            print(execute.get("data", {}).get("final_text", "(无)"))

        # 2.1 多意图 → 多任务 → 多设计/执行（聚合输出）
        multi_in = "明天下午开会，之后去接孩子放学，晚上打球"
        multi_ctx = OrchestratorContext(
            task_type="conversation",
            user_input=multi_in,
            conversation_history=[],
            user_profile={"age": 35, "occupation": "工程师"},
            current_goals=["安排一天行程"],
            mood_state="正常",
        )
        multi_res = orch.generate_and_respond_multi(multi_in, multi_ctx)
        if output_mode == "json":
            print(json.dumps({"type": "orchestrator_multi", **multi_res}, ensure_ascii=False))
        else:
            print("\n🧩 多任务链路演示（多意图 → 多设计/执行）")
            print("-" * 60)
            print("[聚合结果]\n")
            print(multi_res.get("data", {}).get("final", {}).get("summary", "(无)"))

        # 3. Prompt优化演示（结构化包装简单输出）
        if output_mode == "text":
            self.demo_prompt_optimization()
        else:
            print(json.dumps({"type": "demo_opt", "success": True, "meta": {"note": "see text mode for details"}}, ensure_ascii=False))

        # 4. Prompt管理演示（返回结构化统计）
        if output_mode == "text":
            self.demo_prompt_management()
        else:
            stats = self.prompt_manager.get_performance_stats_structured()
            print(json.dumps({"type": "manager_stats", **stats}, ensure_ascii=False))

        # 5. 交互式演示
        if output_mode == "text":
            self.interactive_demo()

def print_help():
    """显示帮助信息"""
    print("\n📖 AI Prompt生成器系统帮助")
    print("=" * 30)
    print("🎯 核心功能:")
    print("  • 自动生成个性化Prompt")
    print("  • 基于用户反馈优化Prompt")
    print("  • Prompt质量评估")
    print("  • Prompt历史管理")
    print("  • 性能统计分析")
    print("\n💡 使用说明:")
    print("  • 直接输入您的问题或需求")
    print("  • 系统会自动识别任务类型")
    print("  • 生成相应的个性化Prompt")
    print("  • 提供具体的可执行建议")
    print("  • 输入 'quit' 退出程序")

if __name__ == "__main__":
    # 修复导入问题
    from datetime import datetime
    
    system = AIPromptSystem()
    system.run()
