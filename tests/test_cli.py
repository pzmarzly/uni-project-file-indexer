from typing import List
from unittest import TestCase
from indexme.cli.indexme import app as indexme
from indexme.cli.purgeme import app as purgeme
from indexme.cli.searchme import app as searchme
from typer.testing import CliRunner
from click.testing import Result

from indexme.db.connection import connect
from indexme.db.file_model import File


def get_db_size() -> int:
    Session = connect()
    with Session() as s:
        return s.query(File).count()


def index(args: List[str]) -> Result:
    return CliRunner().invoke(indexme, args)


def purge(args: List[str]) -> Result:
    return CliRunner().invoke(purgeme, args)


def search(args: List[str]) -> Result:
    return CliRunner().invoke(searchme, args)


class CliIndexMeTests(TestCase):
    def test_runs_on_ignored_dir(self) -> None:
        res = index(["tests/empty_dir", "--exclude", "ignore"])
        self.assertEqual(res.stdout, "")

    def test_indexes_a_file(self) -> None:
        res = index(["tests/empty_dir", "--exclude", "one", "--exclude", "two"])
        self.assertIn("example_file.txt", res.stdout)


class CliPurgeMeTests(TestCase):
    def setUp(self) -> None:
        purge(["/", "--all"])
        index(["tests/empty_dir"])

    def test_purges_dir(self) -> None:
        self.assertEqual(get_db_size(), 2)
        res = purge(["tests/empty_dir", "--all"])
        self.assertEqual(get_db_size(), 0)
        self.assertIn("example_file.txt", res.stdout)

    def test_removes_only_deleted_files(self) -> None:
        self.assertEqual(get_db_size(), 2)
        res = purge(["tests/empty_dir"])
        self.assertEqual(get_db_size(), 2)


class CliSearchMeTests(TestCase):
    def setUp(self) -> None:
        purge(["/", "--all"])
        index(["tests/empty_dir"])

    def test_finds_file(self) -> None:
        res = search(["example", "--extension", "txt", "tests/empty_dir"])
        self.assertIn("example_file.txt", res.stdout)

    def test_is_silent_on_no_matches(self) -> None:
        res = search(["invalid", "--extension", "pdf", "tests/empty_dir"])
        self.assertEqual(res.stdout, "")

    def test_lists_all_files(self) -> None:
        res = search(["", "tests/empty_dir"])
        self.assertIn("example_file.txt", res.stdout)

    def test_counts_files(self) -> None:
        res = search(["", "--count-only", "tests/empty_dir"])
        self.assertEqual(res.stdout, "1\n")
