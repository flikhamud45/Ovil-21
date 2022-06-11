from typing import Tuple, List
from datetime import datetime
from browser_history import get_history, get_bookmarks


def get_browser_info() -> List[Tuple[datetime, str]]:
    """
    Returns the browser history.
    Returns a list of tuples. Each tuple contains a datetime object and the url of the website (str).
    """
    return get_history().histories


def history_to_str(hist: Tuple[datetime, str]):
    """
    Gets an history entity and concert this to str
    """
    t, site = hist
    return f"{t.strftime('%d.%m.%Y %H:%M:%S')}, {site}"


def list_of_history_to_str(history_list: List[Tuple[datetime, str]]) -> str:
    """
    gets a list of history entities and concert this to str
    """
    msg = ""
    for history in history_list:
        msg += history_to_str(history) + "\n"
    return msg
