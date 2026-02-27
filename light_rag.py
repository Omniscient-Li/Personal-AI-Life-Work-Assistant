#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight, in-memory RAG utilities.

This module provides:
- A tiny built-in "knowledge base" (health / learning tips)
- A simple keyword-based retrieval function
- A formatter that turns retrieved snippets into prompt text

It is designed to be dependency-free so it can be used both in:
- standalone demos (e.g. rag_demo.py)
- the main orchestrator / agent pipeline as a fallback RAG mechanism
"""

from typing import Dict, Any, List


# Simple built-in "knowledge base" to replace a real vector DB,
# so you can quickly experience a RAG-like idea in any environment.
HEALTH_KNOWLEDGE: List[str] = [
    "Do at least 30 minutes of moderate-intensity exercise every day, such as brisk walking, jogging, or cycling, to support cardiovascular health.",
    "Aim for 7 to 9 hours of quality sleep each night to help your body recover and stabilize your mood.",
    "Eat more vegetables, fruits, whole grains, and high-quality protein, and reduce high-sugar, high-fat processed foods to significantly improve your health.",
    "Prolonged sitting increases the risk of cardiovascular disease and obesity; try to stand up and move for at least 5 minutes every hour of work.",
]

LEARNING_KNOWLEDGE: List[str] = [
    "When designing a study plan, you can use the Pomodoro Technique: focus for 25 minutes, rest for 5 minutes, and take a longer break after 4 pomodoros.",
    "To systematically learn a new technology, you can follow this path: understand the concepts → follow tutorials to build small projects → read the official documentation → build a medium-sized project on your own.",
    "Regular review (e.g., after 1 day, 3 days, 7 days, and 14 days) can significantly improve long-term memory, a method known as spaced repetition.",
    "When taking notes, prioritize writing down your own summaries and key examples instead of mechanically copying slides or textbooks.",
]


def simple_retrieve(user_input: str, intent: str) -> List[Dict[str, Any]]:
    """
    Very simple retrieval over the built-in health / learning knowledge.

    Scoring rule:
    - Count how many intent-dependent keywords hit either the user input
      or the document text (case-insensitive)
    - Return documents with score > 0, sorted by score desc
    """
    if intent == "learning_planning":
        docs = LEARNING_KNOWLEDGE
        knowledge_type = "learning_knowledge"
        keywords = ["study", "course", "review", "efficient", "plan", "pomodoro", "project"]
    else:
        docs = HEALTH_KNOWLEDGE
        knowledge_type = "health_knowledge"
        keywords = ["health", "exercise", "sleep", "diet", "sitting", "workout", "schedule"]

    results: List[Dict[str, Any]] = []
    text_lower = user_input.lower()
    for doc in docs:
        score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in doc.lower() or kw_lower in text_lower:
                score += 1
        if score > 0:
            results.append(
                {"document": doc, "knowledge_type": knowledge_type, "final_score": float(score)}
            )

    # sort by score descending
    results.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
    return results


def format_knowledge_snippets(top_results: List[Dict[str, Any]], max_snippets: int = 3) -> str:
    """
    Format retrieval results into text suitable for putting into an LLM prompt.
    """
    lines: List[str] = []
    for i, item in enumerate(top_results[:max_snippets], start=1):
        doc = item.get("document", "").strip()
        source = item.get("knowledge_type", "unknown")
        score = item.get("final_score", 0.0)
        if not doc:
            continue
        lines.append(f"{i}. [source={source}, score={score:.3f}] {doc}")
    if not lines:
        return "No relevant knowledge was retrieved; please answer based on general knowledge and clearly state the limitations."
    return "\n".join(lines)



