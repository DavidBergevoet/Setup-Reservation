from datetime import datetime, timedelta

DATETIME_FORMAT = '%Y-%m-%d %H:%M'

def floor_datetime(datetime):
    return datetime - timedelta(seconds = datetime.second, microseconds = datetime.microsecond)