from typing import Iterator, List, Optional
import typer
import os
from inotifyrecursive import INotify, flags

from indexme.db.connection import connect
from indexme.db.file_ops import DirectoriesOnly, add_dir, add_file, get_all_files
from indexme.db.paths import get_ignore_path

app = typer.Typer()


def get_global_exclusions() -> Iterator[str]:
    if os.path.exists(get_ignore_path()):
        with open(get_ignore_path()) as f:
            for line in f.readlines():
                yield line.strip()


@app.command()
def index(
    directory: str = typer.Argument(".", help="Root directory"),
    exclude: List[str] = typer.Option([], help="Directory names to exclude"),
    scan: bool = typer.Option(True, help="Scan the directory first"),
    watch: bool = typer.Option(False, help="Watch for changes"),
) -> None:
    exclude = [*exclude, *get_global_exclusions()]

    observer: Optional[INotify] = None
    if watch:
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

    Session = connect()
    if scan:
        with Session() as s:
            for dir_path, subdirs, files in os.walk(directory):
                # https://stackoverflow.com/a/19859907
                subdirs[:] = [d for d in subdirs if d not in exclude]

                for file in files:
                    entry = add_file(s, os.path.join(dir_path, file))
                    print(entry)
                for subdir in subdirs:
                    entry = add_dir(s, os.path.join(dir_path, subdir))
                    print(entry)

            s.commit()

    if watch:
        assert observer is not None
        while True:
            for event in observer.read():
                try:
                    path = os.path.join(observer.get_path(event.wd), event.name)
                    for flag in flags.from_mask(event.mask):
                        if flag in [flags.CREATE, flags.MOVED_TO]:
                            with Session() as s:
                                if os.path.isdir(path):
                                    print(add_dir(s, path))
                                else:
                                    print(add_file(s, path))
                                s.commit()

                        if flag in [
                            flags.MOVED_FROM,
                            flags.DELETE,
                            flags.DELETE_SELF,
                            flags.MOVE_SELF,
                        ]:
                            with Session() as s:
                                for file in get_all_files(
                                    s, path, None, None, DirectoriesOnly.BOTH, None
                                ):
                                    print(file)
                                    s.delete(file)
                                s.commit()

                except Exception as e:
                    print(e)
