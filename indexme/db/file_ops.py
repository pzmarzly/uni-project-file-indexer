import os
from datetime import datetime
from typing import Iterator, Optional, cast

from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

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


class GetAllFiles:
    def __init__(self, session: Session, root: str):
        self.root = os.path.abspath(root)
        self.query = session.query(File).where(File.path.startswith(self.root))

    def with_path_prefix(self, path: Optional[str]) -> "GetAllFiles":
        if path is not None:
            self.query = self.query.where(File.path.startswith(path))
        return self

    def with_path_equal(self, path: Optional[str]) -> "GetAllFiles":
        if path is not None:
            self.query = self.query.where(File.path == path)
        return self

    def with_name(self, name: Optional[str]) -> "GetAllFiles":
        if name is not None:
            self.query = self.query.where(File.name.contains(name))
        return self

    def with_extension(self, extension: Optional[str]) -> "GetAllFiles":
        if extension is not None:
            self.query = self.query.where(File.name.endswith(f".{extension}"))
        return self

    def with_executable_bit(self, executable: Optional[bool]) -> "GetAllFiles":
        if executable is not None:
            self.query = self.query.where(File.is_executable == executable)
        return self

    def with_suid_bit(self, suid: Optional[bool]) -> "GetAllFiles":
        if suid is not None:
            self.query = self.query.where(File.is_suid == suid)
        return self

    def with_directories_bit(self, directory: Optional[bool]) -> "GetAllFiles":
        if directory is not None:
            self.query = self.query.where(File.is_dir == directory)
        return self

    def with_created_after(self, timestamp: Optional[int]) -> "GetAllFiles":
        if timestamp is not None:
            self.query = self.query.where(
                File.created_at >= datetime.fromtimestamp(timestamp)
            )
        return self

    def with_created_before(self, timestamp: Optional[int]) -> "GetAllFiles":
        if timestamp is not None:
            self.query = self.query.where(
                File.created_at <= datetime.fromtimestamp(timestamp)
            )
        return self

    def with_modified_after(self, timestamp: Optional[int]) -> "GetAllFiles":
        if timestamp is not None:
            self.query = self.query.where(
                File.modified_at >= datetime.fromtimestamp(timestamp)
            )
        return self

    def with_modified_before(self, timestamp: Optional[int]) -> "GetAllFiles":
        if timestamp is not None:
            self.query = self.query.where(
                File.modified_at <= datetime.fromtimestamp(timestamp)
            )
        return self

    def with_sorting(self, sort_by: Optional[FileSortDirection]) -> "GetAllFiles":
        if sort_by is not None:
            self.query = sort_by.apply(self.query)
        return self

    def limit(self, num: int) -> "GetAllFiles":
        self.query = self.query.limit(num)
        return self

    def __iter__(self) -> Iterator[File]:
        yield from self.query.all()


def get_file(s: Session, path: str) -> Optional[File]:
    query = GetAllFiles(s, path).with_path_equal(path).limit(1)
    return next(query.__iter__())
