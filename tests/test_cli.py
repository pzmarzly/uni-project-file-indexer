from typing import Optional
from unittest import TestCase
from indexme.cli.indexme import index
from indexme.cli.purgeme import purge
from indexme.cli.searchme import search
from contextlib import contextmanager
import io
import sys

from indexme.db.connection import connect
from indexme.db.file_model import File

captured_stdout: Optional[io.StringIO]


@contextmanager
def capture_stdout():
    global captured_stdout
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout
    yield
    sys.stdout = sys.__stdout__
    captured_stdout = None


def get_captured_stdout() -> str:
    global captured_stdout
    assert captured_stdout is not None
    return captured_stdout.getvalue()


def get_db_size() -> int:
    Session = connect()
    with Session() as s:
        return s.query(File).count()


class CliIndexMeTests(TestCase):
    def test_runs_on_ignored_dir(self) -> None:
        with capture_stdout():
            index(directory="tests/empty_dir", exclude=["ignore"])
            self.assertEqual(get_captured_stdout(), "")

    def test_indexes_a_file(self) -> None:
        with capture_stdout():
            index(directory="tests/empty_dir", exclude=["none"])
            self.assertNotEqual(get_captured_stdout(), "")


class CliPurgeMeTests(TestCase):
    def test_purges_dir(self) -> None:
        with capture_stdout():
            index(directory="tests/empty_dir", exclude=[])
        with capture_stdout():
            size1 = get_db_size()
            purge(root="tests/empty_dir")
            size2 = get_db_size()
            self.assertNotEqual(get_captured_stdout(), "")
            self.assertGreater(size1, size2)


class CliSearchMeTests(TestCase):
    def test_finds_file(self) -> None:
        with capture_stdout():
            index(directory="tests/empty_dir", exclude=[])
        with capture_stdout():
            search(
                root="tests/empty_dir",
                name="example",
                extension="txt",
                directories=False,
                sort_by="name",
            )
            self.assertIn("example_file.txt", get_captured_stdout())

    def test_is_silent_on_no_matches(self) -> None:
        with capture_stdout():
            search(
                root="tests/empty_dir",
                name="invalid",
                extension="pdf",
                directories=False,
                sort_by="name",
            )
            self.assertEqual(get_captured_stdout(), "")
