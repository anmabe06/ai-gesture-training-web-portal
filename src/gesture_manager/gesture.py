import os
import re

from src import config
from src.file_manager import FileManager
from src.logger import logger
from src.mediapipe.mediapipe_handler import MediapipeHandler
from . import s3_mgr, mediapipe_handlers
from .enums import GestureNamespaceEnum, GestureSubdirEnum
from .gesture_manager import GestureManager


class Gesture:
    NAMESPACES = GestureNamespaceEnum
    NAMESPACE_SEPARATOR = '/'
    SUB_DIRNAMES = GestureSubdirEnum

    def __init__(self, namespace: str, name: str, mgr: GestureManager):
        self.namespace = namespace
        self.name = name
        self.mgr = mgr
        self.__check()

    def __str__(self):
        return self.namespace + self.NAMESPACE_SEPARATOR + self.name

    def __dict__(self):
        return dict(namespace=self.namespace, name=self.name)

    def __check(self):
        if not self.__has_kebab_case(self.namespace):
            raise Exception(f'Wrong gesture name "{self.name}". Must be in kebab-case format')
        self.__check_namespace()

    def __has_kebab_case(self, str):
        # https://stylelint.io/user-guide/rules/regex/#enforce-a-case
        kebab_case_regex = r"^([a-z][a-z0-9]*)(-[a-z0-9]+)*$"
        return bool(re.match(kebab_case_regex, str))

    def __check_namespace(self):
        if not self.__has_kebab_case(self.namespace):
            raise Exception(f'Wrong gesture namespace "{self.namespace}". Must be in kebab-case format')
        if self.namespace is None:
            raise Exception(f'Gesture must be namespaced. Available namespaces: {self.get_namespaces_str()}')
        if self.namespace not in self.NAMESPACES.__members__.values():
            raise Exception(f'Invalid namespace "{self.namespace}". Available: {self.get_namespaces_str()}')

    def __flush_local_subdirs(self):
        for dir in self.SUB_DIRNAMES.values():
            dir_path = self.__get_local_subpath(dir)
            FileManager.flush_directory(dir_path)

    def __get_local_subpath(self, *subpaths):
        return os.path.join(self.local_path, *subpaths)

    def __get_s3_subpath(self, subpath):
        return f'{self.s3_path}/{subpath}'

    def __get_sample_csv_path(self, original_video_filename):
        csv_filename = FileManager.get_filename_without_extension(original_video_filename)
        return self.__get_local_subpath(self.SUB_DIRNAMES.CSV, f'{csv_filename}.csv')

    def __get_mp_handler(self) -> MediapipeHandler:
        return mediapipe_handlers[self.namespace]

    def __get_original_video_sample_number(self, original_video_filename):
        "e.g. sample_4_dfdfdf.mp4 it returns 4"
        return original_video_filename.split('_')[1]

    def __is_video_already_processed(self, video_filename):
        has_landmarked = os.path.exists(self.__get_local_subpath(self.SUB_DIRNAMES.LANDMARKED, video_filename))
        csv_dir = FileManager.get_filename_without_extension(video_filename)
        has_csv = os.path.exists(self.__get_local_subpath(self.SUB_DIRNAMES.CSV, csv_dir))
        return has_landmarked and has_csv

    def __is_video_renamed(self, original_video_filename):
        return original_video_filename.startswith(f'{config.ORIGINAL_VIDEO_SAMPLE_PREFIX}_')

    @classmethod
    def get_namespaces_str(cls):
        return ', '.join(cls.NAMESPACES)

    @classmethod
    def from_str(cls, gesture_str: str, *args):
        if cls.NAMESPACE_SEPARATOR not in gesture_str:
            raise Exception('Gesture must contain namespace separator "/"')
        namespace, name = gesture_str.split('/')
        return cls(namespace, name, *args)

    @property
    def local_path(self):
        return os.path.join(self.mgr.local_data_path, self.namespace, self.name)

    @property
    def s3_path(self):
        return f'{self.namespace}/{self.name}'

    @property
    def local_path_exists(self):
        return os.path.exists(self.local_path)

    @property
    def original_videos_path_local(self):
        return self.__get_local_subpath(self.SUB_DIRNAMES.ORIGINAL)

    @property
    def csv_path_local(self):
        return self.__get_local_subpath(self.SUB_DIRNAMES.CSV)

    @property
    def csv_path_s3(self):
        return self.__get_s3_subpath(self.SUB_DIRNAMES.CSV)

    @property
    def original_videos_path_s3(self):
        return self.__get_s3_subpath(self.SUB_DIRNAMES.ORIGINAL)

    @property
    def original_videos_list_s3(self):
        return s3_mgr.get_files_list(self.original_videos_path_s3)

    @property
    def original_videos_list_local(self):
        return FileManager.listdir(self.original_videos_path_local, ignored=config.LOCAL_FILES_IGNORED)

    @property
    def s3_original_folder_files_count(self):
        return len(self.original_videos_list_s3)

    @property
    def has_s3_original_videos(self):
        return len(self.original_videos_list_s3) > 0

    @property
    def original_videos_files_names_local(self):
        return self.mgr.listdir(self.original_videos_path_local)

    @property
    def original_videos_unrenamed(self):
        return [
            file_name for file_name in self.original_videos_files_names_local
            if not self.mgr.has_original_video_prefix(file_name)
        ]

    def create_local_dir(self, overwrite=False):
        overwrited = False
        if self.local_path_exists:
            if overwrite:
                overwrited = True
            else:
                raise Exception(f'Cannot create gesture dirs that already exists in {self.local_path}')
        self.__flush_local_subdirs()
        if overwrited:
            logger.success(f'New gesture dirs overwritten ok: {self}')
        else:
            logger.success(f'New gesture dirs created ok: {self}')

    def rename_original_videos(self, **options):
        self.mgr._rename_files_in_ascending_numbering(
            self.original_videos_path_local,
            self.original_videos_path_s3,
            config.ORIGINAL_VIDEO_SAMPLE_PREFIX,
            **options
        )

    def upload(self, subpaths=None, overwrite=False):
        logger.info(f'Uploading gesture "{self}"..')
        subpaths = subpaths or self.SUB_DIRNAMES.values()
        for subpath in subpaths:
            local_subpath = os.path.join(self.local_path, subpath)
            logger.debug(f'checking subpath {local_subpath}..')
            s3_subpath = f'{self.s3_path}/{subpath}'
            if subpath == self.SUB_DIRNAMES.ORIGINAL:
                for file_name in self.original_videos_list_local:
                    original_video_path_local = os.path.join(self.original_videos_path_local, file_name)
                    logger.debug(f'checking original video {original_video_path_local}..')
                    if self.__is_video_renamed(file_name):
                        original_video_path_s3 = f'{s3_subpath}/{file_name}'
                        s3_mgr.upload_local_to_s3(original_video_path_local, original_video_path_s3, overwrite, exclude=config.LOCAL_FILES_IGNORED)
                    else:
                        logger.warning(f'Original video needs to be renamed before uploading to s3: {original_video_path_local}')

            s3_subpath = f'{self.s3_path}/{subpath}'
            s3_mgr.upload_local_to_s3(local_subpath, s3_subpath, overwrite, config.LOCAL_FILES_IGNORED)

    def download(self, subpaths=None, overwrite=False):
        if subpaths is None:
            s3_mgr.download_s3_to_local(self.s3_path, self.local_path, overwrite)
        else:
            for subpath in subpaths:
                local_subpath = os.path.join(self.local_path, subpath)
                s3_subpath = f'{self.s3_path}/{subpath}'
                s3_mgr.download_s3_to_local(s3_subpath, local_subpath, overwrite)

    def process(self, samples_only=None, re_process=False):
        def skip(original_video):
            if not self.__is_video_renamed(original_video):
                logger.warning(f'Gesture "{self}" has video not renamed yet: {original_video}')
                return True

            if samples_only:
                sample_number = self.__get_original_video_sample_number(original_video)
                if sample_number not in samples_only:
                    return True

            if self.__is_video_already_processed(original_video) and not re_process:
                logger.debug(f'Gesture {self} has video already processed: {original_video}')
                return True

            return False

        if not self.original_videos_list_local:
            logger.warning(f'Gesture has no original videos: {self}')
            return

        mp_handler = self.__get_mp_handler()
        for original_video in self.original_videos_list_local:
            if skip(original_video):
                continue
            original_video_path = self.__get_local_subpath(self.SUB_DIRNAMES.ORIGINAL, original_video)
            landmarked_video_path = self.__get_local_subpath(self.SUB_DIRNAMES.LANDMARKED, original_video)
            mp_handler.set_csv_file_path(self.__get_sample_csv_path(original_video))
            mp_handler.process_video(
                original_video_path,
                landmarked_video_path,
            )

    def parse_samples_data(self):
        return s3_mgr.read_files_contents(f'{self.csv_path_s3}/')

    def create_sample_video_link(self):
        "Creates sample video s3 link that can be accessed publicly"
        if not self.has_s3_original_videos:
            return None

        first_sample_video_path = f'{self.original_videos_path_s3}/{self.original_videos_list_s3[0]}'
        return s3_mgr.create_link(first_sample_video_path)
