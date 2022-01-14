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
from indexme.db.file_ops import add_file

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
            self.assertIn("example_file.txt", get_captured_stdout())


class CliPurgeMeTests(TestCase):
    def setUp(self) -> None:
        with capture_stdout():
            purge(root="/", all=True)
        Session = connect()
        with Session() as s:
            add_file(s, "tests/empty_dir/ignore/example_file.txt")
            add_file(s, "tests/empty_dir/ignore/not_a_file.txt")

    def test_purges_dir(self) -> None:
        with capture_stdout():
            self.assertEqual(get_db_size(), 2)
            purge(root="tests/empty_dir", all=True)
            self.assertEqual(get_db_size(), 0)
            self.assertIn("example_file.txt", get_captured_stdout())
            self.assertIn("not_a_file.txt", get_captured_stdout())

    def test_removes_deleted_files(self) -> None:
        with capture_stdout():
            self.assertEqual(get_db_size(), 2)
            purge(root="tests/empty_dir", all=False)
            self.assertEqual(get_db_size(), 1)
            self.assertIn("example_file.txt", get_captured_stdout())


class CliSearchMeTests(TestCase):
    def setUp(self) -> None:
        with capture_stdout():
            index(directory="tests/empty_dir", exclude=[])

    def test_finds_file(self) -> None:
        with capture_stdout():
            search(
                root="tests/empty_dir",
                name="example",
                extension="txt",
                directories=False,
                sort_by="name",
                count_only=False,
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
                count_only=False,
            )
            self.assertEqual(get_captured_stdout(), "")

    def test_lists_all_files(self) -> None:
        with capture_stdout():
            search(
                root="tests/empty_dir",
                name=None,
                extension=None,
                directories=False,
                sort_by="name",
                count_only=False,
            )
            self.assertIn("example_file.txt", get_captured_stdout())

    def test_counts_files(self) -> None:
        with capture_stdout():
            search(
                root="tests/empty_dir",
                name=None,
                extension=None,
                directories=False,
                sort_by="name",
                count_only=True,
            )
            self.assertEqual(get_captured_stdout(), "1\n")
