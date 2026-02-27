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


def safe_print(text: Any) -> None:
    """
    在 GBK 终端中安全打印字符串：
    - 尽量正常打印
    - 如果遇到无法编码的字符（例如 emoji），自动忽略这些字符，避免 UnicodeEncodeError
    """
    try:
        if not isinstance(text, str):
            text = str(text)
        print(text)
    except UnicodeEncodeError:
        try:
            safe = text.encode("gbk", errors="ignore").decode("gbk", errors="ignore")
            print(safe)
        except Exception:
            # 最保守兜底
            print(repr(text))

from ai_prompt_generator import AIPromptGenerator, PromptContext
from config import Config
from orchestrator import PromptOrchestrator, OrchestratorContext
from agents import select_agent_by_intent
from knowledge_base import knowledge_base

class AIPromptSystem:
    """AI Prompt生成器系统主类"""
    
    def __init__(self):
        self.config = Config()
        self.prompt_generator = None
        
        # 初始化AI Prompt生成器
        self._initialize_ai_generator()
    
    def _initialize_ai_generator(self):
        """初始化AI Prompt生成器"""
        try:
            # 直接初始化基于 DeepSeek / SiliconFlow 的 Prompt 生成器
            self.prompt_generator = AIPromptGenerator()
            # 避免终端编码问题，这里只使用英文/ASCII 文本
            print("AI Prompt generator initialized (SiliconFlow / DeepSeek).")
        except Exception as e:
            print(f"AI generator initialization failed: {e}")
            self.prompt_generator = None
    
    def demo_basic_functionality(self, output_mode: str = "text"):
        """Demonstrate basic functionality (supports structured output)"""
        header = {"type": "demo_basic", "title": "AI Prompt Generator Basic Demo"}
        if output_mode == "text":
            print("AI Prompt Generator - Basic Demo")
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
            print(f"Task type: {context.task_type}")
            print(f"User input: {context.user_input}")
            print(f"User goals: {', '.join(context.current_goals)}")
            print(f"Mood state: {context.mood_state}")
            print(f"Available time: {context.available_time}")
        
        # 生成Prompt（真实模型模式）
        if not self.prompt_generator:
            safe_print("AI Prompt generator not initialized, skip basic demo.")
            return

            result = self.prompt_generator.generate_prompt_structured(context)
            if output_mode == "json":
                print(json.dumps({**header, **result}, ensure_ascii=False))
            else:
            safe_print("\nUsing AI to generate prompt...")
            safe_print(result.get("data", {}).get("prompt_text", ""))
        
        if output_mode == "text":
            print("\n系统功能：")
            print("1. 自动生成个性化的Prompt")
            print("2. 基于用户反馈优化Prompt")
            print("3. 评估Prompt质量")
            print("4. 管理Prompt历史")
            print("5. 提供性能统计")
    
  
    def chat_loop(self):
        """
        简单命令行对话模式：
        - 用户直接输入自然语言
        - 内部调用 Orchestrator + RAG + Agent
        - 连续多轮对话共用同一个 session_id 和 history
        """
        # 在自动化环境中禁止进入交互，避免阻塞
        if os.getenv("AIPS_NO_INTERACTIVE", "").lower() in ("1", "true", "yes"):
            safe_print("AIPS_NO_INTERACTIVE 已开启，跳过命令行对话模式。")
            return

        orch = PromptOrchestrator()
        session_id = os.getenv("AIPS_SESSION_ID", "cli_session")
        conversation_history = []
        # user_profile 用于给 JSONPromptGenerator + Orchestrator 提供额外上下文
        user_profile: Dict[str, Any] = {}
        # 跟踪当前主线场景（例如 work / study / life / general）
        current_scene: str = "general"

        safe_print("个人 AI 助手（对话模式）")
        safe_print("输入内容开始对话，输入 exit / quit 退出。\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                    break
                
                if not user_input:
                    continue
            if user_input.lower() in ("exit", "quit", "q"):
                safe_print("会话已结束。")
                break

            # 1) 解析当前轮的意图 & 场景，用于 Agent 选择 + 长期记忆
            analysis = orch.analyze_intent_and_scene(user_input, previous_scene=current_scene)
            intent = analysis.get("intent", "general")
            primary_topic = analysis.get("primary_topic", current_scene)
            understanding = analysis.get("understanding", {})

            # 根据当前意图选择 Agent，用于给用户一个可见的“角色”提示
            agent = select_agent_by_intent(intent or "general")

            # 更新当前主线场景，并写入 user_profile，方便 JSON Prompt 设计阶段引用
            current_scene = primary_topic or current_scene
            user_profile["current_scene"] = current_scene
            user_profile["last_intent"] = intent
            user_profile["last_agent"] = agent.name

            # 构造编排上下文
            ctx = OrchestratorContext(
                task_type="conversation",
                    user_input=user_input,
                conversation_history=conversation_history,
                user_profile=user_profile,
                current_goals=[],
                mood_state="unknown",
                session_id=session_id,
            )

            # 2) 使用识别出的意图驱动 Agent/RAG，而不是固定 general
            result = orch.generate_and_respond_with_light_rag(ctx, intent=intent)
            data = result.get("data", {})
            final_resp = data.get("final_response", {}).get("final_text", "").strip() or "(无回复)"

            # 在终端中展示当前 Agent 和场景信息，增强多 Agent 的存在感
            safe_print(f"\n[Agent: {agent.name} | Scene: {current_scene} | Intent: {intent}]")
            safe_print("Assistant:")
            safe_print(final_resp + "\n")

            # 3) 将本轮对话存入持久化知识库（用于长期记忆 + 用户画像）
            try:
                knowledge_base.store_conversation(
                    session_id=session_id,
                    user_input=user_input,
                    ai_response=final_resp,
                    understanding=understanding,
                )
            except Exception as e:
                # 不因知识库存储失败而中断对话
                safe_print(f"(warning) 存储对话到知识库失败: {e}")

            # 4) 追加到当前会话的内存历史（供短期上下文使用）
            conversation_history.append(
                {"user_input": user_input, "assistant_response": final_resp, "intent": intent, "scene": current_scene}
            )
    
    def run(self):
        """运行主程序：支持 demo 模式 和 对话模式"""
        mode = os.getenv("AIPS_MODE", "demo").lower()

        if mode == "chat":
            # 进入对话模式（真正给用户交互使用）
            self.chat_loop()
            return

        # 默认：保留原有 Demo 演示逻辑
        output_mode = os.getenv("AIPS_OUTPUT", "text").lower()
        if output_mode == "text":
            print("AI Prompt生成器系统")
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
            print("\n两段式链路演示（设计 → 执行）")
            print("-" * 60)
            print("[设计] 结构化 JSON Prompt 预览：")
            safe_print(json.dumps(design.get("data", {}), ensure_ascii=False, indent=2))
            print("\n[执行] 最终回复：")
            safe_print(execute.get("data", {}).get("final_text", "(无)"))

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
            print("\n多任务链路演示（多意图 → 多设计/执行）")
            print("-" * 60)
            print("[聚合结果]\n")
            safe_print(multi_res.get("data", {}).get("final", {}).get("summary", "(无)"))

        # 3. 其它教学向 Demo（Prompt 优化、Prompt 管理、命令行交互）已移除，主程序聚焦在：
        #    - 基础 Prompt 生成功能
        #    - Orchestrator 两段式 & 多任务链路（内部已集成 RAG + Agent）

if __name__ == "__main__":
    system = AIPromptSystem()
    system.run()
