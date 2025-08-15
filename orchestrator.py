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

try:
    import openai
except Exception:  # 允许在无 openai 环境下导入本模块
    openai = None

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


class PromptOrchestrator:
    """两段式编排器：设计 → 执行。"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.json_gen = JSONPromptGenerator()
        self.openai_client = None

        # 优先使用通用 OPENAI_API_KEY；无则尝试 AZURE_OPENAI_API_KEY（但此处不走 Azure 特殊参数）
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        if openai and api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("✅ 执行器 OpenAI 客户端已初始化")
            except Exception as e:
                logger.warning(f"⚠️ 执行器 OpenAI 初始化失败，使用 mock 执行: {e}")
                self.openai_client = None

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
        task_description = json_prompt.get("task_description", "")
        user_context = json_prompt.get("user_context", {})
        required_outputs = json_prompt.get("required_outputs", [])
        constraints = json_prompt.get("constraints", [])
        output_format = json_prompt.get("output_format", {})

        # 将 JSON Prompt 编译为可读指令
        compiled = self._compile_prompt(role, task_description, user_context, required_outputs, constraints, output_format)

        if self.openai_client is None:
            # mock 执行：根据 required_outputs 生成骨架化答案
            final_text = self._mock_execute(required_outputs, task_description, user_context)
            return {"success": True, "data": {"final_text": final_text, "compiled_prompt": compiled}, "error": None, "meta": {"stage": "execute", "mode": "mock"}}

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {role}."},
                    {"role": "user", "content": compiled},
                ],
                temperature=0.6,
                max_tokens=600,
            )
            final_text = resp.choices[0].message.content.strip()
            return {"success": True, "data": {"final_text": final_text, "compiled_prompt": compiled}, "error": None, "meta": {"stage": "execute", "mode": "ai", "model": self.model}}
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


