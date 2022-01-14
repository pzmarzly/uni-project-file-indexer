from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker

from indexme.db.paths import get_db_string

if TYPE_CHECKING:
    Base = Any
else:
    Base = declarative_base()


def connect() -> sessionmaker:
    engine = create_engine(get_db_string())
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
