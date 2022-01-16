from typing import Callable

from xdg import xdg_config_home, xdg_data_home


def default_ignore_path() -> str:
    """
    Default ignore path factory.
    Usually ~/.config/indexme.ignore.
    """
    return f"{xdg_config_home()}/indexme.ignore"


def default_db_str() -> str:
    """
    Default db_string factory.
    Usually sqlite:///~/.local/share/indexme.sqlite3.
    """
    return f"sqlite:///{xdg_data_home()}/indexme.sqlite3"


_IGNORE_PATH_FACTORY: Callable[[], str] = default_ignore_path
_DB_STRING_FACTORY: Callable[[], str] = default_db_str


def get_ignore_path() -> str:
    """
    Gets a current ignore path.
    """
    return _IGNORE_PATH_FACTORY()


def set_ignore_path_factory(factory: Callable[[], str]) -> None:
    """
    Sets a new ignore path factory.
    """
    global _IGNORE_PATH_FACTORY
    _IGNORE_PATH_FACTORY = factory


def get_db_string() -> str:
    """
    Gets a current db_string.
    """
    return _DB_STRING_FACTORY()


def set_db_string_factory(factory: Callable[[], str]) -> None:
    """
    Sets a new db_string factory.
    """
    global _DB_STRING_FACTORY
    _DB_STRING_FACTORY = factory
