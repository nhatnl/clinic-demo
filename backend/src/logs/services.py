from src.logs.models import ActivitiesLog
from src.logs.schemas import ActivityLogCreate


def create_activity_log(data: ActivityLogCreate, session)->None:
    activity_log = ActivitiesLog(
        event=data.event,
        data=data.data
    )

    session.add(activity_log)
    session.commit()
