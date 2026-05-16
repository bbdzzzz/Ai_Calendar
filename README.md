# AI语音日历系统

基于自然语言语音交互的智能日历系统。用户通过语音或文字下达指令，后端 ASR 转文字后交由 AI Agent 解析，Agent 生成日程配置及文字回复，后端将行程同步至数据库，并通过 TTS 将文字转码为语音流推回前端播放。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Flutter (Dart), GetX, Dio, WebSocket, Hive, table_calendar, record, audioplayers |
| 后端 | Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2, WebSocket |
| 数据库 | MySQL (Docker) |
| ASR | FunASR paraformer-zh-streaming |
| TTS | edge-tts (zh-CN-XiaoxiaoNeural) |
| LLM | DeepSeek (deepseek-v4-flash), OpenAI 兼容接口, ReAct + Function Calling |
| 包管理 | uv (后端), pub (前端) |

## 系统架构

系统采用 **RESTful + WebSocket** 双协议通信：

- **RESTful (Dio)**：负责常规 CRUD、登录、获取周报等无状态请求
- **WebSocket (WS)**：负责语音流上传、ASR 结果流式返回、Agent 文本/音频流式返回、行程实时推送

```
┌──────────┐   PCM Audio    ┌──────────┐   PCM Stream   ┌─────────┐
│  Flutter  │ ────────────── │  FastAPI  │ ────────────── │  FunASR  │
│  Frontend │ ◄──────────── │  Backend  │ ◄──────────── │  (ASR)   │
└──────────┘   TTS Audio    └──────────┘   Text          └─────────┘
     │              ▲             │
     │   JSON/Binary (WS)        │  Agent Input
     └──────────────────────────┘
                        │
                  ┌─────┴─────┐
                  │ AI Agent  │ ◄── DeepSeek LLM
                  │ (ReAct)   │ ──► Tool Calls
                  └─────┬─────┘
                        │
                  ┌─────┴─────┐
                  │   MySQL   │
                  │  Database │
                  └───────────┘
```

## 项目结构

```
c:\xm\Ai_Calendar\
├── main.py                    # FastAPI 入口, uvicorn 启动
├── pyproject.toml             # uv 依赖管理
├── .env                       # 环境变量 (已加入 .gitignore)
├── .gitignore
├── 开发文档                    # 完整开发规范文档
├── backend/
│   ├── core/
│   │   ├── config.py          # Settings (pydantic-settings, 支持 .env)
│   │   ├── database.py        # engine, SessionLocal, Base, init_db()
│   │   └── security.py        # bcrypt 密码哈希, JWT (python-jose)
│   ├── models/
│   │   └── models.py          # User, Event, Conversation, Report (SQLAlchemy ORM)
│   ├── schemas/
│   │   ├── auth.py            # UserRegister, UserLogin, TokenResponse, UserOut
│   │   ├── event.py           # EventCreate, EventUpdate, EventOut, EventUpsertWS, EventConfirmWS
│   │   ├── report.py          # ReportOut, ReportQuery
│   │   └── agent.py           # AgentInput, AgentAction
│   ├── api/
│   │   ├── deps.py            # get_current_user (JWT Bearer 认证依赖)
│   │   └── v1/
│   │       ├── auth.py        # /api/v1/auth/register, /login, /me
│   │       ├── events.py      # /api/v1/events CRUD + 筛选
│   │       └── reports.py     # /api/v1/reports 列表与详情
│   ├── services/
│   │   ├── asr_service.py     # FunASR 流式 ASR
│   │   ├── tts_service.py     # edge-tts 流式 TTS
│   │   └── event_engine.py    # 区间重叠冲突检测
│   ├── agent/
│   │   ├── adapter.py         # ReAct 循环主控
│   │   ├── prompts.py         # 动态 System Prompt 拼接
│   │   ├── llm_client.py      # LLM 抽象层 (AsyncOpenAI)
│   │   ├── tools.py           # 4 个工具的 JSON Schema 定义
│   │   └── tool_executor.py   # 工具执行器 (CRUD + 冲突检测)
│   ├── websocket/
│   │   └── handler.py         # WSHandler 信令状态机
│   └── scheduler/
│       └── report_cron.py     # APScheduler 周报定时生成
├── tests/                     # 各模块独立测试脚本 (15 个)
└── ai_calendar_app/           # Flutter 前端
    └── lib/
        ├── main.dart
        ├── app/routes/        # GetX 路由
        ├── app/theme/         # Material 3 主题
        ├── models/            # 数据模型
        ├── services/          # API / WS / 录音 / 播放 / 本地存储
        ├── controllers/       # GetX 业务逻辑
        └── views/             # UI 界面
```

## 快速开始

### 环境要求

- Python 3.11+
- Flutter SDK (Dart ^3.11.5)
- Docker (MySQL)
- uv (Python 包管理)

### 1. 数据库

```bash
docker run -d --name mysql-dev -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:latest
docker exec mysql-dev mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS ai_calendar;"
```

### 2. 后端

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY 等配置

# 启动服务
uv run python main.py
```

服务地址: http://localhost:8000
API 文档: http://localhost:8000/docs

### 3. 前端

```bash
cd ai_calendar_app
flutter pub get
flutter run
```

## 环境变量

在项目根目录创建 `.env` 文件：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/ai_calendar
SECRET_KEY=ai-calendar-secret-key-change-in-production
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
LLM_MAX_TOOL_ROUNDS=5
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1024
LLM_HISTORY_WINDOW_MINUTES=30
LLM_MAX_HISTORY_CHARS=8000
```

## WebSocket 信令格式

前后端及 AI 交互严格遵守以下 JSON 信令规范：

| 方向 | type | 说明 |
|------|------|------|
| 前端→后端 | `audio_start` | 开始录音 (含 format, sample_rate) |
| 前端→后端 | Binary Frame | 录音二进制数据 |
| 前端→后端 | `audio_end` | 结束录音 |
| 前端→后端 | `text_message` | 文字消息输入 |
| 后端→前端 | `asr_partial` | ASR 中间识别结果 |
| 后端→前端 | `asr_final` | ASR 最终识别结果 |
| 后端→前端 | `agent_text_delta` | Agent 文本回复 (流式) |
| 后端→前端 | Binary Frame | Agent 音频回复 (流式) |
| 后端→前端 | `agent_audio_done` | Agent 音频结束标识 |
| 后端→前端 | `event_upsert` | Agent 发起行程配置 |
| 前端→后端 | `event_confirm` | 用户确认/修改行程 |

## 数据库设计

| 表 | 说明 |
|----|------|
| `users` | 用户表 (username, password_hash, preferences) |
| `events` | 行程表 (title, start_time, end_time, location, category, priority, status, source) |
| `conversations` | 对话记录表 (role, content, tool_calls) |
| `reports` | 报告表 (report_type, start_date, end_date, summary, statistics) |

## AI Agent

Agent 采用 **ReAct (Reason + Act) + Function Calling** 模式，提供 4 个工具：

| 工具 | 说明 |
|------|------|
| `query_events` | 查询日程 (创建/修改前必须先调用以检查冲突) |
| `create_event` | 创建日程 |
| `update_event` | 修改日程 |
| `delete_event` | 删除日程 |

上下文管理采用三层防护：
1. **时间窗口过滤**：只加载最近 30 分钟的对话记录
2. **字符预算截断**：历史消息超过 8000 字符时从最旧消息开始丢弃
3. **溢出紧急截断**：LLM API 返回 context_length 错误时自动砍掉一半历史重试

## 关键设计决策

- **密码哈希**：使用 bcrypt 直接调用 (非 passlib, 因 passlib 与新版 bcrypt 不兼容)
- **JWT**：HS256 算法, SECRET_KEY 支持通过 .env 覆盖
- **冲突检测**：区间重叠算法 `S1 < E2 AND S2 < E1`, 冲突时自动设为 tentative
- **Agent 死循环保护**：最大 5 轮工具调用
- **DeepSeek 推理模型**：返回 reasoning_content, 必须在后续调用中原样传回
- **LLM 抽象化**：通过 LLM_BASE_URL + LLM_MODEL 切换模型
- **周报生成**：APScheduler 每周日晚 23:00 触发
- **前端助手**：4 态状态机 (idle → recording → processing → speaking)
- **Android minSdk**：固定为 24 (record 库最低要求)

## 测试

### 后端

```bash
# 无需服务器的测试
uv run python tests/test_01_database.py
uv run python tests/test_02_security.py
uv run python tests/test_05_event_engine.py
uv run python tests/test_06_tts.py
uv run python tests/test_07_agent.py
uv run python tests/test_09_report.py
uv run python tests/test_11_agent_tools.py
uv run python tests/test_13_agent_prompts.py
uv run python tests/test_14_agent_llm.py

# 需要 MySQL 的测试
uv run python tests/test_12_tool_executor.py

# 需要 MySQL + LLM API Key 的测试
uv run python tests/test_15_agent_react.py

# 需要服务器运行的测试 (先启动 uv run python main.py)
uv run python tests/test_03_auth_api.py
uv run python tests/test_04_events_api.py
uv run python tests/test_08_websocket.py
uv run python tests/test_10_health.py

# 一键全量测试
uv run python tests/run_all_tests.py
```

### 前端

```bash
cd ai_calendar_app
flutter analyze
flutter test
```
