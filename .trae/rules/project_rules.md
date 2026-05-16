# AI语音日历系统 - 项目规则

## 项目概述
基于自然语言语音交互的智能日历系统。用户通过语音下达指令，后端ASR转文字后交由AI Agent解析，Agent生成日程配置及文字回复，后端将行程同步至数据库，并通过TTS将文字转码为语音流推回前端播放。

## 技术栈
- **后端**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2, WebSocket
- **前端**: Flutter (Dart), GetX, Dio, WebSocket (暂未开发)
- **数据库**: MySQL (Docker, localhost:3306, root/123456, 库名 ai_calendar)
- **ASR**: FunASR paraformer-zh-streaming
- **TTS**: edge-tts
- **包管理**: uv (pyproject.toml)

## 项目结构
```
c:\xm\Ai_Calendar\
├── main.py                    # FastAPI入口, uvicorn启动
├── pyproject.toml             # uv依赖管理
├── 开发文档                    # 完整开发规范文档
├── backend/
│   ├── core/
│   │   ├── config.py          # Settings (pydantic-settings, 支持.env)
│   │   ├── database.py        # engine, SessionLocal, Base, init_db()
│   │   └── security.py        # bcrypt密码哈希, JWT (python-jose)
│   ├── models/
│   │   └── models.py          # User, Event, Conversation, Report (SQLAlchemy ORM)
│   ├── schemas/
│   │   ├── auth.py            # UserRegister, UserLogin, TokenResponse, UserOut
│   │   ├── event.py           # EventCreate, EventUpdate, EventOut, EventUpsertWS, EventConfirmWS
│   │   ├── report.py          # ReportOut, ReportQuery
│   │   └── agent.py           # AgentInput, AgentAction
│   ├── api/
│   │   ├── deps.py            # get_current_user (JWT Bearer认证依赖)
│   │   └── v1/
│   │       ├── auth.py        # /api/v1/auth/register, /login, /me
│   │       ├── events.py      # /api/v1/events CRUD + 时间/分类/状态筛选
│   │       └── reports.py     # /api/v1/reports 列表与详情
│   ├── services/
│   │   ├── asr_service.py     # FunASR流式ASR (ASRStream, create_stream)
│   │   ├── tts_service.py     # edge-tts流式TTS (stream_tts async generator)
│   │   └── event_engine.py    # 区间重叠冲突检测 (check_conflict)
│   ├── agent/
│   │   ├── adapter.py         # Agent适配器 (当前为桩, 后续接入LLM)
│   │   └── prompts.py         # 构建AgentInput (build_agent_input)
│   ├── websocket/
│   │   └── handler.py         # WSHandler 信令状态机
│   └── scheduler/
│       └── report_cron.py     # APScheduler 周日晚23:00生成周报
├── tests/                     # 各模块独立测试脚本
│   ├── test_01_database.py
│   ├── test_02_security.py
│   ├── test_03_auth_api.py
│   ├── test_04_events_api.py
│   ├── test_05_event_engine.py
│   ├── test_06_tts.py
│   ├── test_07_agent.py
│   ├── test_08_websocket.py
│   ├── test_09_report.py
│   ├── test_10_health.py
│   └── run_all_tests.py
└── ai_calendar_app/           # Flutter前端 (暂未开发)
```

## 编码规范

### Python
- 使用 type hints, Mapped[] 风格的 SQLAlchemy 2.x 声明
- Pydantic v2: model_config = {"from_attributes": True} 代替 Config 类
- 异步函数使用 async/await
- 不添加注释除非明确要求
- import 顺序: stdlib → third-party → local (backend.*)
- Session 管理注意: 在 session 关闭前提取所需属性值, 避免 DetachedInstanceError

### API路由
- RESTful路由挂载在 /api/v1 前缀下
- 认证依赖通过 Depends(get_current_user) 注入
- 响应体使用 Pydantic schema, 设置 response_model

### WebSocket信令格式
严格遵守JSON信令规范:
- audio_start / audio_end / binary: 录音控制
- asr_partial / asr_final: ASR结果
- agent_text_delta / agent_audio_done: Agent回复
- event_upsert / event_confirm: 行程同步

## 常用命令

### 启动服务
```bash
uv run python main.py
```
服务地址: http://localhost:8000
API文档: http://localhost:8000/docs

### 数据库
```bash
# 启动MySQL Docker
docker run -d --name mysql-dev -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:latest
# 创建数据库
docker exec mysql-dev mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS ai_calendar;"
```

### 测试
```bash
# 无需服务器的测试
uv run python tests/test_01_database.py
uv run python tests/test_02_security.py
uv run python tests/test_05_event_engine.py
uv run python tests/test_06_tts.py
uv run python tests/test_07_agent.py
uv run python tests/test_09_report.py

# 需要服务器运行的测试 (先启动 uv run python main.py)
uv run python tests/test_03_auth_api.py
uv run python tests/test_04_events_api.py
uv run python tests/test_08_websocket.py
uv run python tests/test_10_health.py

# 一键全量测试
uv run python tests/run_all_tests.py
```

### 依赖管理
```bash
uv sync          # 同步依赖
uv add <pkg>     # 添加依赖
```

## 关键设计决策
1. **密码哈希**: 使用 bcrypt 直接调用 (非 passlib, 因 passlib 与新版 bcrypt 不兼容)
2. **JWT**: HS256 算法, SECRET_KEY 在 config.py 中配置, 支持通过 .env 覆盖
3. **冲突检测**: 区间重叠算法 S1 < E2 AND S2 < E1, 冲突时自动设为 tentative
4. **Agent**: 当前为桩实现, 返回固定文本回复, 后续接入真实LLM
5. **ASR**: FunASR paraformer-zh-streaming, 接收PCM 16kHz 16bit音频流
6. **TTS**: edge-tts, 默认语音 zh-CN-XiaoxiaoNeural, 流式返回MP3分块
7. **周报**: APScheduler 每周日晚23:00触发, 统计分类占比和会议时长

## 注意事项
- 修改模型后需重启服务 (init_db 会自动建表, 但不会自动迁移)
- WebSocket 端点 /ws/{user_id} 暂无JWT认证, 后续需加强
- Agent adapter.py 是桩代码, 替换时保持 AgentInput/AgentAction 接口不变
- 前端 Flutter 代码在 ai_calendar_app/ 下, 暂未开发
