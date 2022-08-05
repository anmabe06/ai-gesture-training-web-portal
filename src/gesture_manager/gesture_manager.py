import os
import re

from . import s3_mgr
from src import config
from src.file_manager import FileManager
from src.logger import logger


class GestureManager:
    """Only manages given gesture_name when initialized"""

    def __init__(self, local_data_path=None):
        self.local_data_path = local_data_path or config.LOCAL_DATA_PATH

    def listdir(self, local_path):
        "Return files and directories under given local_path. Ignores dotfiles"
        def is_dotfile(file_name):
            return file_name.startswith('.')

        return [
            file_name for file_name in FileManager.listdir(local_path, ignored=config.LOCAL_FILES_IGNORED)
            if not is_dotfile(file_name)
        ]

    @staticmethod
    def has_original_video_prefix(original_video_file_name):
        return original_video_file_name.startswith(f'{config.ORIGINAL_VIDEO_SAMPLE_PREFIX}_')

    @staticmethod
    def has_prefix(file_name, prefix):
        return file_name.startswith(f'{prefix}_')

    def _get_renamed_filename(self, file_name, prefix, current_video_num, append_original_filename=True):
        # builds new file name from given file_name
        file_name, file_ext = os.path.splitext(file_name)

        if self.has_prefix(file_name, prefix):
            # if has prefix, we need to rename again to current_video_num, deleting test_\d+_ prefix
            result = re.search(rf"^{prefix}_\d+_(.+)$", file_name)
            file_name = result.group(1)

        current_video_num_with_leading_zeros = str(current_video_num).zfill(config.PREFIX_DIGITS_NUM)
        new_file_name = f'{prefix}_{current_video_num_with_leading_zeros}'
        if append_original_filename:
            new_file_name += f'_{file_name}'
        new_file_name += file_ext
        return new_file_name

    def _rename_files_in_ascending_numbering(self, local_path, s3_path, prefix,
                                             append_original_filename=True, ignore_local=False,
                                             ignore_s3=False, force=False):
        """
            It counts the number of files on given `s3_path` and then, on a loop, changes
            the names of the files under `local_path` directory to: sample_n[_original_filename].extension,
            where n is an ascending number for each new file.

            e.g.
                - with 14 files already in given s3_path
                - with 2 files renamed in given local_path not uploaded yet to s3_path
                - prefix='sample'
                - append_original_filename=True:

                video1.mp4 -> sample_17_video1.mp4

            Args:
             - local_path (str): absolute or relative path to local directory.
             - s3_path (str): absolute path in s3 bucket.
             - prefix (str): prepends this string for each new file renamed.
             - append_original_filename (bool): decides if we want to include original file name.
        """
        s3_files_list = s3_mgr.get_files_list(s3_path)

        if ignore_s3:
            current_video_num = 0
        else:
            current_video_num = len(s3_files_list)

        local_files_list = self.listdir(local_path)

        if force:
            local_files_list_to_rename = local_files_list
        else:
            local_files_list_unrenamed = [
                file_name for file_name in local_files_list if not self.has_prefix(file_name, prefix)
            ]

            if len(local_files_list_unrenamed) == 0:
                logger.debug(f'No files had to be renamed inside {local_path}')
                return
            local_files_list_to_rename = local_files_list_unrenamed

        if not ignore_local:
            local_files_list_renamed = [
                file_name for file_name in local_files_list if self.has_prefix(file_name, prefix)
            ]
            local_files_renamed_not_in_s3 = [
                file_name for file_name in local_files_list_renamed
                if file_name not in s3_files_list
            ]
            current_video_num += len(local_files_renamed_not_in_s3)

        renamed_count = 0

        for file_name in local_files_list_to_rename:
            current_video_num += 1
            new_file_name = self._get_renamed_filename(file_name, prefix, current_video_num, append_original_filename)
            renamed_count += 1
            FileManager.rename_file(local_path, file_name, new_file_name)
            logger.success(f'\t- File renamed sucessfully: {file_name} -> {new_file_name}')

        logger.success(f'{renamed_count} files were renamed successfully inside {local_path}')

    @property
    def s3_namespaces(self):
        return s3_mgr.get_directories_list('')

    def get_gestures_from_str(self, gesture_str):
        """
        Given gesture_str, it returns all its Gesture objects.

        e.g.
            'single-hand/open-hand' it returns that gesture
            'single-hand/' it returns all gestures from that namespace
        """
        from .gesture import Gesture
        if self.NAMESPACE_SEPARATOR in gesture_str:
            namespace, name = gesture_str.split('/')
            if name == '':
                gesture_names = self.get_local_gestures_names_from_namespace(namespace)
            else:
                gesture_names = [name]
            return [
                Gesture(namespace, name, self) for name in gesture_names
            ]

    def get_local_gestures_inside_namespace(self, namespace):
        "Returns all gesture names in local filesystem under given namespace"
        namespace_gestures_path = os.path.join(self.local_data_path, namespace)
        return FileManager.listdir(namespace_gestures_path, ignored=config.LOCAL_FILES_IGNORED)

    def get_local_namespaces(self):
        return FileManager.listdir(self.local_data_path, ignored=config.LOCAL_FILES_IGNORED)

    def get_local_gestures_names_from_namespace(self, namespace):
        "Returns all gesture names in local filesystem under given namespace"
        namespace_path = os.path.join(self.local_data_path, namespace)
        return FileManager.listdir(namespace_path, ignored=config.LOCAL_FILES_IGNORED)

    def get_gestures_from_csv_file(self, csv_file_path):
        from .gesture import Gesture
        rows = FileManager.get_rows_from_csv_file(csv_file_path, has_header=False)
        return [Gesture(*row, self) for row in rows]

    def get_all_gestures_from_s3(self):
        all_gestures = []
        for namespace in self.s3_namespaces:
            gestures = self.get_all_gestures_from_s3_namespace(namespace)
            all_gestures.extend(gestures)
        return all_gestures

    def get_all_gestures_from_s3_namespace(self, namespace):
        from .gesture import Gesture
        gestures = s3_mgr.get_directories_list(namespace + '/')
        return [Gesture(namespace, gesture, self) for gesture in gestures]

    def get_all_local_gestures(self):
        from .gesture import Gesture
        all_gestures = []
        namespaces = self.get_local_namespaces()
        for namespace in namespaces:
            gestures = self.get_local_gestures_names_from_namespace(namespace)
            all_gestures.extend(
                [Gesture(namespace, gesture, self) for gesture in gestures]
            )
        return all_gestures

    def get_samples_data_from_s3_namespace(self, namespace):
        data = {}
        gestures = self.get_all_gestures_from_s3_namespace(namespace)
        for gesture in gestures:
            data[gesture.name] = gesture.parse_samples_data()
        return data

    def upload_sample_file(self, file, namespace, gesture):
        from .gesture import Gesture
        g = Gesture(namespace, gesture, self)
        current_file_num = g.s3_original_folder_files_count + 1
        prefix = config.ORIGINAL_VIDEO_SAMPLE_PREFIX
        file.filename = self._get_renamed_filename(file.filename, prefix, current_file_num)
        s3_path = f'{g.original_videos_path_s3}/{file.filename}'
        s3_mgr.upload_file_to_s3(file, s3_path)
