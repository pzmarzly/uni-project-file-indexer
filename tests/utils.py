import os
import tempfile
from typing import List, cast

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner

from indexme.db.connection import connect
from indexme.db.file_model import File
from indexme.db.paths import set_db_string_factory, set_ignore_path_factory


def test_env() -> None:
    fd, path = tempfile.mkstemp()
    os.close(fd)
    set_db_string_factory(lambda: f"sqlite:///{path}")
    set_ignore_path_factory(lambda: "/does/not/exist")


def get_db_size() -> int:
    Session = connect()
    with Session() as s:
        return cast(int, s.query(File).count())


def run_app(app: Typer, args: List[str]) -> Result:
    res = CliRunner().invoke(app, args)
    if res.exception is not None:
        raise res.exception
    return res
