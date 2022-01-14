import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from stat import S_IFDIR, S_ISUID, S_IXUSR  # type: ignore


class Stat(ABC):
    @classmethod
    def get(cls, path: str):
        try:
            return ValidStat(os.stat(path))
        except:
            return InvalidStat()

    @abstractmethod
    def is_dir(self) -> bool:
        pass

    @abstractmethod
    def is_executable(self) -> bool:
        pass

    @abstractmethod
    def is_suid(self) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def ctime(self) -> datetime:
        pass

    @abstractmethod
    def mtime(self) -> datetime:
        pass


class InvalidStat(Stat):
    def is_dir(self) -> bool:
        return False

    def is_executable(self) -> bool:
        return False

    def is_suid(self) -> bool:
        return False

    def size(self) -> int:
        return 0

    def ctime(self) -> datetime:
        return datetime.now()

    def mtime(self) -> datetime:
        return datetime.now()


class ValidStat(Stat):
    def is_dir(self) -> bool:
        return self.stat.st_mode & S_IFDIR != 0

    def is_executable(self) -> bool:
        return self.stat.st_mode & S_IXUSR != 0

    def is_suid(self) -> bool:
        return self.stat.st_mode & S_ISUID != 0

    def __init__(self, stat: os.stat_result):
        self.stat = stat

    def size(self) -> int:
        return self.stat.st_size

    def ctime(self) -> datetime:
        return datetime.fromtimestamp(self.stat.st_ctime, timezone.utc)

    def mtime(self) -> datetime:
        return datetime.fromtimestamp(self.stat.st_mtime, timezone.utc)
