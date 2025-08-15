# AI Prompt System

这是一个“JSON 优先”的 Prompt 生成系统：支持生成、评估、优化 Prompt，并且所有核心库函数返回统一的结构化对象（JSON 可序列化）。命令行支持文本/JSON 两种输出模式（由环境变量 `AIPS_OUTPUT` 控制）。此外，内置“两段式（设计→执行）”与“多意图→多任务”编排能力，可将复杂输入自动拆解为多个子任务，分别为每个子任务设计结构化 JSON Prompt 并执行，再聚合成最终回复。

## 设计原则
- 核心库函数只返回结构化对象，展示逻辑由 CLI 决定
- JSON-first：稳定的输出 schema，便于集成与测试
- 配置依赖环境变量（无硬编码密钥）
- 无密钥自动降级为 mock 模式（meta.mode=mock）

## 快速开始
```bash
python -m venv app_env
source app_env/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 如需使用 Azure/OpenAI，请填写密钥

# 文本模式
python main.py

# JSON 模式
AIPS_OUTPUT=json python main.py
```

## 环境变量
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`（默认：2024-02-15-preview）
- `AIPS_OUTPUT`：`text` | `json`

## 两段式与多任务编排（Orchestrator）
- 两段式：
  - 设计（design）：根据上下文产出结构化 JSON Prompt（包含角色、任务描述、所需输出、约束、输出格式等）
  - 执行（execute）：将 JSON Prompt 编译为可执行提示，并生成最终结构化回复（无密钥时为降级示例）
- 多意图→多任务：
  - 解析：`intent_parser.py` 将复杂输入按句切分并识别多意图与轻量实体
  - 多任务设计：`design_prompts_multi` 为每个子句/意图生成独立 JSON Prompt
  - 多任务执行：`execute_prompts_multi` 逐个执行，`_aggregate_results` 聚合生成最终摘要
- 主要接口（见 `orchestrator.py`）：
  - `design_prompt(ctx)`、`execute_prompt(json_prompt)`
  - `design_prompts_multi(user_input, base_ctx)`、`execute_prompts_multi(tasks)`
  - `generate_and_respond(ctx)`、`generate_and_respond_multi(user_input, base_ctx)`

## 运行演示（示例命令）
```bash
# 文本模式（默认）
python main.py

# JSON 模式（推荐用于集成与调试）
AIPS_OUTPUT=json python main.py
```

JSON 模式输出包含以下关键段：
- `type: orchestrator_design`：两段式“设计”阶段产物（JSON Prompt）
- `type: orchestrator_execute`：两段式“执行”阶段产物（最终文本+编译后的提示）
- `type: orchestrator_multi`：多意图→多任务整链路（含 understanding、tasks、executed、final）

## 结构化输出示例
- 生成 Prompt（GeneratedPrompt）
```json
{
  "success": true,
  "data": {
    "prompt_text": "...",
    "confidence_score": 0.86,
    "reasoning": "...",
    "optimization_suggestions": ["..."],
    "context_used": {"task_type": "...", "user_input": "..."}
  },
  "meta": {"mode": "ai|mock", "model": "gpt-4"}
}
```

- 结构化 JSON Prompt（JSONPrompt）
```json
{
  "success": true,
  "data": {
    "role": "time_management_specialist",
    "user_context": {"...": "..."},
    "task_description": "...",
    "required_outputs": [ ... ],
    "constraints": [ ... ],
    "output_format": { ... }
  }
}
```

- 多任务编排结果（节选）
```json
{
  "type": "orchestrator_multi",
  "success": true,
  "data": {
    "designed": { "understanding": { "segments": [ {"text": "明天下午开会", "intent": "schedule_management"} ] }, "tasks": [ ... ] },
    "executed": [ { "task_id": "task_1", "result": { "final_text": "..." } } ],
    "final": { "summary": "...", "count": 3 }
  }
}
```

## Mock 模式说明
- 未配置 `AZURE_OPENAI_*` 时自动进入降级（mock）模式：
  - 仍产出完整的结构化 JSON（`meta.mode=mock`）
  - 执行阶段返回占位但结构化良好的示例文本，便于前后端联调与自动化测试

## 测试
```bash
pytest -q
```

## 许可证
MIT
