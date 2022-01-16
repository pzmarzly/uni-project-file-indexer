import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone

# Copied from stat.py due to Pylance errors.
S_IFDIR = 0o040000  # directory
S_ISUID = 0o4000  # set UID bit
S_IXUSR = 0o0100  # execute by owner


class Stat(ABC):
    """
    Represents a Stat results.
    Can contain null values (zeros, empty strings etc.).
    """

    @classmethod
    def get(cls, path: str) -> "Stat":
        """
        Try stat-ing a given path. Never fails.
        """
        try:
            return ValidStat(os.stat(path))
        except:
            return InvalidStat()

    @abstractmethod
    def is_dir(self) -> bool:
        """
        Does this path lead to a directory?
        """

    @abstractmethod
    def is_executable(self) -> bool:
        """
        Is this a file with owner-executable bit set?
        """

    @abstractmethod
    def is_suid(self) -> bool:
        """
        Is this a file with SUID bit set?
        """

    @abstractmethod
    def size(self) -> int:
        """
        How large (in bytes) is this file?
        """

    @abstractmethod
    def ctime(self) -> datetime:
        """
        Get a creation time.
        """

    @abstractmethod
    def mtime(self) -> datetime:
        """
        Get a modification time.
        """


class InvalidStat(Stat):
    """
    Represents a failed stat results.
    Returns null values (zeros, empty strings, etc.).
    """

    def is_dir(self) -> bool:
        return False

    def is_executable(self) -> bool:
        return False

    def is_suid(self) -> bool:
        return False

    def size(self) -> int:
        return 0

    def ctime(self) -> datetime:
        return datetime.fromtimestamp(0)

    def mtime(self) -> datetime:
        return datetime.fromtimestamp(0)


class ValidStat(Stat):
    """
    Represents a successful stat results.
    Does not do any I/O anymore - uses memoized results instead.
    """

    def __init__(self, stat: os.stat_result):
        self.stat = stat

    def is_dir(self) -> bool:
        return self.stat.st_mode & S_IFDIR != 0

    def is_executable(self) -> bool:
        return (not self.is_dir()) and self.stat.st_mode & S_IXUSR != 0

    def is_suid(self) -> bool:
        return (not self.is_dir()) and self.stat.st_mode & S_ISUID != 0

    def size(self) -> int:
        return self.stat.st_size

    def ctime(self) -> datetime:
        return datetime.fromtimestamp(int(self.stat.st_ctime), timezone.utc)

    def mtime(self) -> datetime:
        return datetime.fromtimestamp(int(self.stat.st_mtime), timezone.utc)
