TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_events",
            "description": "查询指定时间范围内的日程安排。在创建或修改日程前，必须先调用此工具检查是否存在时间冲突。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "查询起始时间，ISO 8601格式，如 2025-05-21T00:00:00",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "查询结束时间，ISO 8601格式，如 2025-05-21T23:59:59",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "创建一个新的日程。请确保先调用query_events检查冲突后再创建。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "日程标题",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "开始时间，ISO 8601格式，如 2025-05-21T15:00:00",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "结束时间，ISO 8601格式，如 2025-05-21T16:00:00",
                    },
                    "location": {
                        "type": "string",
                        "description": "地点，可选",
                    },
                    "category": {
                        "type": "string",
                        "description": "分类：meeting/work/personal/health/other，默认other",
                        "enum": ["meeting", "work", "personal", "health", "other"],
                    },
                    "priority": {
                        "type": "string",
                        "description": "优先级：low/medium/high，默认medium",
                        "enum": ["low", "medium", "high"],
                    },
                    "description": {
                        "type": "string",
                        "description": "日程描述，可选",
                    },
                },
                "required": ["title", "start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "修改已有的日程。只需传入需要修改的字段，未传入的字段保持不变。",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "integer",
                        "description": "要修改的日程ID",
                    },
                    "title": {
                        "type": "string",
                        "description": "新标题，可选",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "新的开始时间，ISO 8601格式，可选",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "新的结束时间，ISO 8601格式，可选",
                    },
                    "location": {
                        "type": "string",
                        "description": "新地点，可选",
                    },
                    "category": {
                        "type": "string",
                        "description": "新分类，可选",
                        "enum": ["meeting", "work", "personal", "health", "other"],
                    },
                    "priority": {
                        "type": "string",
                        "description": "新优先级，可选",
                        "enum": ["low", "medium", "high"],
                    },
                    "status": {
                        "type": "string",
                        "description": "新状态，可选",
                        "enum": ["confirmed", "tentative", "cancelled"],
                    },
                    "description": {
                        "type": "string",
                        "description": "新描述，可选",
                    },
                },
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "删除一个已有的日程。",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "integer",
                        "description": "要删除的日程ID",
                    },
                },
                "required": ["event_id"],
            },
        },
    },
]
