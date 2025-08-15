#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt生成器集成示例
展示如何将AI Prompt生成器集成到现有的对话系统中
"""

import os
import sys
from typing import Dict, Any, Optional, List
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_prompt_generator import (
    AIPromptGenerator, 
    PromptContext, 
    GeneratedPrompt, 
    PromptManager
)

class EnhancedConversationEngine:
    """增强版对话引擎，集成AI Prompt生成器"""
    
    def __init__(self, api_key: str = None):
        self.prompt_generator = None
        self.prompt_manager = PromptManager()
        
        # 如果提供了API密钥，初始化AI Prompt生成器
        if api_key:
            try:
                self.prompt_generator = AIPromptGenerator(api_key)
                print("✅ AI Prompt生成器初始化成功")
            except Exception as e:
                print(f"⚠️ AI Prompt生成器初始化失败: {e}")
                print("将使用传统Prompt模板")
        else:
            print("ℹ️ 未提供API密钥，将使用传统Prompt模板")
        
        # 传统Prompt模板（作为备用）
        self.traditional_prompts = {
            "health_advice": "你是一个健康顾问，请基于用户需求提供健康建议。",
            "work_assistant": "你是一个工作助手，请帮助用户提高工作效率。",
            "learning_coach": "你是一个学习教练，请帮助用户制定学习计划。",
            "life_planner": "你是一个生活规划师，请帮助用户平衡工作和生活。",
            "conversation": "你是一个智能助手，请根据用户需求提供帮助。"
        }
    
    def generate_response(self, user_input: str, context_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成对话响应，优先使用AI生成的Prompt"""
        
        # 1. 确定任务类型
        task_type = self._classify_task(user_input, context_info)
        
        # 2. 构建Prompt上下文
        prompt_context = self._build_prompt_context(user_input, task_type, context_info)
        
        # 3. 尝试使用AI生成Prompt
        if self.prompt_generator:
            try:
                # 使用结构化接口，兼容旧接口
                structured = self.prompt_generator.generate_prompt_structured(prompt_context)
                if structured.get("success") and structured.get("data"):
                    generated_prompt_text = structured["data"].get("prompt_text", "")
                    generated_confidence = structured["data"].get("confidence_score", 0.0)
                else:
                    # 回退：使用旧接口
                    gp = self.prompt_generator.generate_prompt(prompt_context)
                    generated_prompt_text = gp.prompt_text
                    generated_confidence = gp.confidence_score
                
                # 存储生成的Prompt
                # 仅在有数据类时可存储；结构化模式下可跳过或构造
                
                
                # 如果置信度足够高，使用AI生成的Prompt
                if generated_confidence > 0.7:
                    final_prompt = generated_prompt_text
                    prompt_source = "AI生成"
                    confidence = generated_confidence
                else:
                    # 置信度不够高，使用传统模板
                    final_prompt = self._enhance_traditional_prompt(
                        self.traditional_prompts.get(task_type, self.traditional_prompts["conversation"]),
                        context_info
                    )
                    prompt_source = "传统模板增强"
                    confidence = 0.6
                    
            except Exception as e:
                print(f"⚠️ AI Prompt生成失败: {e}")
                # 使用传统模板
                final_prompt = self._enhance_traditional_prompt(
                    self.traditional_prompts.get(task_type, self.traditional_prompts["conversation"]),
                    context_info
                )
                prompt_source = "传统模板增强"
                confidence = 0.6
        else:
            # 没有AI生成器，使用传统模板
            final_prompt = self._enhance_traditional_prompt(
                self.traditional_prompts.get(task_type, self.traditional_prompts["conversation"]),
                context_info
            )
            prompt_source = "传统模板增强"
            confidence = 0.6
        
        # 4. 生成响应（这里模拟，实际需要调用AI）
        response = self._generate_ai_response(final_prompt, user_input, context_info)
        
        # 5. 返回结果
        return {
            "response": response,
            "prompt_used": final_prompt,
            "prompt_source": prompt_source,
            "confidence": confidence,
            "task_type": task_type,
            "suggestions": self._generate_follow_up_suggestions(task_type, context_info)
        }

    def generate_response_structured(self, user_input: str, context_info: Dict[str, Any]) -> Dict[str, Any]:
        """结构化封装结果"""
        try:
            data = self.generate_response(user_input, context_info)
            return {"success": True, "data": data, "error": None, "meta": {"engine": "EnhancedConversationEngine"}}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e), "meta": {"engine": "EnhancedConversationEngine"}}
    
    def _classify_task(self, user_input: str, context_info: Dict[str, Any]) -> str:
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
        
        # 生活规划相关关键词
        life_keywords = ["生活", "平衡", "规划", "目标", "习惯", "时间", "家庭", "休闲"]
        if any(keyword in input_lower for keyword in life_keywords):
            return "life_planner"
        
        return "conversation"
    
    def _build_prompt_context(self, user_input: str, task_type: str, context_info: Dict[str, Any]) -> PromptContext:
        """构建Prompt上下文"""
        return PromptContext(
            task_type=task_type,
            user_input=user_input,
            conversation_history=context_info.get("conversation_history", []),
            user_profile=context_info.get("user_profile", {}),
            current_goals=context_info.get("current_goals", []),
            mood_state=context_info.get("mood_state", "正常"),
            available_time=context_info.get("available_time"),
            location=context_info.get("location"),
            weather=context_info.get("weather")
        )
    
    def _enhance_traditional_prompt(self, base_prompt: str, context_info: Dict[str, Any]) -> str:
        """增强传统Prompt模板"""
        enhanced_prompt = f"{base_prompt}\n\n"
        
        # 添加用户背景信息
        if context_info.get("user_profile"):
            profile = context_info["user_profile"]
            enhanced_prompt += f"用户背景：{profile.get('age', '未知年龄')}岁，{profile.get('occupation', '职场人士')}\n"
        
        # 添加当前目标
        if context_info.get("current_goals"):
            goals = context_info["current_goals"]
            enhanced_prompt += f"当前目标：{', '.join(goals)}\n"
        
        # 添加心情状态
        if context_info.get("mood_state"):
            enhanced_prompt += f"心情状态：{context_info['mood_state']}\n"
        
        enhanced_prompt += "\n请基于以上信息，为用户提供个性化的帮助和建议。"
        
        return enhanced_prompt
    
    def _generate_ai_response(self, prompt: str, user_input: str, context_info: Dict[str, Any]) -> str:
        """生成AI响应（这里模拟，实际需要调用AI）"""
        # 模拟AI响应生成
        if "健康" in prompt or "睡眠" in prompt:
            return f"基于你的情况，我建议：\n1. 建立规律的作息时间\n2. 睡前1小时避免使用电子设备\n3. 尝试冥想或深呼吸练习\n4. 保持适度的运动\n5. 注意饮食调节"
        elif "工作" in prompt or "效率" in prompt:
            return f"针对你的工作效率问题，建议：\n1. 使用番茄工作法\n2. 优先处理重要且紧急的任务\n3. 减少干扰，专注工作\n4. 定期休息，保持精力\n5. 建立工作流程和模板"
        elif "学习" in prompt or "技能" in prompt:
            return f"关于你的学习目标，建议：\n1. 制定具体的学习计划\n2. 每天保持固定的学习时间\n3. 理论与实践相结合\n4. 找到学习伙伴或导师\n5. 定期评估学习进度"
        else:
            return f"我理解你的需求：{user_input}\n让我为你提供一些建议和帮助。"
    
    def _generate_follow_up_suggestions(self, task_type: str, context_info: Dict[str, Any]) -> List[str]:
        """生成后续建议"""
        suggestions_map = {
            "health_advice": [
                "是否需要制定具体的健康计划？",
                "想要了解更多关于压力管理的方法吗？",
                "需要我帮你跟踪健康数据吗？"
            ],
            "work_assistant": [
                "需要我帮你制定详细的工作计划吗？",
                "想要了解更多时间管理技巧？",
                "需要我帮你分析工作效率瓶颈吗？"
            ],
            "learning_coach": [
                "需要我帮你制定详细的学习计划吗？",
                "想要了解更多学习方法？",
                "需要我帮你找到合适的学习资源吗？"
            ],
            "life_planner": [
                "需要我帮你制定生活规划吗？",
                "想要了解更多平衡工作生活的方法？",
                "需要我帮你建立良好的习惯吗？"
            ],
            "conversation": [
                "还有其他需要帮助的吗？",
                "想要了解更多相关信息？",
                "需要我为你提供其他建议吗？"
            ]
        }
        
        return suggestions_map.get(task_type, ["还有其他需要帮助的吗？"])
    
    def optimize_prompt_based_on_feedback(self, user_feedback: str, context_info: Dict[str, Any]) -> Optional[GeneratedPrompt]:
        """基于用户反馈优化Prompt"""
        if not self.prompt_generator:
            print("⚠️ 没有AI Prompt生成器，无法优化Prompt")
            return None
        
        try:
            # 获取最近的Prompt
            recent_prompts = self.prompt_manager.prompt_history[-5:] if self.prompt_manager.prompt_history else []
            
            if not recent_prompts:
                print("⚠️ 没有可优化的Prompt")
                return None
            
            # 使用最新的Prompt进行优化
            latest_prompt = recent_prompts[-1]
            
            # 构建优化上下文
            optimization_context = self._build_prompt_context(
                latest_prompt.context_used.get("user_input", ""),
                latest_prompt.context_used.get("task_type", "conversation"),
                context_info
            )
            
            # 优化Prompt
            optimized_prompt = self.prompt_generator.optimize_prompt(
                latest_prompt.prompt_text,
                user_feedback,
                optimization_context
            )
            
            # 存储优化后的Prompt
            self.prompt_manager.store_prompt(optimized_prompt)
            
            print(f"✅ Prompt优化成功 (新置信度: {optimized_prompt.confidence_score:.2f})")
            return optimized_prompt
            
        except Exception as e:
            print(f"❌ Prompt优化失败: {e}")
            return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        prompt_stats = self.prompt_manager.get_performance_stats()
        
        return {
            "prompt_generator_available": self.prompt_generator is not None,
            "prompt_stats": prompt_stats,
            "traditional_prompts_count": len(self.traditional_prompts),
            "system_status": "运行正常" if self.prompt_generator else "使用传统模式"
        }

def demo_integration():
    """演示集成功能（支持 JSON 输出）"""
    output_mode = os.getenv("AIPS_OUTPUT", "text").lower()
    if output_mode == "text":
        print("🔗 AI Prompt生成器集成演示")
        print("=" * 60)
    
    # 创建增强版对话引擎（不提供API密钥，使用传统模式）
    engine = EnhancedConversationEngine()
    
    # 模拟用户输入和上下文
    test_cases = [
        {
            "user_input": "我想提高睡眠质量，最近总是失眠",
            "context_info": {
                "user_profile": {"age": 28, "occupation": "软件工程师"},
                "current_goals": ["改善睡眠", "减少压力"],
                "mood_state": "压力较大",
                "conversation_history": []
            }
        },
        {
            "user_input": "我想提高工作效率，感觉最近效率很低",
            "context_info": {
                "user_profile": {"age": 30, "occupation": "产品经理"},
                "current_goals": ["提高效率", "按时完成项目"],
                "mood_state": "焦虑",
                "conversation_history": []
            }
        },
        {
            "user_input": "我想学习Python编程",
            "context_info": {
                "user_profile": {"age": 25, "occupation": "市场营销"},
                "current_goals": ["学习编程", "提升技能"],
                "mood_state": "兴奋",
                "conversation_history": []
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        if output_mode == "text":
            print(f"\n📝 测试案例 {i}: {test_case['user_input']}")
            print("-" * 50)
        structured = engine.generate_response_structured(test_case["user_input"], test_case["context_info"])
        if output_mode == "json":
            print(json.dumps({"type": "integration_case", "index": i, **structured}, ensure_ascii=False))
        else:
            result = structured.get("data", {})
            print(f"任务类型: {result.get('task_type')}")
            print(f"Prompt来源: {result.get('prompt_source')}")
            print(f"置信度: {result.get('confidence'):.2f}")
            print(f"响应: {result.get('response','')[:100]}...")
            print(f"后续建议: {', '.join(result.get('suggestions', []))}")
    
    # 获取系统统计
    stats = engine.get_system_stats()
    if os.getenv("AIPS_OUTPUT", "text").lower() == "json":
        print(json.dumps({"type": "integration_stats", "success": True, "data": stats, "error": None}, ensure_ascii=False))
    else:
        print(f"\n📊 系统统计")
        print("-" * 50)
        print(f"AI Prompt生成器: {'可用' if stats['prompt_generator_available'] else '不可用'}")
        print(f"系统状态: {stats['system_status']}")
        print(f"传统Prompt数量: {stats['traditional_prompts_count']}")
        if stats['prompt_stats']['total_prompts'] > 0:
            print(f"Prompt统计: {stats['prompt_stats']}")

def demo_with_api_key():
    """演示使用API密钥的完整功能"""
    print("\n🔑 完整功能演示（需要API密钥）")
    print("=" * 60)
    
    print("要使用完整功能，请：")
    print("1. 设置OpenAI API密钥")
    print("2. 创建EnhancedConversationEngine实例")
    print("3. 享受AI生成的个性化Prompt")
    
    # 模拟代码示例
    example_code = '''
# 使用API密钥创建增强版对话引擎
api_key = "your-openai-api-key-here"
engine = EnhancedConversationEngine(api_key)

# 生成响应
result = engine.generate_response(
    "我想提高睡眠质量",
    {
        "user_profile": {"age": 28, "occupation": "程序员"},
        "current_goals": ["改善睡眠", "减少压力"],
        "mood_state": "压力较大"
    }
)

print(f"AI生成的Prompt: {result['prompt_used']}")
print(f"响应: {result['response']}")
'''
    
    print("\n代码示例：")
    print(example_code)

if __name__ == "__main__":
    # 演示集成功能
    demo_integration()
    
    # 演示完整功能
    demo_with_api_key()
    
    print("\n🎉 集成演示完成！")
    print("\n💡 下一步：")
    print("1. 获取OpenAI API密钥")
    print("2. 测试AI Prompt生成功能")
    print("3. 集成到现有的对话系统中")
    print("4. 收集用户反馈并优化Prompt")
