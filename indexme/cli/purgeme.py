import os

import typer

from indexme.db.connection import connect
from indexme.db.file_ops import GetAllFiles

app = typer.Typer()


@app.command()
def purge(
    root: str = typer.Argument(".", help="Root directory"),
    all: bool = typer.Option(False, help="Purge even if file exists"),
) -> None:
    """
    Scan a subtree and remove deleted files from database.
    Optionally remove the whole subtree.
    """
    Session = connect()
    with Session() as s:
        for file in GetAllFiles(s, root):
            if all or not os.path.exists(file.path):
                s.delete(file)
                print(file)
        s.commit()
