#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt生成器系统
让AI自动生成和优化Prompt，减少手动编写代码的需求
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import openai

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PromptContext:
    """Prompt上下文信息"""
    task_type: str
    user_input: str
    conversation_history: List[Dict]
    user_profile: Dict[str, Any]
    current_goals: List[str]
    mood_state: str
    available_time: Optional[str] = None
    location: Optional[str] = None
    weather: Optional[str] = None

@dataclass
class GeneratedPrompt:
    """生成的Prompt信息"""
    prompt_text: str
    confidence_score: float
    reasoning: str
    optimization_suggestions: List[str]
    created_at: datetime
    context_used: Dict[str, Any]

class AIPromptGenerator:
    """AI Prompt生成器核心类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        # 允许从环境变量读取，未提供则进入 mock 模式
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        self.model = model
        self.openai_client = None
        try:
            if self.api_key:
                self.openai_client = openai.OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI 客户端已初始化")
            else:
                logger.info("ℹ️ 未检测到 API Key，使用 mock 模式")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI 客户端初始化失败，将使用 mock 模式: {e}")
            self.openai_client = None
        
        # 基础Prompt模板
        self.base_templates = {
            "conversation": "你是一个智能助手，能够理解用户需求并提供帮助。",
            "health_advice": "你是一个健康顾问，基于用户的健康数据提供个性化建议。",
            "work_assistant": "你是一个工作助手，帮助用户提高工作效率和生产力。",
            "learning_coach": "你是一个学习教练，帮助用户制定学习计划和提升技能。",
            "life_planner": "你是一个生活规划师，帮助用户平衡工作和生活。"
        }
        
        # Prompt质量评估标准
        self.quality_criteria = [
            "清晰度：Prompt是否清晰明确",
            "相关性：是否与用户需求高度相关",
            "个性化：是否体现用户特点",
            "可执行性：AI是否能基于此Prompt生成好的回答",
            "一致性：是否与系统风格保持一致"
        ]
    
    def generate_prompt(self, context: PromptContext) -> GeneratedPrompt:
        """根据上下文生成最适合的Prompt（返回数据类）"""
        try:
            # 无客户端则直接返回后备
            if self.openai_client is None:
                return self._generate_fallback_prompt(context)
            # 构建Prompt生成请求
            generation_prompt = self._build_generation_prompt(context)
            
            # 调用AI生成Prompt
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的Prompt工程师，擅长为不同场景生成高质量的Prompt。"},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            generated_text = response.choices[0].message.content
            
            # 解析生成的Prompt
            parsed_prompt = self._parse_generated_prompt(generated_text)
            
            # 评估Prompt质量
            confidence_score = self._evaluate_prompt_quality(parsed_prompt, context)
            
            return GeneratedPrompt(
                prompt_text=parsed_prompt,
                confidence_score=confidence_score,
                reasoning=self._generate_reasoning(context, parsed_prompt),
                optimization_suggestions=self._generate_optimization_suggestions(parsed_prompt, context),
                created_at=datetime.now(),
                context_used=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"生成Prompt时出错: {e}")
            # 返回默认Prompt
            return self._generate_fallback_prompt(context)

    # 结构化封装：统一返回 OperationResult
    def generate_prompt_structured(self, context: PromptContext) -> Dict[str, Any]:
        """返回结构化结果: { success, data, error, meta }"""
        meta: Dict[str, Any] = {}
        mode = "mock" if self.openai_client is None else "ai"
        meta["mode"] = mode
        meta["model"] = self.model
        try:
            result = self.generate_prompt(context)
            return {
                "success": True,
                "data": self._to_dict(result),
                "error": None,
                "meta": meta
            }
        except Exception as e:
            logger.error(f"生成Prompt失败: {e}")
            return {"success": False, "data": None, "error": str(e), "meta": meta}
    
    def _build_generation_prompt(self, context: PromptContext) -> str:
        """构建Prompt生成的请求"""
        return f"""
        请为以下场景生成一个高质量的Prompt：

        任务类型：{context.task_type}
        用户输入：{context.user_input}
        
        用户背景信息：
        - 个人资料：{json.dumps(context.user_profile, ensure_ascii=False)}
        - 当前目标：{', '.join(context.current_goals)}
        - 心情状态：{context.mood_state}
        - 可用时间：{context.available_time or '不限'}
        - 位置：{context.location or '未知'}
        - 天气：{context.weather or '未知'}

        对话历史（最近3轮）：
        {self._format_conversation_history(context.conversation_history[-3:])}

        要求：
        1. 生成的Prompt要清晰、具体、可执行
        2. 要体现用户的个性化需求
        3. 要包含必要的上下文信息
        4. 要符合任务类型的特点
        5. 要能够引导AI生成高质量的回答

        请直接返回生成的Prompt文本，不需要额外的解释。
        """
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """格式化对话历史"""
        if not history:
            return "无对话历史"
        
        formatted = []
        for i, turn in enumerate(history):
            formatted.append(f"第{i+1}轮：用户说'{turn.get('user_input', '')}'，助手回答'{turn.get('assistant_response', '')}'")
        
        return "\n".join(formatted)
    
    def _parse_generated_prompt(self, generated_text: str) -> str:
        """解析AI生成的Prompt文本"""
        # 清理和提取Prompt文本
        lines = generated_text.strip().split('\n')
        prompt_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('```') and not line.startswith('要求：') and not line.startswith('任务类型：'):
                prompt_lines.append(line)
        
        return '\n'.join(prompt_lines) if prompt_lines else generated_text.strip()
    
    def _evaluate_prompt_quality(self, prompt: str, context: PromptContext) -> float:
        """评估Prompt质量，返回0-1的置信度分数"""
        try:
            evaluation_prompt = f"""
            请评估以下Prompt的质量，给出0-1之间的分数：

            Prompt：{prompt}
            
            评估标准：
            {chr(10).join(f"{i+1}. {criterion}" for i, criterion in enumerate(self.quality_criteria))}
            
            请分析每个标准，然后给出总体评分（0-1之间，保留两位小数）。
            格式：评分：X.XX
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个Prompt质量评估专家。"},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            response_text = response.choices[0].message.content
            
            # 提取评分
            if "评分：" in response_text:
                score_text = response_text.split("评分：")[-1].strip()
                try:
                    score = float(score_text)
                    return min(max(score, 0.0), 1.0)  # 确保在0-1范围内
                except ValueError:
                    pass
            
            # 如果无法解析，返回默认分数
            return 0.8
            
        except Exception as e:
            logger.error(f"评估Prompt质量时出错: {e}")
            return 0.7
    
    def _generate_reasoning(self, context: PromptContext, prompt: str) -> str:
        """生成Prompt选择的推理过程"""
        try:
            reasoning_prompt = f"""
            请解释为什么这个Prompt适合当前场景：

            Prompt：{prompt}
            
            场景信息：
            - 任务类型：{context.task_type}
            - 用户输入：{context.user_input}
            - 用户目标：{', '.join(context.current_goals)}
            
            请简要说明这个Prompt如何满足用户需求，以及它的优势。
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个AI系统分析专家。"},
                    {"role": "user", "content": reasoning_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"生成推理过程时出错: {e}")
            return "基于用户需求和上下文信息生成的个性化Prompt"
    
    def _generate_optimization_suggestions(self, prompt: str, context: PromptContext) -> List[str]:
        """生成Prompt优化建议"""
        try:
            optimization_prompt = f"""
            请为以下Prompt提供3-5条优化建议：

            Prompt：{prompt}
            
            场景：{context.task_type} - {context.user_input}
            
            请提供具体的、可操作的优化建议，每条建议要简洁明了。
            格式：
            1. 建议内容
            2. 建议内容
            ...
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个Prompt优化专家。"},
                    {"role": "user", "content": optimization_prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 解析建议
            suggestions = []
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('-')):
                    suggestion = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    if suggestion:
                        suggestions.append(suggestion)
            
            return suggestions if suggestions else ["可以尝试增加更多上下文信息", "考虑添加具体的输出格式要求"]
            
        except Exception as e:
            logger.error(f"生成优化建议时出错: {e}")
            return ["可以尝试增加更多上下文信息", "考虑添加具体的输出格式要求"]
    
    def _generate_fallback_prompt(self, context: PromptContext) -> GeneratedPrompt:
        """生成备用Prompt"""
        base_template = self.base_templates.get(context.task_type, self.base_templates["conversation"])
        
        fallback_prompt = f"""
        {base_template}
        
        用户当前需求：{context.user_input}
        用户目标：{', '.join(context.current_goals)}
        
        请基于以上信息，为用户提供个性化的帮助和建议。
        """
        
        return GeneratedPrompt(
            prompt_text=fallback_prompt,
            confidence_score=0.6,
            reasoning="使用基础模板生成的备用Prompt",
            optimization_suggestions=["可以尝试重新生成以获得更好的Prompt"],
            created_at=datetime.now(),
            context_used=context.__dict__
        )
    
    def optimize_prompt(self, original_prompt: str, user_feedback: str, context: PromptContext) -> GeneratedPrompt:
        """基于用户反馈优化Prompt（返回数据类）"""
        try:
            optimization_prompt = f"""
            请基于用户反馈优化以下Prompt：

            原始Prompt：{original_prompt}
            
            用户反馈：{user_feedback}
            
            当前场景：
            - 任务类型：{context.task_type}
            - 用户输入：{context.user_input}
            
            请优化Prompt，使其：
            1. 更好地满足用户需求
            2. 提高响应质量
            3. 减少误解和错误
            4. 保持个性化和一致性
            
            请直接返回优化后的Prompt文本。
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个Prompt优化专家。"},
                    {"role": "user", "content": optimization_prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            optimized_text = response.choices[0].message.content.strip()
            
            # 评估优化后的Prompt
            confidence_score = self._evaluate_prompt_quality(optimized_text, context)
            
            return GeneratedPrompt(
                prompt_text=optimized_text,
                confidence_score=confidence_score,
                reasoning=f"基于用户反馈'{user_feedback}'优化的Prompt",
                optimization_suggestions=["继续收集用户反馈以进一步优化"],
                created_at=datetime.now(),
                context_used=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"优化Prompt时出错: {e}")
            return self._generate_fallback_prompt(context)

    def optimize_prompt_structured(self, original_prompt: str, user_feedback: str, context: PromptContext) -> Dict[str, Any]:
        """结构化优化结果"""
        meta: Dict[str, Any] = {"mode": "mock" if self.openai_client is None else "ai", "model": self.model}
        try:
            result = self.optimize_prompt(original_prompt, user_feedback, context)
            return {"success": True, "data": self._to_dict(result), "error": None, "meta": meta}
        except Exception as e:
            logger.error(f"优化Prompt失败: {e}")
            return {"success": False, "data": None, "error": str(e), "meta": meta}

    @staticmethod
    def _to_dict(obj: Any) -> Dict[str, Any]:
        try:
            return asdict(obj)
        except Exception:
            if hasattr(obj, "__dict__"):
                return dict(obj.__dict__)
            return {"value": str(obj)}

class PromptManager:
    """Prompt管理器，负责存储、检索和管理生成的Prompt"""
    
    def __init__(self):
        self.prompt_history: List[GeneratedPrompt] = []
        self.prompt_cache: Dict[str, GeneratedPrompt] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
    
    def store_prompt(self, prompt: GeneratedPrompt):
        """存储生成的Prompt"""
        self.prompt_history.append(prompt)
        
        # 创建缓存键
        cache_key = f"{prompt.context_used.get('task_type', 'unknown')}_{hash(prompt.context_used.get('user_input', ''))}"
        self.prompt_cache[cache_key] = prompt
    
    def get_similar_prompt(self, context: PromptContext) -> Optional[GeneratedPrompt]:
        """查找相似的Prompt"""
        cache_key = f"{context.task_type}_{hash(context.user_input)}"
        return self.prompt_cache.get(cache_key)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.prompt_history:
            return {"total_prompts": 0, "avg_confidence": 0.0}
        
        total_prompts = len(self.prompt_history)
        avg_confidence = sum(p.confidence_score for p in self.prompt_history) / total_prompts
        
        # 按任务类型统计
        task_stats = {}
        for prompt in self.prompt_history:
            task_type = prompt.context_used.get('task_type', 'unknown')
            if task_type not in task_stats:
                task_stats[task_type] = []
            task_stats[task_type].append(prompt.confidence_score)
        
        # 计算每种任务类型的平均置信度
        for task_type in task_stats:
            task_stats[task_type] = sum(task_stats[task_type]) / len(task_stats[task_type])
        
        return {
            "total_prompts": total_prompts,
            "avg_confidence": avg_confidence,
            "task_type_stats": task_stats,
            "recent_prompts": len([p for p in self.prompt_history if (datetime.now() - p.created_at).days <= 7])
        }

    def get_performance_stats_structured(self) -> Dict[str, Any]:
        stats = self.get_performance_stats()
        return {"success": True, "data": stats, "error": None, "meta": {}}

    @staticmethod
    def _to_dict(obj: Any) -> Dict[str, Any]:
        try:
            return asdict(obj)
        except Exception:
            if hasattr(obj, "__dict__"):
                return dict(obj.__dict__)
            return {"value": str(obj)}

# 使用示例
def demo_usage():
    """演示如何使用AI Prompt生成器"""
    print("🚀 AI Prompt生成器演示")
    print("=" * 50)
    
    # 注意：这里需要真实的API密钥
    # api_key = "your-openai-api-key-here"
    # generator = AIPromptGenerator(api_key)
    
    print("由于没有真实的API密钥，这里展示代码结构：")
    
    # 创建示例上下文
    context = PromptContext(
        task_type="health_advice",
        user_input="我想提高睡眠质量",
        conversation_history=[
            {"user_input": "最近工作压力很大", "assistant_response": "我理解你的感受..."},
            {"user_input": "晚上总是睡不着", "assistant_response": "睡眠问题确实很常见..."}
        ],
        user_profile={"age": 30, "occupation": "程序员", "health_goals": ["改善睡眠", "减少压力"]},
        current_goals=["改善睡眠质量", "提高工作效率"],
        mood_state="压力较大",
        available_time="晚上9点后",
        location="家里",
        weather="阴天"
    )
    
    print(f"任务类型: {context.task_type}")
    print(f"用户输入: {context.user_input}")
    print(f"用户目标: {', '.join(context.current_goals)}")
    print(f"心情状态: {context.mood_state}")
    print(f"可用时间: {context.available_time}")
    
    print("\n这个系统可以：")
    print("1. 自动生成个性化的Prompt")
    print("2. 基于用户反馈优化Prompt")
    print("3. 评估Prompt质量")
    print("4. 管理Prompt历史")
    print("5. 提供性能统计")
    
    print("\n要使用真实功能，请：")
    print("1. 设置OpenAI API密钥")
    print("2. 创建AIPromptGenerator实例")
    print("3. 调用generate_prompt()方法")

if __name__ == "__main__":
    demo_usage()
