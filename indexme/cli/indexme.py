import os
from typing import Iterator, List

import typer
from inotifyrecursive import INotify, flags  # type: ignore

from indexme.db.connection import connect
from indexme.db.file_ops import GetAllFiles, add_file
from indexme.db.paths import get_ignore_path

app = typer.Typer()


def get_global_exclusions() -> Iterator[str]:
    if os.path.exists(get_ignore_path()):
        with open(get_ignore_path()) as f:
            for line in f.readlines():
                yield line.strip()


def create_observer(directory: str, exclude: List[str]) -> INotify:
    observer = INotify()
    watch_flags = (
        flags.CREATE
        | flags.MOVED_FROM
        | flags.MOVED_TO
        | flags.DELETE
        | flags.DELETE_SELF
        | flags.MOVE_SELF
    )
    observer.add_watch_recursive(
        directory, watch_flags, lambda name, wd, mask: name not in exclude
    )
    return observer


def run_observer(observer: INotify, exclude: List[str]) -> None:
    Session = connect()
    while True:
        for event in observer.read():
            if event.name in exclude:
                continue
            path = os.path.join(observer.get_path(event.wd), event.name)
            try:
                for flag in flags.from_mask(event.mask):
                    if flag in [flags.CREATE, flags.MOVED_TO]:
                        with Session() as s:
                            print(add_file(s, path))
                            s.commit()

                    if flag in [
                        flags.MOVED_FROM,
                        flags.DELETE,
                        flags.DELETE_SELF,
                        flags.MOVE_SELF,
                    ]:
                        with Session() as s:
                            for file in GetAllFiles(s, path):
                                print(file)
                                s.delete(file)
                            s.commit()

            except Exception as e:
                print(e)


def scan_dir(directory: str, exclude: List[str]) -> None:
    Session = connect()
    with Session() as s:
        for dir_path, subdirs, files in os.walk(directory):
            # https://stackoverflow.com/a/19859907
            files[:] = [x for x in files if x not in exclude]
            subdirs[:] = [x for x in subdirs if x not in exclude]

            for file in files:
                entry = add_file(s, os.path.join(dir_path, file))
                print(entry)
            for subdir in subdirs:
                entry = add_file(s, os.path.join(dir_path, subdir))
                print(entry)
        s.commit()


@app.command()
def index(
    directory: str = typer.Argument(".", help="Root directory"),
    exclude: List[str] = typer.Option([], help="Directory names to exclude"),
    scan: bool = typer.Option(True, help="Scan the directory first"),
    watch: bool = typer.Option(False, help="Watch for changes"),
) -> None:
    exclude = [*exclude, *get_global_exclusions()]

    observer = create_observer(directory, exclude) if watch else None

    if scan:
        scan_dir(directory, exclude)

    if watch:
        assert observer is not None
        run_observer(observer, exclude)
