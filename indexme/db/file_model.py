import os
from typing import Any, cast

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from indexme.db.connection import Base


class File(Base):
    """
    An indexed file or directory.
    """

    __tablename__ = "files"

    path: Any = Column(String, primary_key=True)
    name: Any = Column(String, nullable=False, index=True)
    is_dir: Any = Column(Boolean, nullable=False)
    is_executable: Any = Column(Boolean, nullable=False)
    is_suid: Any = Column(Boolean, nullable=False)
    size: Any = Column(Integer, nullable=False)
    created_at: Any = Column(DateTime, nullable=False)
    modified_at: Any = Column(DateTime, nullable=False)

    def __str__(self) -> str:
        path = os.path.relpath(cast(str, self.path))
        size = "dir" if self.is_dir else format_bytes(cast(int, self.size))
        return f"{path}: {self.name} ({size}, {self.created_at} - {self.modified_at})"


def format_bytes(size: float) -> str:
    """
    Formats byte number to human-readable form.
    Based on https://stackoverflow.com/a/49361727.

    >>> format_bytes(12345.6)
    '12.06 KB'
    """
    power = 1024
    n = 0
    labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {labels[n]}B"
