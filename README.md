# Personal AI Life & Work Assistant

这是一个**个人 AI 助手**项目，聚焦三个核心能力：

- **RAG（检索增强生成）**：结合轻量规则知识库 + 向量库（Chroma + sentence-transformers）+ 用户长期画像。
- **多 Agent 场景切换**：根据意图在学习 / 工作 / 生活 / 通用等 Agent 间自动切换。
- **对话模式 + 长期记忆**：支持多轮自然对话，并将对话存入 SQLite 知识库，用于后续更个性化的回答。

当前你主要以 **聊天模式（chat mode）** 使用本项目。

## 功能概览

- **两段式 Orchestrator（设计 → 执行）**
  - 设计：`json_prompt_generator.py` 生成结构化 JSON Prompt，包括角色、任务描述、输出要求、约束等。
  - 执行：`orchestrator.py` 将 JSON Prompt 编译成自然语言提示，调用大模型（通过 SiliconFlow/DeepSeek），生成最终回答。

- **多意图与多任务**
  - `intent_parser.py` 对用户输入进行多意图解析，必要时可以拆分为多个子任务（目前聊天主流程使用轻量意图分析）。
  - 支持多任务设计与执行，并聚合结果（用于日程规划等场景）。

- **RAG 与长期记忆**
  - `light_rag.py`：基于规则/关键词的轻量知识检索，用于健康/学习等常识场景。
  - `retrieval_system.py`：整合向量检索（Chroma + sentence-transformers）、偏好、上下文的多策略检索。
  - `knowledge_base.py`：使用 SQLite 存储：
    - 每轮对话的 `session_id / user_input / ai_response / intent / topic / timestamp`。
    - 用户偏好（常见意图、频率、偏好分数）。
    - 行为模式（如常在早上/下午/晚上聊天、话题切换模式等）。
  - Orchestrator 在回答前，会把“用户画像摘要 + 轻量知识 + 向量检索结果”合并成 `rag_knowledge` 注入 Prompt。

- **多 Agent 架构**
  - `agents.py` 定义多个 Agent 画像，例如：
    - `StudyAgent`：学习规划/方法论教练。
    - `WorkAgent`：工作任务/效率助手。
    - `LifeAgent`：生活习惯/情绪支持助手。
    - `GeneralAgent`：通用聊天与问答。
  - `select_agent_by_intent(intent)` 根据当前意图选择合适的 Agent，并把 Agent 信息写入 JSON Prompt 的 `agent_profile`，影响模型的 System Prompt。

- **命令行对话模式**
  - `main.py` 提供 `chat_loop`：
    - 每轮读取用户输入，调用 `PromptOrchestrator` + RAG + Agent。
    - 自动检测意图与场景（工作/学习/生活/通用），切换到对应 Agent。
    - 在终端提示当前 Agent 和场景，并将对话写入长期知识库。

## 安装与环境

假设项目克隆或放置在：`C:\ai-projects\Personal-AI-Life-Work-Assistant`

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 关键环境变量

- **模型与 API**
  - `DEEPSEEK_API_KEY`：SiliconFlow / DeepSeek 的 API Key（必须配置，否则执行阶段会退回 mock 模式）。
  - `MODEL`：可选，自定义模型名称（默认：`Qwen/Qwen2.5-7B-Instruct`）。

- **运行模式**
  - `AIPS_MODE`：
    - `demo`（默认）→ 运行原有 Demo 演示（基础 Prompt + Orchestrator 示例）。
    - `chat` → 进入命令行聊天模式（推荐你日常使用）。
  - `AIPS_NO_INTERACTIVE`：
    - `1/true/yes` → 禁用命令行交互（用于自动化环境）。
    - 其它/未设置 → 允许交互。

- **其它**
  - `AIPS_OUTPUT`：`text` | `json`，控制 Demo 输出格式（对 chat 模式影响不大）。
  - `AIPS_SESSION_ID`：可选，用于区分不同会话的长期记忆（默认：`cli_session`）。

## 如何运行聊天模式

在 PowerShell 中（Windows 示例）：

```powershell
cd C:\ai-projects\Personal-AI-Life-Work-Assistant

# 激活虚拟环境（如果有）
.\.venv\Scripts\activate

# 设置环境变量并启动聊天模式
$env:AIPS_MODE="chat"
$env:AIPS_NO_INTERACTIVE="0"
python main.py
```

进入后，你会看到类似提示：

- `个人 AI 助手（对话模式）`
- `输入内容开始对话，输入 exit / quit 退出。`

每轮回答前，会显示当前 Agent 状态，例如：

```text
[Agent: WorkAgent | Scene: work | Intent: work_task]
Assistant:
...
```

你可以自由说：工作、学习、生活相关的问题，系统会自动切换到对应 Agent。

## 两段式 Orchestrator 与多任务

详见 `orchestrator.py`：

- **核心方法**
  - `design_prompt(ctx)` / `execute_prompt(json_prompt)`
  - `generate_and_respond(ctx)`：单任务完整链路（设计 → 执行）。
  - `design_prompts_multi` / `execute_prompts_multi` / `generate_and_respond_multi`：多意图 → 多任务链路。
  - `generate_and_respond_with_light_rag(ctx, intent)`：带 RAG + Agent 的主流程。

- **意图与场景分析**
  - `analyze_intent_and_scene(user_input, previous_scene)`：
    - 调用 `parse_multi_intent` 分析意图片段。
    - 提取主意图 `intent` 与主话题 `primary_topic`。
    - 补全 `understanding["life_context"]["topic_analysis"]`，用于行为模式分析和长期记忆。

## 知识库与用户画像

- `knowledge_base.py`：
  - `store_conversation(session_id, user_input, ai_response, understanding)`
    - 保存每轮对话及意图、话题、置信度等。
    - 在同一事务中更新用户偏好和行为模式（时间偏好/话题切换）。
  - `get_knowledge_summary(session_id)`
    - 返回该会话的对话数、意图分布、话题分布、偏好、行为模式等。
  - `get_user_profile_summary_text(session_id)`
    - 将上述结构转为一段简短的用户画像描述：
      - 常见意图与话题。
      - 常用时间段（早上/下午/晚上聊天）。
      - 主要行为模式类型列表。
    - 这段文本会被 Orchestrator 作为 RAG 上下文的一部分注入模型。

## 开发与调试建议

- **代码入口**
  - 核心入口：`main.py` → `AIPromptSystem.run()`。
  - 聊天模式主要看：`AIPromptSystem.chat_loop()`。

- **查看长期记忆效果**
  - 与助手多聊几轮后，可以在代码中调用：
    - `knowledge_base.get_knowledge_summary(session_id)`
    - `knowledge_base.get_user_profile_summary_text(session_id)`
  - 或者在未来加一个 `/profile` 命令，把当前画像打印出来。

## 许可证

MIT
