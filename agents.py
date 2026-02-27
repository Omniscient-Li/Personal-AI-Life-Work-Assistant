#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级多场景 Agent 定义

设计理念：
- 不做复杂的多轮自协作，只做“按场景切换不同 Agent 角色”
- 每个 Agent 主要提供：名称、描述、适配的意图列表、偏好的工具/能力标签
- Orchestrator 负责：解析意图 → 选择合适的 Agent → 把 Agent 信息写入 Prompt
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AgentProfile:
    """Agent 的静态画像，用于提示模型“你现在扮演谁、重点做什么”"""

    name: str
    description: str
    intents: List[str]
    preferred_tools: List[str]
    scenario: str  # 学习 / 工作 / 生活 / 通用 等


# 轻量场景 Agent 列表
STUDY_AGENT = AgentProfile(
    name="StudyAgent",
    scenario="learning",
    description=(
        "You are a patient and structured learning coach. "
        "You help the user design study plans, break down complex topics, "
        "and keep a sustainable learning rhythm."
    ),
    intents=["learning_planning"],
    preferred_tools=["rag_knowledge", "user_profile", "schedule_planning"],
)

WORK_AGENT = AgentProfile(
    name="WorkAgent",
    scenario="work",
    description=(
        "You are a pragmatic productivity and work assistant. "
        "You help the user clarify priorities, break down tasks, "
        "and design realistic action plans around deadlines."
    ),
    intents=["work_task", "schedule_management"],
    preferred_tools=["rag_knowledge", "user_profile", "task_planning"],
)

LIFE_AGENT = AgentProfile(
    name="LifeAgent",
    scenario="life",
    description=(
        "You are a gentle life and wellbeing assistant. "
        "You pay attention to health, rest, and emotional balance, "
        "and help the user build sustainable daily routines."
    ),
    intents=["sports_activity", "pickup_kids"],
    preferred_tools=["rag_knowledge", "user_profile", "habit_tracking"],
)

GENERAL_AGENT = AgentProfile(
    name="GeneralAgent",
    scenario="general",
    description=(
        "You are a friendly general assistant. "
        "You chat naturally, answer questions, and try to be practically helpful."
    ),
    intents=["general"],
    preferred_tools=["rag_knowledge", "user_profile"],
)


ALL_AGENTS: List[AgentProfile] = [
    STUDY_AGENT,
    WORK_AGENT,
    LIFE_AGENT,
    GENERAL_AGENT,
]


def select_agent_by_intent(intent: str) -> AgentProfile:
    """
    根据解析出的 intent 选择一个 Agent。
    - 精确匹配：如果某个 Agent 声明了该 intent，则优先返回
    - 回退：找不到匹配时，返回通用 GeneralAgent
    """
    for agent in ALL_AGENTS:
        if intent in agent.intents:
            return agent
    return GENERAL_AGENT


def agent_profile_to_dict(agent: AgentProfile) -> Dict[str, str]:
    """
    方便塞进 JSON Prompt / user_context 的序列化形式。
    """
    return {
        "name": agent.name,
        "scenario": agent.scenario,
        "description": agent.description,
        "preferred_tools": agent.preferred_tools,
    }


