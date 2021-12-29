import typer

from indexme.db.connection import connect
from indexme.db.file_ops import purge_all_files

app = typer.Typer()


@app.command()
def purge(
    root: str = typer.Argument(..., help="Root directory"),
) -> None:
    Session = connect()
    with Session() as s:
        for file in purge_all_files(s, root):
            print(file)
        s.commit()
