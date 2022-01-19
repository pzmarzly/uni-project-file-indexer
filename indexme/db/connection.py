from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker

from indexme.db.paths import get_db_string

if TYPE_CHECKING:

    class Base:
        metadata: Any

        def __init__(self, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
            pass

else:
    Base = declarative_base()


def connect() -> sessionmaker:
    """
    Connects to a database according to current db_string.
    """
    engine = create_engine(get_db_string(), isolation_level="AUTOCOMMIT")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
