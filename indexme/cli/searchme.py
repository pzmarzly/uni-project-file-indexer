from typing import Optional
import typer

from indexme.db.connection import connect
from indexme.db.file_ops import FileSortDirection, get_all_files

app = typer.Typer()


@app.command()
def search(
    name: Optional[str] = typer.Argument(None, help="Filename fragment"),
    root: str = typer.Argument(".", help="Root directory"),
    extension: Optional[str] = typer.Option(None, help="Extension"),
    directories: bool = typer.Option(False, help="Search for directories"),
    sort_by: str = typer.Option("date", help="Sort by name or by date"),
) -> None:
    if sum(x is not None for x in [name, extension]) == 0:
        raise Exception("Please specify at least one search option!")
    direction = FileSortDirection(sort_by)

    Session = connect()
    with Session() as s:
        for file in get_all_files(s, root, name, extension, directories, direction):
            print(file)
