from typing import Callable
from xdg import xdg_data_home, xdg_config_home


def _get_ignore_path() -> str:
    return f"{xdg_config_home()}/indexme.ignore"


def _get_db_str() -> str:
    return f"sqlite:///{xdg_data_home()}/indexme.sqlite3"


IGNORE_PATH_FACTORY: Callable[[], str] = _get_ignore_path
DB_STRING_FACTORY: Callable[[], str] = _get_db_str


def get_ignore_path() -> str:
    return IGNORE_PATH_FACTORY()


def get_db_string() -> str:
    return DB_STRING_FACTORY()
