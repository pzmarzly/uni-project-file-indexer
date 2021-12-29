from datetime import datetime
import os
from typing import Iterator, Optional
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.schema import Column

from indexme.db.file_model import File


def _add_entry(s: Session, path: str, is_dir: bool) -> File:
    entry = s.query(File).filter(File.path == path).one_or_none() or File()
    entry.path = path
    entry.name = os.path.split(path)[1]
    entry.is_dir = is_dir
    entry.size = 0 if is_dir else os.stat(path).st_size
    entry.first_seen_at = entry.first_seen_at or datetime.now()
    s.add(entry)
    return entry


def add_file(s: Session, path: str) -> File:
    file_path = os.path.realpath(path)
    return _add_entry(s, file_path, False)


def add_dir(s: Session, path: str) -> File:
    dir_path = os.path.realpath(path)
    return _add_entry(s, dir_path, True)


class FileSortDirection:
    def __init__(self, dir: str):
        if dir in ["date", "newest"]:
            self.col = File.first_seen_at
            return
        if dir in ["name"]:
            self.col = File.name
            return
        if dir in ["size", "bytes"]:
            self.col = File.size
            return
        raise Exception(f"Unknown sort direction {dir}")

    def get(self) -> Column:
        return self.col


def get_all_files(
    s: Session,
    root: str,
    name: Optional[str],
    extension: Optional[str],
    directories: bool,
    sort_by: FileSortDirection,
) -> Iterator[File]:
    real_root = os.path.realpath(root)
    query = s.query(File).where(File.path.startswith(real_root))
    if name is not None:
        query = query.where(File.name.contains(name))
    if extension is not None:
        query = query.where(File.name.endswith(f".{extension}"))
    query = query.where(File.is_dir == directories)
    query = query.order_by(sort_by.get())
    yield from query.all()


def purge_all_files(s: Session, root: str) -> Iterator[File]:
    real_root = os.path.realpath(root)
    query = s.query(File).where(File.path.startswith(real_root))
    for file in query.all():
        yield file
        s.delete(file)
