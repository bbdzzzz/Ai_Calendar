import logging

import uvicorn
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.api.deps import get_current_user
from backend.api.v1 import auth, events, reports
from backend.core.config import settings
from backend.core.database import init_db
from backend.models.models import User
from backend.scheduler.report_cron import start_scheduler
from backend.websocket.handler import WSHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI语音日历系统", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()
    logger.info("AI语音日历系统启动完成")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    handler = WSHandler(websocket, user_id)
    await handler.run()


def main():
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)


if __name__ == "__main__":
    main()
