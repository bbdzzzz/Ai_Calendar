---
alwaysApply: true
---
# AI语音日历系统 - 项目规则

## 项目概述
基于自然语言语音交互的智能日历系统。用户通过语音或文字下达指令，后端ASR转文字后交由AI Agent解析，Agent生成日程配置及文字回复，后端将行程同步至数据库，并通过TTS将文字转码为语音流推回前端播放。

## 技术栈
- **后端**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2, WebSocket
- **前端**: Flutter (Dart), GetX, Dio, WebSocket, Hive, table_calendar, record, audioplayers
- **数据库**: MySQL (Docker, localhost:3306, root/123456, 库名 ai_calendar)
- **ASR**: FunASR paraformer-zh-streaming
- **TTS**: edge-tts
- **LLM**: DeepSeek (deepseek-v4-flash), OpenAI兼容接口, ReAct + Function Calling
- **包管理**: uv (pyproject.toml)

## 项目结构
```
c:\xm\Ai_Calendar\
├── main.py                    # FastAPI入口, uvicorn启动
├── pyproject.toml             # uv依赖管理
├── .env                       # 环境变量 (LLM_API_KEY等, 已加入.gitignore)
├── .gitignore
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
│   │   └── agent.py           # AgentInput, AgentAction (含new_messages)
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
│   │   ├── adapter.py         # ReAct循环主控 (run函数, 工具调用循环, 输出解析)
│   │   ├── prompts.py         # 动态System Prompt拼接 + build_agent_input + build_messages
│   │   ├── llm_client.py      # LLM抽象层 (AsyncOpenAI, 自动拼接/v1)
│   │   ├── tools.py           # 4个工具的JSON Schema定义
│   │   └── tool_executor.py   # 工具执行器 (本地业务逻辑: CRUD + 冲突检测)
│   ├── websocket/
│   │   └── handler.py         # WSHandler 信令状态机 (集成Agent, 保存tool_calls到对话, 支持文字消息)
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
│   ├── test_11_agent_tools.py    # Agent工具定义验证
│   ├── test_12_tool_executor.py  # 工具执行器(CRUD+冲突检测, 需MySQL)
│   ├── test_13_agent_prompts.py  # Prompt构建与消息列表
│   ├── test_14_agent_llm.py      # LLM客户端初始化与真实调用(需API Key)
│   ├── test_15_agent_react.py    # 完整ReAct流程(需MySQL+API Key)
│   └── run_all_tests.py
└── ai_calendar_app/           # Flutter前端
    ├── lib/
    │   ├── main.dart                  # 应用入口, 服务注入, 路由初始化
    │   ├── app/
    │   │   ├── routes/app_routes.dart # GetX路由定义 (6条路由)
    │   │   └── theme/app_theme.dart   # Material 3 主题 (light/dark)
    │   ├── models/
    │   │   ├── user.dart              # AppUser模型
    │   │   ├── event.dart             # CalendarEvent模型 (含copyWith)
    │   │   ├── conversation.dart      # ChatMessage模型
    │   │   └── report.dart            # Report模型
    │   ├── services/
    │   │   ├── api_service.dart       # Dio封装, JWT拦截器, 401自动跳转, 全部REST端点
    │   │   ├── ws_service.dart        # WebSocket连接管理, JSON信令, 二进制音频, 文字消息
    │   │   ├── audio_recorder.dart    # PCM 16kHz流式录音 → WebSocket
    │   │   ├── audio_player.dart      # MP3分块缓冲 + 播放
    │   │   └── local_db.dart          # Hive本地存储 (token/userId/serverUrl)
    │   ├── controllers/
    │   │   ├── user_ctrl.dart         # 登录/注册/登出, JWT持久化, WS自动连接
    │   │   ├── calendar_ctrl.dart     # 事件加载/创建/更新/删除, 日期选择, 事件确认
    │   │   ├── assistant_ctrl.dart    # 4态状态机(idle→recording→processing→speaking), 语音+文字输入
    │   │   └── report_ctrl.dart       # 周报列表加载, 类型切换, 详情查看
    │   └── views/
    │       ├── auth/login_page.dart           # 登录/注册切换, 表单验证
    │       ├── home_page.dart                 # 底部导航(日历+周报+我的) + 助手悬浮层
    │       ├── calendar/
    │       │   ├── calendar_page.dart         # TableCalendar, 事件列表, 分类色标, FAB创建
    │       │   ├── event_detail_page.dart     # 事件详情/编辑 (只读↔编辑切换)
    │       │   └── event_create_page.dart     # 手动创建事件表单
    │       ├── assistant/
    │       │   └── assistant_overlay.dart     # FAB触发, 底部面板, 聊天气泡, 文字+语音输入
    │       ├── report/
    │       │   ├── report_list_page.dart      # 周报列表, 类型切换, 下拉刷新
    │       │   └── report_detail_page.dart    # 周报详情, 统计数据展示
    │       └── profile/
    │           └── profile_page.dart          # 用户信息, 服务器地址设置, 退出登录
    └── test/
        ├── models_test.dart           # 数据模型单元测试 (10个用例)
        ├── local_db_test.dart         # 本地存储单元测试 (4个用例)
        ├── widgets_test.dart          # 主题/路由单元测试 (9个用例)
        └── widget_test.dart           # 占位smoke test
```

## 编码规范

### Python
- 使用 type hints, Mapped[] 风格的 SQLAlchemy 2.x 声明
- Pydantic v2: model_config = {"from_attributes": True} 代替 Config 类
- 异步函数使用 async/await
- 不添加注释除非明确要求
- import 顺序: stdlib → third-party → local (backend.*)
- Session 管理注意: 在 session 关闭前提取所需属性值, 避免 DetachedInstanceError

### Flutter/Dart
- 架构: Service → Controller (GetX) → View, 严格分层
- 状态管理: GetX, 响应式变量用 .obs, UI 用 Obx() 包裹
- 路由: GetX命名路由, 定义在 app_routes.dart
- 主题: Material 3, 统一圆角12px, Card无阴影+边框
- 错误处理: catch 块使用 Get.snackbar 向用户展示错误
- LocalDb 测试: 使用 initForTest() 替代 init() (避免依赖 path_provider 平台通道)

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
- text_message: 文字消息输入 (前端→后端, 走Agent流程)

### Agent模块
- ReAct (Reason + Act) + Function Calling 模式
- 4个工具: query_events, create_event, update_event, delete_event
- 创建/修改前必须先调用query_events检查冲突
- 死循环保护: 最大5轮工具调用 (LLM_MAX_TOOL_ROUNDS)
- DeepSeek推理模型需保留reasoning_content回传
- LLM抽象化: 通过LLM_BASE_URL+LLM_MODEL切换模型

### 上下文管理 (三层防护)
1. **时间窗口过滤**: 只加载最近N分钟的对话记录 (LLM_HISTORY_WINDOW_MINUTES=30)
2. **字符预算截断**: 历史消息超过LLM_MAX_HISTORY_CHARS时, 从最旧消息开始丢弃, tool_calls与tool消息成对丢弃
3. **溢出紧急截断**: LLM API返回context_length错误时, 自动砍掉一半历史重试, 仅重试一次

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

### 后端测试
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

# 需要MySQL的测试
uv run python tests/test_12_tool_executor.py

# 需要MySQL + LLM API Key的测试
uv run python tests/test_15_agent_react.py

# 需要服务器运行的测试 (先启动 uv run python main.py)
uv run python tests/test_03_auth_api.py
uv run python tests/test_04_events_api.py
uv run python tests/test_08_websocket.py
uv run python tests/test_10_health.py

# 一键全量测试
uv run python tests/run_all_tests.py
```

### 前端测试
```bash
cd ai_calendar_app

# 静态分析
flutter analyze

# 运行全部测试
flutter test

# 运行单个测试文件
flutter test test/models_test.dart
flutter test test/local_db_test.dart
flutter test test/widgets_test.dart
```

### 依赖管理
```bash
# 后端
uv sync          # 同步依赖
uv add <pkg>     # 添加依赖

# 前端
cd ai_calendar_app
flutter pub get  # 同步依赖
flutter pub add <pkg>  # 添加依赖
```

## 环境变量 (.env)
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

## 关键设计决策
1. **密码哈希**: 使用 bcrypt 直接调用 (非 passlib, 因 passlib 与新版 bcrypt 不兼容)
2. **JWT**: HS256 算法, SECRET_KEY 在 config.py 中配置, 支持通过 .env 覆盖
3. **冲突检测**: 区间重叠算法 S1 < E2 AND S2 < E1, 冲突时自动设为 tentative
4. **Agent**: ReAct + Function Calling 模式, DeepSeek推理模型, 工具调用循环最大5轮
5. **ASR**: FunASR paraformer-zh-streaming, 接收PCM 16kHz 16bit音频流
6. **TTS**: edge-tts, 默认语音 zh-CN-XiaoxiaoNeural, 流式返回MP3分块
7. **周报**: APScheduler 每周日晚23:00触发, 统计分类占比和会议时长
8. **LLM抽象化**: llm_client.py 封装AsyncOpenAI, 自动拼接/v1, 切换模型只需改.env
9. **上下文管理**: 三层防护 - 时间窗口(30分钟) + 字符预算截断(8000字符) + 溢出紧急截断(砍半重试)
10. **前端架构**: GetX分层(Service→Controller→View), 助手4态状态机, 语音+文字双输入
11. **文字消息**: WebSocket新增text_message信令, 前端文字输入走与语音相同的Agent流程
12. **平台权限**: Android minSdk=24, RECORD_AUDIO权限; iOS NSMicrophoneUsageDescription

## 注意事项
- 修改模型后需重启服务 (init_db 会自动建表, 但不会自动迁移)
- WebSocket 端点 /ws/{user_id} 暂无JWT认证, 后续需加强
- .env 文件包含敏感信息(LLM_API_KEY), 已加入.gitignore, 不可提交到仓库
- DeepSeek推理模型(deepseek-v4-flash)返回reasoning_content, 必须在后续调用中原样传回
- Agent adapter.py 的 run() 是核心入口, 保持 AgentInput/AgentAction 接口不变
- 前端 LocalDb 测试使用 initForTest() 而非 init(), 避免依赖平台通道
- 前端 Android minSdk 固定为24 (record库最低要求), 不可使用 flutter.minSdkVersion
