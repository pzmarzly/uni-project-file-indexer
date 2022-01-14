import os
from typing import Optional

import typer

from indexme.db.connection import connect
from indexme.db.file_ops import FileSortDirection, GetAllFiles

app = typer.Typer()


@app.command()
def search(
    name: Optional[str] = typer.Argument(None, help="Filename fragment"),
    root: str = typer.Argument(".", help="Root directory"),
    extension: Optional[str] = typer.Option(None, help="File extension"),
    executable: Optional[bool] = typer.Option(None, help="Search for executables?"),
    suid: Optional[bool] = typer.Option(None, help="Search for SUID bits?"),
    directories: Optional[bool] = typer.Option(None, help="Search for directories?"),
    created_after: Optional[int] = typer.Option(
        None, help="Minimum creation timestamp"
    ),
    created_before: Optional[int] = typer.Option(
        None, help="Maximum creation timestamp"
    ),
    modified_after: Optional[int] = typer.Option(
        None, help="Minimum modification timestamp"
    ),
    modified_before: Optional[int] = typer.Option(
        None, help="Maximum modification timestamp"
    ),
    sort_by: str = typer.Option("date", help="What to sort results by"),
    count_only: bool = typer.Option(False, help="Print number of matches"),
    xargs: bool = typer.Option(False, help="Print xargs-readable NUL-sep. list"),
) -> None:
    direction = FileSortDirection(sort_by)
    if count_only and xargs:
        raise Exception("Conflicting options")

    counter = 0
    Session = connect()
    with Session() as s:
        for file in (
            GetAllFiles(s, root)
            .with_name(name)
            .with_extension(extension)
            .with_executable_bit(executable)
            .with_suid_bit(suid)
            .with_directories_bit(directories)
            .with_created_after(created_after)
            .with_created_before(created_before)
            .with_modified_after(modified_after)
            .with_modified_before(modified_before)
            .with_sorting(direction)
        ):
            counter += 1
            if not count_only:
                if xargs:
                    print(os.path.relpath(file.path), end="\0")
                else:
                    print(file)

    if count_only:
        print(counter)
