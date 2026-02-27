#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一封装 SiliconFlow / DeepSeek Chat Completions 调用。

从环境变量读取：
- DEEPSEEK_API_KEY
- DEEPSEEK_API_URL (默认: https://api.siliconflow.cn/v1/chat/completions)
- MODEL, MAX_TOKEN, TEMPERATURE, TOP_P, TOP_K, FREQUENCY_PENALTY, MIN_P
"""

import os
import logging
from typing import Any, Dict, List, Tuple

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 尝试加载项目根目录下的 .env（如果存在）
load_dotenv()


def _get_env_float(name: str, default: float) -> float:
    val = os.getenv(name)
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        logger.warning("环境变量 %s=%r 解析为 float 失败，使用默认值 %s", name, val, default)
        return default


def _get_env_int(name: str, default: int) -> int:
    val = os.getenv(name)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        logger.warning("环境变量 %s=%r 解析为 int 失败，使用默认值 %s", name, val, default)
        return default


API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
DEFAULT_MODEL = os.getenv("MODEL", "Qwen/Qwen2.5-7B-Instruct")
DEFAULT_MAX_TOKENS = _get_env_int("MAX_TOKEN", 512)
DEFAULT_TEMPERATURE = _get_env_float("TEMPERATURE", 0.7)
DEFAULT_TOP_P = _get_env_float("TOP_P", 0.7)
DEFAULT_TOP_K = _get_env_int("TOP_K", 50)
DEFAULT_FREQ_PENALTY = _get_env_float("FREQUENCY_PENALTY", 0.0)
DEFAULT_MIN_P = _get_env_float("MIN_P", 0.05)


def silicon_chat_completion(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = None,
    max_tokens: int = None,
    **extra_params: Any,
) -> Tuple[str, Dict[str, Any]]:
    """
    调用 SiliconFlow Chat Completions 接口。

    返回:
        (assistant_text, raw_json)
    """
    if not API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置，无法调用 SiliconFlow 接口")

    payload: Dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": DEFAULT_TEMPERATURE if temperature is None else float(temperature),
        "max_tokens": DEFAULT_MAX_TOKENS if max_tokens is None else int(max_tokens),
        "top_p": DEFAULT_TOP_P,
        "top_k": DEFAULT_TOP_K,
        "frequency_penalty": DEFAULT_FREQ_PENALTY,
        "min_p": DEFAULT_MIN_P,
        "stream": False,
    }

    # 允许调用方覆盖/补充参数
    payload.update(extra_params)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    try:
        text = data["choices"][0]["message"]["content"]
    except Exception as e:  # noqa: BLE001
        logger.error("解析 SiliconFlow 响应失败: %s; data=%r", e, data)
        raise

    return text, data


