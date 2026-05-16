import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.models import Event, Report, User

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _generate_weekly_report(db: Session, user: User, start: date, end: date) -> dict:
    events = (
        db.query(Event)
        .filter(
            Event.user_id == user.id,
            Event.start_time >= start,
            Event.start_time < end,
        )
        .all()
    )

    category_stats = {}
    total_minutes = 0
    for e in events:
        duration = (e.end_time - e.start_time).total_seconds() / 60
        total_minutes += duration
        category_stats[e.category] = category_stats.get(e.category, 0) + duration

    statistics = {
        "total_events": len(events),
        "total_minutes": total_minutes,
        "category_breakdown": category_stats,
    }

    summary_lines = [f"# {user.username} 周报 ({start} ~ {end})\n"]
    summary_lines.append(f"- 本周共 {len(events)} 项行程")
    summary_lines.append(f"- 总时长 {total_minutes:.0f} 分钟")
    for cat, mins in category_stats.items():
        summary_lines.append(f"- {cat}: {mins:.0f} 分钟")

    summary = "\n".join(summary_lines)
    return {"summary": summary, "statistics": statistics}


async def weekly_report_job():
    logger.info("开始生成周报...")
    db = SessionLocal()
    try:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=7)

        users = db.query(User).all()
        for user in users:
            existing = db.query(Report).filter(
                Report.user_id == user.id,
                Report.report_type == "weekly",
                Report.start_date == start_of_week,
            ).first()
            if existing:
                continue

            result = _generate_weekly_report(db, user, start_of_week, end_of_week)
            report = Report(
                user_id=user.id,
                report_type="weekly",
                start_date=start_of_week,
                end_date=end_of_week,
                summary=result["summary"],
                statistics=result["statistics"],
            )
            db.add(report)
        db.commit()
    finally:
        db.close()
    logger.info("周报生成完成")


def start_scheduler():
    scheduler.add_job(weekly_report_job, "cron", day_of_week="sun", hour=23, minute=0, id="weekly_report")
    scheduler.start()
    logger.info("定时任务调度器已启动")
