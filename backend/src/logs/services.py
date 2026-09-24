from sqlmodel import Session

from src.logs.models import ActivitiesLog
from src.logs.schemas import ActivityLogCreate


def create_activity_log(data: ActivityLogCreate, session: Session) -> None:
    activity_log = ActivitiesLog(
        event=data.event,
        data=data.data,
        user_id=data.user_id,
    )

    session.add(activity_log)
    session.commit()
