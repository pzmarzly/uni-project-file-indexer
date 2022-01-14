import os
import typer

from indexme.db.connection import connect
from indexme.db.file_ops import get_all_files

app = typer.Typer()


@app.command()
def purge(
    root: str = typer.Argument(..., help="Root directory"),
    all: bool = typer.Argument(False, help="Purge even if file exists"),
) -> None:
    Session = connect()
    with Session() as s:
        for is_dir in [False, True]:
            for file in get_all_files(s, root, None, None, is_dir, None):
                if all or not os.path.exists(file):
                    s.delete(file)
                    print(file)
        s.commit()
