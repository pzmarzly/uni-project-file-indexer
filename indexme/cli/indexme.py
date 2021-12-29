from typing import List
import typer
import os

from indexme.db.connection import connect
from indexme.db.file_ops import add_dir, add_file

app = typer.Typer()


@app.command()
def index(
    directory: str = typer.Argument(".", help="Root directory"),
    exclude: List[str] = typer.Option([], help="Directory names to exclude"),
) -> None:
    Session = connect()
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
