import os
import json
from ai_prompt_generator import AIPromptGenerator, PromptContext


def test_generate_prompt_structured_mock(monkeypatch):
    # 确保走 mock
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('AZURE_OPENAI_API_KEY', raising=False)

    gen = AIPromptGenerator()
    ctx = PromptContext(
        task_type='health_advice',
        user_input='我想提高睡眠质量',
        conversation_history=[],
        user_profile={'age': 28, 'occupation': '工程师'},
        current_goals=['改善睡眠'],
        mood_state='压力较大'
    )
    res = gen.generate_prompt_structured(ctx)
    assert res['success'] is True
    assert 'data' in res and isinstance(res['data'], dict)
    assert 'prompt_text' in res['data']
    assert res['meta']['mode'] in ('mock', 'ai')


def test_json_prompt_generator_dict():
    from json_prompt_generator import JSONPromptGenerator, PromptContext as JCtx
    gen = JSONPromptGenerator()
    ctx = JCtx(
        task_type='schedule_assistant',
        user_input='明天有会议',
        conversation_history=[],
        user_profile={},
        current_goals=['合理安排时间'],
        mood_state='正常'
    )
    res = gen.generate_json_prompt(ctx)
    assert res['success'] is True
    assert 'data' in res and isinstance(res['data'], dict)
    assert 'role' in res['data']
