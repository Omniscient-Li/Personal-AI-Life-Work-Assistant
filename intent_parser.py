#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量多意图解析器
Multi-intent parser: 句子分割 + 规则识别 + 简单实体抽取（时间/活动）
输出结构化的多意图理解结果，供任务规划使用。
"""

from typing import List, Dict
import re


def split_sentences(text: str) -> List[str]:
    # 主要标点分割，再用中文逗号切分但保留语义
    seps = ["。", "！", "？", ";", "；"]
    for sep in seps:
        text = text.replace(sep, "|")
    parts = []
    for chunk in text.split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        # 再按逗号粗略切分
        sub = [c.strip() for c in re.split("，|,", chunk) if c.strip()]
        parts.extend(sub)
    # 去重保持顺序
    seen = set()
    unique = []
    for p in parts:
        if p not in seen:
            unique.append(p)
            seen.add(p)
    return unique


def identify_intent(sentence: str) -> str:
    s = sentence.lower()
    # 简化规则
    if any(k in s for k in ["开会", "会议", "安排", "日程", "时间"]):
        return "schedule_management"
    if any(k in s for k in ["接孩子", "接小孩", "放学", "学校"]):
        return "pickup_kids"
    if any(k in s for k in ["打球", "运动", "锻炼", "健身"]):
        return "sports_activity"
    if any(k in s for k in ["学习", "课程", "作业"]):
        return "learning_planning"
    if any(k in s for k in ["工作", "任务", "项目"]):
        return "work_task"
    return "general"


def extract_time_entities(sentence: str) -> List[str]:
    patterns = [
        r"今天|明天|后天|下午|上午|中午|晚上|早上",
        r"\d+点|\d+:\d+",
    ]
    found: List[str] = []
    for pat in patterns:
        found.extend(re.findall(pat, sentence))
    # 去重
    return list(dict.fromkeys(found))


def extract_activity(sentence: str) -> List[str]:
    act_words = ["开会", "接孩子", "打球", "学习", "健身", "跑步"]
    return [w for w in act_words if w in sentence]


def parse_multi_intent(user_input: str) -> Dict:
    segments = split_sentences(user_input)
    items: List[Dict] = []
    for seg in segments:
        intent = identify_intent(seg)
        entities = {
            "time": extract_time_entities(seg),
            "activities": extract_activity(seg),
        }
        items.append({"text": seg, "intent": intent, "entities": entities})
    return {
        "original_input": user_input,
        "segments": items
    }


