import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from ..config import Settings
from ..database import SessionLocal
from ..integrations.notifications import get_notification_provider
from ..models import Reminder, ReminderEvent

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.scheduler.add_job(
            self.process_due_reminders,
            "interval",
            seconds=self.settings.reminder_poll_interval_seconds,
            id="process_due_reminders",
            replace_existing=True,
            max_instances=1,
        )
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def process_due_reminders(self) -> None:
        now = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            reminders = db.scalars(
                select(Reminder).where(Reminder.active.is_(True), Reminder.scheduled_at <= now)
            ).all()
            provider = get_notification_provider(self.settings.notification_provider)
            for reminder in reminders:
                already_sent = db.scalar(
                    select(ReminderEvent.id).where(
                        ReminderEvent.reminder_id == reminder.id,
                        ReminderEvent.scheduled_at == reminder.scheduled_at,
                    )
                )
                if already_sent:
                    continue
                result = provider.send(reminder.user_id, reminder.title)
                db.add(ReminderEvent(
                    reminder_id=reminder.id,
                    scheduled_at=reminder.scheduled_at,
                    status=result.status,
                    message=result.message,
                ))
                if reminder.recurrence:
                    reminder.scheduled_at = self._next_time(reminder.scheduled_at, reminder.recurrence)
                else:
                    reminder.active = False
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Reminder scheduler failed to process due reminders")
        finally:
            db.close()

    @staticmethod
    def _next_time(value: datetime, recurrence: str) -> datetime:
        delta = {"daily": timedelta(days=1), "weekly": timedelta(days=7), "monthly": timedelta(days=30)}.get(recurrence)
        if delta is None:
            raise ValueError(f"Unsupported recurrence: {recurrence}")
        return value + delta
