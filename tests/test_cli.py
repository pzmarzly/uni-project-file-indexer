from typing import List
from unittest import TestCase
from indexme.cli.indexme import app as indexme
from indexme.cli.purgeme import app as purgeme
from indexme.cli.searchme import app as searchme
from typer import Typer
from typer.testing import CliRunner
from click.testing import Result

from indexme.db.connection import connect
from indexme.db.file_model import File


def get_db_size() -> int:
    Session = connect()
    with Session() as s:
        return s.query(File).count()


def _invoke(app: Typer, args: List[str]) -> Result:
    res = CliRunner().invoke(app, args)
    if res.exception is not None:
        raise res.exception
    return res


def index(args: List[str]) -> Result:
    return _invoke(indexme, args)


def purge(args: List[str]) -> Result:
    return _invoke(purgeme, args)


def search(args: List[str]) -> Result:
    return _invoke(searchme, args)


class CliIndexMeTests(TestCase):
    def test_can_ignore_dir(self) -> None:
        res = index(["tests/example_dir", "--exclude", "inner"])
        self.assertEqual(res.stdout, "")

    def test_can_ignore_file(self) -> None:
        res = index(["tests/example_dir", "--exclude", "example_file.txt"])
        self.assertNotIn("example_file", res.stdout)

    def test_indexes_a_file(self) -> None:
        res = index(["tests/example_dir", "--exclude", "one", "--exclude", "two"])
        self.assertIn("example_file.txt", res.stdout)


class CliPurgeMeTests(TestCase):
    def setUp(self) -> None:
        purge(["/", "--all"])
        index(["tests/example_dir"])

    def test_purges_dir(self) -> None:
        self.assertEqual(get_db_size(), 2)
        res = purge(["tests/example_dir", "--all"])
        self.assertEqual(get_db_size(), 0)
        self.assertIn("example_file.txt", res.stdout)

    def test_removes_only_deleted_files(self) -> None:
        self.assertEqual(get_db_size(), 2)
        res = purge(["tests/example_dir"])
        self.assertEqual(get_db_size(), 2)


class CliSearchMeTests(TestCase):
    def setUp(self) -> None:
        purge(["/", "--all"])
        index(["tests/example_dir"])

    def test_finds_file(self) -> None:
        res = search(["example", "--extension", "txt", "tests/example_dir"])
        self.assertIn("example_file.txt", res.stdout)

    def test_is_silent_on_no_matches(self) -> None:
        res = search(["invalid", "--extension", "pdf", "tests/example_dir"])
        self.assertEqual(res.stdout, "")

    def test_lists_all_dirs_and_files(self) -> None:
        res = search(["", "tests/example_dir"])
        self.assertIn("inner", res.stdout)
        self.assertIn("example_file.txt", res.stdout)

    def test_lists_all_dirs(self) -> None:
        res = search(["", "--directories", "tests/example_dir"])
        self.assertIn("inner:", res.stdout)
        self.assertNotIn("example_file.txt:", res.stdout)

    def test_lists_all_files(self) -> None:
        res = search(["", "--no-directories", "tests/example_dir"])
        self.assertNotIn("inner:", res.stdout)
        self.assertIn("example_file.txt:", res.stdout)

    def test_counts_files_and_dirs(self) -> None:
        res = search(["", "--count-only", "tests/example_dir"])
        self.assertEqual(res.stdout, "2\n")

    def test_can_list_for_xargs(self) -> None:
        res = search(["", "--xargs", "tests/example_dir"])
        self.assertEqual(
            res.stdout,
            "tests/example_dir/inner\0tests/example_dir/inner/example_file.txt\0",
        )
