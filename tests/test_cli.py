from typing import List
from unittest import TestCase

from click.testing import Result

from indexme.cli.indexme import app as indexme
from indexme.cli.purgeme import app as purgeme
from indexme.cli.searchme import app as searchme
from tests.utils import get_db_size, run_app, test_env


def index(args: List[str]) -> Result:
    return run_app(indexme, args)


def purge(args: List[str]) -> Result:
    return run_app(purgeme, args)


def search(args: List[str]) -> Result:
    return run_app(searchme, args)


class CliIndexMeTests(TestCase):
    def setUp(self) -> None:
        test_env()

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
        test_env()
        purge(["/", "--all"])
        index(["tests/example_dir"])

    def test_purges_dir(self) -> None:
        self.assertEqual(get_db_size(), 2)
        res = purge(["tests/example_dir", "--all"])
        self.assertEqual(get_db_size(), 0)
        self.assertIn("example_file.txt", res.stdout)

    def test_removes_only_deleted_files(self) -> None:
        self.assertEqual(get_db_size(), 2)
        purge(["tests/example_dir"])
        self.assertEqual(get_db_size(), 2)


class CliSearchMeTests(TestCase):
    def setUp(self) -> None:
        test_env()
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
        self.assertIn("inner\n", res.stdout)
        self.assertIn("example_file.txt\n", res.stdout)

    def test_lists_all_dirs(self) -> None:
        res = search(["", "--directories", "tests/example_dir"])
        self.assertIn("inner\n", res.stdout)
        self.assertNotIn("example_file.txt\n", res.stdout)

    def test_lists_all_files(self) -> None:
        res = search(["", "--no-directories", "tests/example_dir"])
        self.assertNotIn("inner\n", res.stdout)
        self.assertIn("example_file.txt\n", res.stdout)

    def test_counts_files_and_dirs(self) -> None:
        res = search(["", "--count-only", "tests/example_dir"])
        self.assertEqual(res.stdout, "2\n")

    def test_can_list_for_xargs(self) -> None:
        res = search(["", "--xargs", "tests/example_dir"])
        self.assertEqual(
            res.stdout,
            "tests/example_dir/inner\0tests/example_dir/inner/example_file.txt\0",
        )
