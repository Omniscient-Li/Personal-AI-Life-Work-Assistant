#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal runnable RAG-style demo (without external vector DB):
- Use several built-in "health/learning tips" as a tiny knowledge base
- Do a very simple "similarity score" based on keyword matches
- Take the top-scored entries as knowledge snippets and put them into the prompt
- Then ask the DeepSeek / SiliconFlow model to answer

Usage (under project root):
    python rag_demo.py

Prerequisites:
- Environment variables or .env must correctly set DEEPSEEK_API_KEY / DEEPSEEK_API_URL / MODEL, etc.

Note:
- This is a lightweight educational demo that does not depend on sentence-transformers / Chroma.
  It is mainly to help you intuitively feel that:
  RAG = retrieve several snippets + ask the LLM with those snippets as context.
"""

from typing import Dict, Any, List
import textwrap

from silicon_client import silicon_chat_completion
from light_rag import simple_retrieve, format_knowledge_snippets


def run_rag_demo(intent: str = "health_tracking") -> None:
    """Run a lightweight RAG-style workflow once and print the result."""
    if intent == "learning_planning":
        user_input = "I want to systematically improve my study efficiency. What specific suggestions do you have?"
    else:
        user_input = "I want to improve my physical health. Do you have any simple and actionable suggestions?"

    print(f"\n[Question] User question: {user_input}")

    # 1. Simple retrieval of several relevant "knowledge snippets"
    print("[RAG] Using the built-in tiny knowledge base for simple retrieval...")
    results = simple_retrieve(user_input=user_input, intent=intent)
    knowledge_text = format_knowledge_snippets(results, max_snippets=3)

    print("\n[Knowledge] Retrieved snippets (used as RAG context):")
    print(textwrap.indent(knowledge_text, prefix="  "))

    # 2. Build the prompt to send to the LLM
    system_prompt = (
        "You are an intelligent assistant who is good at analyzing information based on given knowledge.\n"
        "You must prioritize answering the user's question using the following knowledge snippets.\n"
        "If the snippets do not contain relevant information, you may use general knowledge with reasonable inference,\n"
        "but you should clearly state that the evidence is limited. Please provide your final answer in English."
    )

    user_message = (
        f"User question: {user_input}\n\n"
        f"Below are knowledge snippets related to the question. Please read them carefully before answering:\n"
        f"{knowledge_text}\n\n"
        "Now please provide a concise and well-structured answer in English."
    )

    # 3. Call the DeepSeek / SiliconFlow model
    print("\n[LLM] Calling the LLM to generate a retrieval-augmented answer...")
    try:
        reply, _raw = silicon_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            # model 从环境变量 MODEL 读取；如果你想单独指定，可以在这里传 model="xxx"
        )
    except Exception as e:
        print(f"[Error] Failed to call the LLM: {e}")
        return

    print("\n[Answer] RAG-style answer:\n")
    print(reply.strip())


if __name__ == "__main__":
    # 你可以把 intent 改成 "learning_planning" 体验学习场景
    run_rag_demo(intent="health_tracking")


