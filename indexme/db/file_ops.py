from datetime import datetime
from enum import IntEnum
import os
from typing import Iterator, Optional, cast
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query

from indexme.db.file_model import File
from indexme.db.stat import Stat


def add_file(s: Session, path: str) -> File:
    path = os.path.abspath(path)
    stat = Stat.get(path)
    entry = s.query(File).filter(File.path == path).one_or_none() or File()
    entry.path = path
    entry.name = os.path.split(path)[1]
    entry.is_dir = stat.is_dir()
    entry.is_executable = stat.is_executable()
    entry.is_suid = stat.is_suid()
    entry.size = stat.size()
    entry.created_at = stat.ctime()
    entry.modified_at = stat.mtime()
    s.add(entry)
    return entry


class FileSortDirection:
    def __init__(self, dir: str):
        if dir in ["date", "newest"]:
            self.col = File.modified_at
            return
        if dir in ["name"]:
            self.col = File.name
            return
        if dir in ["size", "bytes"]:
            self.col = File.size
            return
        raise Exception(f"Unknown sort direction {dir}")

    def apply(self, query: Query) -> Query:
        return cast(Query, query.order_by(self.col))


class DirectoriesOnly(IntEnum):
    YES = 1
    NO = 2
    BOTH = 3

    def apply(self, query: Query) -> Query:
        if self.value == self.YES:
            return query.where(File.is_dir == True)
        if self.value == self.NO:
            return query.where(File.is_dir == False)
        return query


def get_all_files(
    s: Session,
    root: str,
    name: Optional[str],
    extension: Optional[str],
    directories: DirectoriesOnly,
    sort_by: Optional[FileSortDirection],
) -> Iterator[File]:
    real_root = os.path.abspath(root)
    query = s.query(File).where(File.path.startswith(real_root))
    if name is not None:
        query = query.where(File.name.contains(name))
    if extension is not None:
        query = query.where(File.name.endswith(f".{extension}"))
    query = directories.apply(query)
    if sort_by is not None:
        query = sort_by.apply(query)
    yield from query.all()
