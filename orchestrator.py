#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两段式编排器（设计 → 执行）
Design → Execute Orchestrator

阶段1：设计结构化 Prompt（JSON）
阶段2：执行该 Prompt，产出面向用户的最终回复
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import os
import json
import logging

from json_prompt_generator import JSONPromptGenerator, PromptContext as JSONCtx
from intent_parser import parse_multi_intent
from silicon_client import silicon_chat_completion
from light_rag import simple_retrieve, format_knowledge_snippets
from knowledge_base import knowledge_base
from retrieval_system import retrieval_system
from agents import select_agent_by_intent, agent_profile_to_dict

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorContext:
    """编排器输入上下文（与 PromptContext 字段保持一致）。"""
    task_type: str
    user_input: str
    conversation_history: list
    user_profile: dict
    current_goals: list
    mood_state: str
    available_time: Optional[str] = None
    location: Optional[str] = None
    weather: Optional[str] = None
    # 为个性化记忆留一个 session_id，默认单一会话
    session_id: str = "default_session"


class PromptOrchestrator:
    """两段式编排器：设计 → 执行。"""

    def __init__(self, model: str = None):
        # 如果未显式传入，则使用环境变量 MODEL 或默认 DeepSeek/Qwen 模型
        self.model = model or os.getenv("MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.json_gen = JSONPromptGenerator()
        # 是否有可用的 DeepSeek / SiliconFlow API Key
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if self.api_key:
            logger.info("✅ 执行器将通过 SiliconFlow 调用模型 (DEEPSEEK_API_KEY 已配置)")
        else:
            logger.info("ℹ️ 未检测到 DEEPSEEK_API_KEY，执行阶段将使用 mock 模式")

    def analyze_intent_and_scene(self, user_input: str, previous_scene: Optional[str] = None) -> Dict[str, Any]:
        """
        轻量级多意图解析结果 → 提取当前主意图 & 场景主题，并为长期记忆准备 understanding 结构。

        返回:
            {
              "intent": 主意图（如 "study" / "work" / "life" / "general"）,
              "primary_topic": 主话题/场景（如 "study" / "work" / "family" 等）,
              "understanding": 完整理解结果（带 life_context.topic_analysis）
            }
        """
        try:
            understanding = parse_multi_intent(user_input) or {}
        except Exception as e:
            logger.error(f"意图解析失败，使用 general 兜底: {e}")
            return {
                "intent": "general",
                "primary_topic": previous_scene or "general",
                "understanding": {
                    "intent": "general",
                    "entities": {},
                    "confidence": 0.0,
                    "life_context": {
                        "topic_analysis": {
                            "primary_topic": previous_scene or "general",
                            "is_topic_switch": False,
                            "previous_topic": previous_scene or "general",
                        }
                    },
                },
            }

        segments = understanding.get("segments") or []
        main_intent = "general"
        primary_topic = previous_scene or "general"

        if segments:
            # 当前简单策略：取第一段作为主意图
            first = segments[0] or {}
            main_intent = (first.get("intent") or "general") or "general"
            # 有些解析器可能给出 topic / domain 字段；没有就回退到意图
            primary_topic = first.get("topic") or first.get("domain") or main_intent
        else:
            # 没有 segments 的情况，尝试直接从 understanding 顶层取
            main_intent = understanding.get("intent") or "general"
            primary_topic = understanding.get("primary_topic") or main_intent

        # 计算是否发生场景/话题切换
        is_switch = previous_scene is not None and primary_topic != previous_scene

        # 为知识库补齐 life_context 结构，便于后续行为模式分析使用
        life_ctx = understanding.get("life_context") or {}
        topic_analysis = life_ctx.get("topic_analysis") or {}
        topic_analysis.setdefault("primary_topic", primary_topic)
        topic_analysis.setdefault("previous_topic", previous_scene or primary_topic)
        topic_analysis.setdefault("is_topic_switch", is_switch)
        life_ctx["topic_analysis"] = topic_analysis
        understanding["life_context"] = life_ctx

        # 在 understanding 顶层补一个 intent 字段，方便下游直接使用
        understanding.setdefault("intent", main_intent)

        return {
            "intent": main_intent,
            "primary_topic": primary_topic,
            "understanding": understanding,
        }

    def design_prompt(self, ctx: OrchestratorContext) -> Dict[str, Any]:
        """阶段1：基于上下文设计结构化 JSON Prompt（单任务）。"""
        jctx = JSONCtx(
            task_type=ctx.task_type,
            user_input=ctx.user_input,
            conversation_history=ctx.conversation_history,
            user_profile=ctx.user_profile,
            current_goals=ctx.current_goals,
            mood_state=ctx.mood_state,
            available_time=ctx.available_time,
            location=ctx.location,
            weather=ctx.weather,
        )
        result = self.json_gen.generate_json_prompt(jctx)
        return {"success": result.get("success", True), "data": result.get("data"), "error": result.get("error"), "meta": {"stage": "design"}}

    def design_prompts_multi(self, user_input: str, base_ctx: OrchestratorContext) -> Dict[str, Any]:
        """多意图拆解 → 多任务 JSON Prompt 设计。
        返回: {success, data: {understanding, tasks: [{task_id,intent,text,json_prompt}]}}
        """
        understanding = parse_multi_intent(user_input)
        tasks = []
        for idx, seg in enumerate(understanding.get("segments", []), 1):
            task_type = self._map_intent_to_task(seg.get("intent", "general"))
            jctx = JSONCtx(
                task_type=task_type,
                user_input=seg.get("text", base_ctx.user_input),
                conversation_history=base_ctx.conversation_history,
                user_profile=base_ctx.user_profile,
                current_goals=base_ctx.current_goals,
                mood_state=base_ctx.mood_state,
                available_time=base_ctx.available_time,
                location=base_ctx.location,
                weather=base_ctx.weather,
            )
            res = self.json_gen.generate_json_prompt(jctx)
            tasks.append({
                "task_id": f"task_{idx}",
                "intent": seg.get("intent"),
                "text": seg.get("text"),
                "json_prompt": res.get("data")
            })
        return {"success": True, "data": {"understanding": understanding, "tasks": tasks}, "error": None, "meta": {"stage": "design_multi"}}

    def execute_prompt(self, json_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """阶段2：执行结构化 Prompt，产出最终文本回复。"""
        role = json_prompt.get("role", "assistant")
        agent_info = json_prompt.get("agent_profile") or {}
        task_description = json_prompt.get("task_description", "")
        user_context = json_prompt.get("user_context", {})
        required_outputs = json_prompt.get("required_outputs", [])
        constraints = json_prompt.get("constraints", [])
        output_format = json_prompt.get("output_format", {})

        # 将 JSON Prompt 编译为可读指令
        compiled = self._compile_prompt(role, task_description, user_context, required_outputs, constraints, output_format)

        # 无可用 API Key 时走本地 mock 逻辑
        if not self.api_key:
            final_text = self._mock_execute(required_outputs, task_description, user_context)
            return {
                "success": True,
                "data": {"final_text": final_text, "compiled_prompt": compiled},
                "error": None,
                "meta": {"stage": "execute", "mode": "mock"},
            }

        try:
            # 根据 agent_profile（如果有）构造更细致的 system 提示
            if agent_info:
                agent_name = agent_info.get("name", "Agent")
                agent_desc = agent_info.get("description", "")
                system_text = (
                    f"You are {agent_name}, working as an expert {role}. "
                    f"{agent_desc} "
                    "Always ground your answers in the provided RAG knowledge and user profile when possible."
                )
            else:
                system_text = f"You are an expert {role}. Always ground your answers in the provided context."

            reply, _raw = silicon_chat_completion(
                messages=[
                    {"role": "system", "content": system_text},
                    {"role": "user", "content": compiled},
                ],
                model=self.model,
                temperature=0.6,
                max_tokens=600,
            )
            final_text = reply.strip()
            return {
                "success": True,
                "data": {"final_text": final_text, "compiled_prompt": compiled},
                "error": None,
                "meta": {"stage": "execute", "mode": "ai", "model": self.model},
            }
        except Exception as e:
            logger.error(f"执行失败: {e}")
            final_text = self._mock_execute(required_outputs, task_description, user_context)
            return {"success": True, "data": {"final_text": final_text, "compiled_prompt": compiled}, "error": None, "meta": {"stage": "execute", "mode": "mock_fallback"}}

    def execute_prompts_multi(self, tasks: list) -> Dict[str, Any]:
        """执行多个 JSON Prompt 任务。"""
        results = []
        for t in tasks:
            jp = t.get("json_prompt", {})
            ex = self.execute_prompt(jp)
            results.append({"task_id": t.get("task_id"), "intent": t.get("intent"), "text": t.get("text"), "result": ex.get("data", {})})
        return {"success": True, "data": results, "error": None, "meta": {"stage": "execute_multi"}}

    def generate_and_respond(self, ctx: OrchestratorContext) -> Dict[str, Any]:
        """完整链路：设计 → 执行。"""
        design = self.design_prompt(ctx)
        if not design.get("success"):
            return {"success": False, "data": None, "error": design.get("error"), "meta": {"stage": "design"}}

        json_prompt = design.get("data", {})
        execute = self.execute_prompt(json_prompt)
        return {"success": True, "data": {"designed_prompt": json_prompt, "final_response": execute.get("data", {})}, "error": None, "meta": {"pipeline": "design_execute"}}

    def generate_and_respond_with_light_rag(self, ctx: OrchestratorContext, intent: str) -> Dict[str, Any]:
        """
        完整链路（带轻量级 RAG）：
        1) 设计 JSON Prompt
        2) 使用内置小知识库做简单检索
        3) 将检索结果作为 rag_knowledge 写入 user_context
        4) 执行 Prompt，生成最终回复

        说明：
        - intent 一般可以使用解析后的意图，例如 "health_tracking" 或 "learning_planning"
        - 当前 simple_retrieve 只区分 learning_planning vs 其它（健康）
        """
        design = self.design_prompt(ctx)
        if not design.get("success"):
            return {
                "success": False,
                "data": None,
                "error": design.get("error"),
                "meta": {"stage": "design"},
            }

        json_prompt = design.get("data", {}) or {}
        user_ctx = json_prompt.get("user_context") or {}

        # 1) 选择合适的场景 Agent，并把 Agent 画像写入 json_prompt
        agent = select_agent_by_intent(intent or "general")
        json_prompt["agent_profile"] = agent_profile_to_dict(agent)

        # 使用轻量级 RAG 检索若干知识片段（通用健康/学习知识）
        rag_results = simple_retrieve(user_input=ctx.user_input, intent=intent)
        light_rag_text = format_knowledge_snippets(rag_results, max_snippets=3)

        # 基于知识库构建用户画像摘要
        session_id = ctx.session_id or "default_session"
        user_profile_text = knowledge_base.get_user_profile_summary_text(session_id)

        # 使用向量检索系统（Chroma + sentence-transformers）获取更丰富的知识片段
        try:
            # 这里的 understanding 目前只传 intent，后续可以接入真实的多维理解结果
            understanding = {"intent": intent}
            retrieval_summary = retrieval_system.retrieve_knowledge(
                user_input=ctx.user_input,
                session_id=session_id,
                understanding=understanding,
                context={},
            )
            vector_top_results = retrieval_summary.get("top_results", [])
            if vector_top_results:
                lines = []
                for i, item in enumerate(vector_top_results[:3], start=1):
                    doc = str(item.get("document", "")).strip()
                    ktype = item.get("knowledge_type", "unknown")
                    score = float(item.get("final_score", 0.0))
                    if not doc:
                        continue
                    lines.append(f"{i}. [type={ktype}, score={score:.3f}] {doc}")
                vector_rag_text = "\n".join(lines) if lines else "No vector-based results."
            else:
                vector_rag_text = "No vector-based knowledge was retrieved for this query."
        except Exception as e:
            # 如果向量检索出错，不阻塞主流程
            logger.error(f"向量检索失败（已降级为轻量 RAG）：{e}")
            vector_rag_text = "Vector-based retrieval failed; please answer based on other context."

        # 将“用户画像 + 轻量知识 + 向量知识片段”组装成一个整体的 RAG 上下文
        combined_rag = (
            "User profile and habits (long-term memory):\n"
            f"{user_profile_text}\n\n"
            "Lightweight domain knowledge snippets (rule/keyword-based):\n"
            f"{light_rag_text}\n\n"
            "Vector-store knowledge snippets (semantic retrieval):\n"
            f"{vector_rag_text}"
        )

        # 将检索结果写入 user_context，供编译 Prompt 时使用
        user_ctx["rag_knowledge"] = combined_rag
        json_prompt["user_context"] = user_ctx

        execute = self.execute_prompt(json_prompt)
        return {
            "success": True,
            "data": {
                "designed_prompt": json_prompt,
                "final_response": execute.get("data", {}),
                "rag_knowledge": combined_rag,
            },
            "error": None,
            "meta": {"pipeline": "design_execute_light_rag"},
        }

    def generate_and_respond_multi(self, user_input: str, base_ctx: OrchestratorContext) -> Dict[str, Any]:
        """完整链路（多任务）：多意图 → 多设计 → 多执行 → 聚合。"""
        d = self.design_prompts_multi(user_input, base_ctx)
        if not d.get("success"):
            return d
        tasks = d.get("data", {}).get("tasks", [])
        ex = self.execute_prompts_multi(tasks)
        final = self._aggregate_results(ex.get("data", []))
        return {"success": True, "data": {"designed": d.get("data"), "executed": ex.get("data"), "final": final}, "error": None, "meta": {"pipeline": "design_execute_multi"}}

    def _compile_prompt(self, role: str, task_description: str, user_context: Dict[str, Any], required_outputs: list, constraints: list, output_format: Dict[str, Any]) -> str:
        """将结构化 JSON Prompt 编译为模型可读的自然语言指令。"""
        parts = [
            f"Task: {task_description}",
            "User Context:",
            json.dumps(user_context, ensure_ascii=False, indent=2),
            "\nRequired Outputs:",
        ]

        # 如果存在轻量级 RAG 上下文，则单独突出展示
        rag_text = user_context.get("rag_knowledge")
        if rag_text:
            parts.append("\nRetrieved Knowledge Snippets (RAG context):\n")
            parts.append(rag_text)

        for i, item in enumerate(required_outputs, 1):
            parts.append(f"{i}. [{item.get('type','item')}] {item.get('description','')} -> format: {item.get('format','text')}")
        if constraints:
            parts.append("\nConstraints:")
            for c in constraints:
                parts.append(f"- {c}")
        if output_format:
            parts.append("\nOutput Format Preferences:")
            parts.append(json.dumps(output_format, ensure_ascii=False))
        parts.append("\nPlease generate a concise, actionable response following the required outputs.")
        return "\n".join(parts)

    def _mock_execute(self, required_outputs: list, task_description: str, user_context: Dict[str, Any]) -> str:
        """基于 required_outputs 生成骨架化答案（无模型时）。"""
        lines = [f"【任务】{task_description}", "【摘要】基于你的情况，提供结构化建议如下："]
        for i, item in enumerate(required_outputs[:5], 1):
            typ = item.get("type", f"item_{i}")
            desc = item.get("description", "")
            fmt = item.get("format", "text")
            lines.append(f"{i}. {desc or typ}（格式：{fmt}）")
            lines.append("   - 要点1：...\n   - 要点2：...\n   - 要点3：...")
        lines.append("【说明】这是在无模型/降级模式下的示例输出。")
        return "\n".join(lines)

    @staticmethod
    def _map_intent_to_task(intent: str) -> str:
        mapping = {
            "schedule_management": "schedule_assistant",
            "pickup_kids": "schedule_assistant",
            "sports_activity": "schedule_assistant",
            "learning_planning": "learning_coach",
            "work_task": "work_assistant",
            "general": "conversation",
        }
        return mapping.get(intent, "conversation")

    @staticmethod
    def _aggregate_results(items: list) -> Dict[str, Any]:
        # 简单聚合：按顺序拼接文本
        combined = []
        for it in items:
            txt = it.get("result", {}).get("final_text", "")
            if txt:
                combined.append(f"[{it.get('intent','task')}] {txt}")
        summary = "\n\n".join(combined) if combined else "(无结果)"
        return {"summary": summary, "count": len(items)}


