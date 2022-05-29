from typing import Tuple, List
from datetime import datetime
from browser_history import get_history, get_bookmarks


def get_browser_info() -> List[Tuple[datetime, str]]:
    return get_history().histories


def history_to_str(hist: Tuple[datetime, str]):
    t, site = hist
    return f"{t.strftime('%d.%m.%Y %H:%M:%S')}, {site}"


def list_of_history_to_str(history_list: List[Tuple[datetime, str]]) -> str:
    msg = ""
    for history in history_list:
        msg += history_to_str(history) + "\n"
    return msg
