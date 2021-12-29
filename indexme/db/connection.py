from typing import TYPE_CHECKING, Any, Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker
from xdg import xdg_config_home


if TYPE_CHECKING:
    Base = Any
else:
    Base = declarative_base()


def get_db_str() -> str:
    return f"sqlite:///{xdg_config_home()}/indexme.sqlite3"


DB_STRING_FACTORY: Callable[[], str] = get_db_str


def connect() -> sessionmaker:
    engine = create_engine(DB_STRING_FACTORY())
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
