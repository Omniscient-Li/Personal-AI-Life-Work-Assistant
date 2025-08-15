#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt生成器测试文件
演示如何使用AI自动生成和优化Prompt
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_prompt_generator import (
    AIPromptGenerator, 
    PromptContext, 
    GeneratedPrompt, 
    PromptManager
)

def create_mock_context() -> PromptContext:
    """创建模拟的上下文数据"""
    return PromptContext(
        task_type="health_advice",
        user_input="我想提高睡眠质量，最近总是失眠",
        conversation_history=[
            {
                "user_input": "最近工作压力很大，经常加班",
                "assistant_response": "我理解你的感受，工作压力确实会影响生活质量。"
            },
            {
                "user_input": "晚上总是睡不着，白天精神不好",
                "assistant_response": "睡眠问题确实很常见，我们可以一起找到解决方案。"
            }
        ],
        user_profile={
            "age": 28,
            "occupation": "软件工程师",
            "health_goals": ["改善睡眠", "减少压力", "提高精力"],
            "work_schedule": "9:00-18:00，经常加班",
            "exercise_frequency": "每周2-3次",
            "sleep_time": "23:00-07:00"
        },
        current_goals=["改善睡眠质量", "提高工作效率", "平衡工作生活"],
        mood_state="压力较大，有些焦虑",
        available_time="晚上9点后",
        location="家里",
        weather="阴天"
    )

def create_work_context() -> PromptContext:
    """创建工作助手场景的上下文"""
    return PromptContext(
        task_type="work_assistant",
        user_input="我想提高工作效率，感觉最近效率很低",
        conversation_history=[
            {
                "user_input": "项目deadline很紧，感觉很焦虑",
                "assistant_response": "我理解你的压力，让我们一起来分析如何提高效率。"
            }
        ],
        user_profile={
            "age": 30,
            "occupation": "产品经理",
            "work_style": "喜欢深度思考，但容易拖延",
            "current_projects": ["新功能开发", "用户调研", "竞品分析"],
            "stress_level": "高",
            "productivity_patterns": ["上午效率高", "下午容易分心"]
        },
        current_goals=["提高工作效率", "减少拖延", "按时完成项目"],
        mood_state="焦虑，有些疲惫",
        available_time="工作时间",
        location="办公室",
        weather="晴天"
    )

def create_learning_context() -> PromptContext:
    """创建学习教练场景的上下文"""
    return PromptContext(
        task_type="learning_coach",
        user_input="我想学习Python编程，但不知道从哪里开始",
        conversation_history=[
            {
                "user_input": "我对编程很感兴趣，但基础很差",
                "assistant_response": "每个人都是从基础开始的，让我帮你制定学习计划。"
            }
        ],
        user_profile={
            "age": 25,
            "occupation": "市场营销",
            "learning_style": "视觉学习者，喜欢动手实践",
            "available_time": "每天2小时",
            "current_skills": ["Excel", "基础数据分析"],
            "learning_goals": ["掌握Python基础", "能够进行数据分析", "提升职业竞争力"]
        },
        current_goals=["学习Python编程", "提升数据分析能力", "转行到技术岗位"],
        mood_state="兴奋，有些紧张",
        available_time="晚上7-9点",
        location="家里",
        weather="多云"
    )

def demo_prompt_generation_without_api(output_mode: str = "text"):
    """演示Prompt生成功能（不需要真实API），支持结构化输出"""
    if output_mode == "text":
        print("🚀 AI Prompt生成器演示")
        print("=" * 60)
    
    contexts = [
        ("健康建议", create_mock_context()),
        ("工作助手", create_work_context()),
        ("学习教练", create_learning_context())
    ]
    
    for scenario_name, context in contexts:
        mock_prompt = generate_mock_prompt(context)
        payload = {
            "scenario": scenario_name,
            "context": {
                "task_type": context.task_type,
                "user_input": context.user_input,
                "current_goals": context.current_goals,
                "mood_state": context.mood_state,
                "available_time": context.available_time
            },
            "result": {
                "prompt_text": mock_prompt,
                "confidence_score": 0.85,
                "suggestions": [
                    "可以增加更多具体的行动步骤",
                    "考虑添加时间管理建议",
                    "建议包含进度跟踪方法"
                ]
            }
        }
        if output_mode == "json":
            import json as _json
            print(_json.dumps({"type": "demo_prompt", **payload}, ensure_ascii=False))
        else:
            print(f"\n📋 场景：{scenario_name}")
            print("-" * 40)
            print(f"任务类型：{context.task_type}")
            print(f"用户输入：{context.user_input}")
            print(f"用户目标：{', '.join(context.current_goals)}")
            print(f"心情状态：{context.mood_state}")
            print(f"可用时间：{context.available_time}")
            print(f"\n🤖 生成的Prompt：\n{mock_prompt}")
            print("\n💡 优化建议：")
            for s in payload["result"]["suggestions"]:
                print(f"- {s}")

def generate_mock_prompt(context: PromptContext) -> str:
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
    
    elif context.task_type == "learning_coach":
        return f"""你是一个专业的学习教练，专门帮助{context.user_profile.get('occupation', '学习者')}制定学习计划。

基于用户信息：
- 学习风格：{context.user_profile.get('learning_style', '标准学习风格')}
- 可用时间：{context.user_profile.get('available_time', '灵活时间')}
- 当前技能：{', '.join(context.user_profile.get('current_skills', ['基础技能']))}
- 学习目标：{', '.join(context.user_profile.get('learning_goals', ['提升技能']))}

请提供：
1. 个性化的学习路径规划
2. 每日学习计划
3. 实践项目建议
4. 学习资源推荐
5. 进度评估方法

注意：考虑用户的学习风格和可用时间，制定循序渐进的学习计划。"""
    
    else:
        return "你是一个智能助手，请根据用户需求提供帮助。"

def demo_prompt_optimization():
    """演示Prompt优化功能"""
    print("\n🔄 Prompt优化演示")
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

def demo_prompt_management():
    """演示Prompt管理功能"""
    print("\n📊 Prompt管理演示")
    print("=" * 60)
    
    # 创建Prompt管理器
    manager = PromptManager()
    
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
        manager.store_prompt(prompt)
    
    # 获取性能统计
    stats = manager.get_performance_stats()
    
    print(f"📈 性能统计：")
    print(f"总Prompt数量：{stats['total_prompts']}")
    print(f"平均置信度：{stats['avg_confidence']:.2f}")
    print(f"最近7天Prompt：{stats['recent_prompts']}")
    
    print(f"\n📊 按任务类型统计：")
    for task_type, avg_score in stats['task_type_stats'].items():
        print(f"  {task_type}: {avg_score:.2f}")

def main():
    """主函数"""
    print("🎯 AI Prompt生成器完整演示")
    print("=" * 80)
    
    # 1. 演示Prompt生成
    demo_prompt_generation_without_api()
    
    # 2. 演示Prompt优化
    demo_prompt_optimization()
    
    # 3. 演示Prompt管理
    demo_prompt_management()
    
    print("\n🎉 演示完成！")
    print("\n💡 要使用真实功能，请：")
    print("1. 设置OpenAI API密钥")
    print("2. 创建AIPromptGenerator实例")
    print("3. 调用generate_prompt()方法")
    print("4. 集成到现有的对话系统中")

if __name__ == "__main__":
    main()
