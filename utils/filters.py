from datetime import datetime


def filter_by_date(msg, date_start=None, date_end=None):
    """Filter message by date range."""
    if not date_start and not date_end:
        return True

    msg_date = msg.date
    if isinstance(msg_date, datetime):
        pass
    else:
        return True

    if date_start:
        if msg_date < date_start:
            return False
    if date_end:
        if msg_date > date_end:
            return False
    return True


def filter_by_type(msg, media_type="all"):
    """Filter message by media type."""
    if media_type == "all":
        return True

    from pyrogram.enums import MessageMediaType

    type_map = {
        "photo": MessageMediaType.PHOTO,
        "video": MessageMediaType.VIDEO,
        "audio": MessageMediaType.AUDIO,
    }

    if media_type in type_map:
        return msg.media == type_map[media_type]
    return True
