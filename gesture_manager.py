import argparse
import logging

from src.enums import CommandEnum
from src.gesture_manager.gesture_manager import GestureManager
from src.gesture_manager.gesture import Gesture
from src.logger import logger


def parse_args():
    parser = argparse.ArgumentParser()

    if not CommandEnum.has_cmd_in_argv():
        actions = parser.add_argument_group('Actions')
        actions.add_argument(CommandEnum.CREATE_LOCAL_DIRS.value, help='Creates new gestures folders for adding new videos')
        actions.add_argument(CommandEnum.RENAME_ORIGINAL_VIDEOS.value, help='Renames gestures original videos in ascending order')
        actions.add_argument(CommandEnum.UPLOAD.value, help='Uploads gestures content to S3')
        actions.add_argument(CommandEnum.DOWNLOAD.value, help='Downloads gestures content to S3')
        actions.add_argument(CommandEnum.PROCESS.value, help='Process gestures data from videos')

    if CommandEnum.CREATE_LOCAL_DIRS.is_in_argv:
        parser.add_argument(dest=CommandEnum.CREATE_LOCAL_DIRS.value)
        parser.add_argument('gestures', nargs='*')
        parser.add_argument('-f', '--file', nargs='?', help='Creates from given .csv file')
        parser.add_argument('-o', '--overwrite', action='store_true', default=False, help='Overwrites existing gestures with same name and namespace')

    if CommandEnum.RENAME_ORIGINAL_VIDEOS.is_in_argv:
        parser.add_argument(CommandEnum.RENAME_ORIGINAL_VIDEOS.value)
        parser.add_argument('-g', '--gestures', nargs='*', help='Renames original videos for specific gestures only')
        parser.add_argument('-f', '--force', action='store_true', help='Forces renaming again for already renamed files')
        parser.add_argument('--append-original-filename', action='store_true', help='Adds original file name after prefix and number')
        parser.add_argument('--ignore-local', action='store_true', help='Ignores local files for getting next number')
        parser.add_argument('--ignore-s3', action='store_true', help='Ignores s3 files for getting next number')

    if CommandEnum.UPLOAD.is_in_argv:
        parser.add_argument(CommandEnum.UPLOAD.value, help='Uploads gestures from local folder to S3')

    if CommandEnum.DOWNLOAD.is_in_argv:
        parser.add_argument(CommandEnum.DOWNLOAD.value, help="Downloads gestures from S3 to local folder")

    # upload/download options
    if CommandEnum.UPLOAD.is_in_argv or CommandEnum.DOWNLOAD.is_in_argv:
        parser.add_argument('-g', '--gestures', nargs='*', help='Downloads/uploads specific gestures only')
        parser.add_argument('-o', '--overwrite', action='store_true', default=False,
            help=(
                'When downloading, it removes local data that does not exists in s3.'
                'When uploading, it removes remote data that does not exists in local filesystem.'
            )
        )
        parser.add_argument('-p', '--sub-paths', nargs='*')
        parser.add_argument('-a', '--all', action='store_true', default=False)

    if CommandEnum.PROCESS.is_in_argv:
        parser.add_argument(CommandEnum.PROCESS.value, help='Process new original videos for each gesture')
        parser.add_argument('-g', '--gestures', nargs='*', help='Process specific gestures')
        parser.add_argument('-r', '--re-process', action='store_true', default=False, help='Re-processes videos that are already processed')
        parser.add_argument('-s', '--sample-numbers', nargs='*', help='Process specific sample numbers from original videos')

    parser.add_argument('--local-data-path', type=str)
    parser.add_argument('-v', '--verbosity', action="count", help="increase output verbosity")

    return parser.parse_args()


def manage_gesture(gesture: Gesture):
    if CommandEnum.CREATE_LOCAL_DIRS.is_in_argv:
        gesture.create_local_dir(args.overwrite)

    elif CommandEnum.RENAME_ORIGINAL_VIDEOS.is_in_argv:
        options = dict(
            append_original_filename=args.append_original_filename,
            ignore_local=args.ignore_local,
            ignore_s3=args.ignore_s3,
            force=args.force,
        )
        gesture.rename_original_videos(**options)

    elif CommandEnum.UPLOAD.is_in_argv:
        gesture.upload(args.sub_paths, args.overwrite)

    elif CommandEnum.DOWNLOAD.is_in_argv:
        gesture.download(args.sub_paths, args.overwrite)

    elif CommandEnum.PROCESS.is_in_argv:
        gesture.process(args.sample_numbers, args.re_process)


def get_gestures():
    if args.gestures:
        gestures = []
        for gesture_str in args.gestures:
            gestures.extend(gesture_mgr.get_gestures_from_str(gesture_str))

    if CommandEnum.CREATE_LOCAL_DIRS.is_in_argv and args.file is not None:
        return gesture_mgr.get_gestures_from_csv_file(args.file)

    if CommandEnum.RENAME_ORIGINAL_VIDEOS.is_in_argv:
        return gesture_mgr.get_all_local_gestures()

    if CommandEnum.UPLOAD.is_in_argv:
        return gesture_mgr.get_all_local_gestures()

    if CommandEnum.DOWNLOAD.is_in_argv:
        return gesture_mgr.get_all_gestures_from_s3()

    if CommandEnum.PROCESS.is_in_argv:
        return gesture_mgr.get_all_local_gestures()

    return []


def set_verbosity():
    if args.verbosity is None:
        level = logging.WARNING
    elif args.verbosity == 1:
        level = logging.INFO
    elif args.verbosity == 2:
        level = logging.DEBUG
    logger.setLevel(level)


if __name__ == "__main__":

    args = parse_args()

    set_verbosity()

    mgr_options = dict(
        local_data_path=args.local_data_path,
    )
    gesture_mgr = GestureManager(**mgr_options)

    for gesture in get_gestures():
        manage_gesture(gesture)
