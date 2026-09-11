from datetime import datetime
import json


def get_datetime(args: dict, **kwargs) -> str:
    """Get the current date, time, and timezone from the Windows PC."""

    include_timezone = args.get("include_timezone", True)

    now = datetime.now().astimezone()

    result = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": now.tzname(),
        "utc_offset": now.strftime("%z"),
    }

    if not include_timezone:
        result.pop("timezone")
        result.pop("utc_offset")

    return json.dumps(result)