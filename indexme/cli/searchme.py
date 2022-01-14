from typing import Optional
import typer
import os

from indexme.db.connection import connect
from indexme.db.file_ops import DirectoriesOnly, FileSortDirection, get_all_files

app = typer.Typer()


def directories_only(value: Optional[bool]) -> DirectoriesOnly:
    if value is None:
        return DirectoriesOnly.BOTH
    if value:
        return DirectoriesOnly.YES
    return DirectoriesOnly.NO


@app.command()
def search(
    name: Optional[str] = typer.Argument(None, help="Filename fragment"),
    root: str = typer.Argument(".", help="Root directory"),
    extension: Optional[str] = typer.Option(None, help="Extension"),
    directories: Optional[bool] = typer.Option(None, help="Search for directories"),
    sort_by: str = typer.Option("date", help="Sort by name or by date"),
    count_only: bool = typer.Option(False, help="Print number of matches"),
    xargs: bool = typer.Option(False, help="Print xargs-readable NUL-sep. list"),
) -> None:
    direction = FileSortDirection(sort_by)
    dir_only = directories_only(directories)
    if count_only and xargs:
        raise Exception("Conflicting options")

    counter = 0
    Session = connect()
    with Session() as s:
        for file in get_all_files(s, root, name, extension, dir_only, direction):
            counter += 1
            if not count_only:
                if xargs:
                    print(os.path.relpath(file.path), end="\0")
                else:
                    print(file)

    if count_only:
        print(counter)
