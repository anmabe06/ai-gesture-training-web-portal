import sys

from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class CommandEnum(CustomEnum):
    CREATE_LOCAL_DIRS = 'create_local_dirs'
    RENAME_ORIGINAL_VIDEOS = 'rename_original_videos'
    UPLOAD = 'upload'
    DOWNLOAD = 'download'
    PROCESS = 'process'

    @property
    def is_in_argv(self):
        return self.value == sys.argv[1]

    @classmethod
    def has_cmd_in_argv(cls):
        return sys.argv[1] in cls.values()