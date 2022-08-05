import csv
import os
import pathlib
import shutil

from .logger import logger


class FileManager:
    """Local filesystem manager, handles operations with hard disk files and dirs"""

    @classmethod
    def file_exists(cls, file_path):
        return os.path.exists(file_path)

    @classmethod
    def flush_directory(cls, dir_path):
        """Removes directory content."""
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

        cls.create_dirs_if_does_not_exist(dir_path)
        logger.notice(f'Directory flushed: {dir_path}')

    @classmethod
    def remove_file_if_exists(cls, file_path):
        if cls.file_exists(file_path):
            os.remove(file_path)

    @staticmethod
    def create_dirs_if_does_not_exist(path):
        p = pathlib.Path(path)
        dir_p = p if p.is_dir() else p.parent
        dir_p.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def rename_file(file_dir, file_name, new_file_name):
        """Renames file inside given file_dir"""
        os.system(f"mv {file_dir}/{file_name} {file_dir}/{new_file_name}")

    @staticmethod
    def list_absolute_paths(dir_path, ignored=None):
        for dirpath,_,filenames in os.walk(dir_path):
            for f in filenames:
                if not f in ignored:
                    yield os.path.abspath(os.path.join(dirpath, f))

    @staticmethod
    def listdir(dir_path, ignored=None):
        items = []
        for item in os.listdir(dir_path):
            if item not in ignored:
                items.append(item)
        return items

    @classmethod
    def get_rows_from_csv_file(cls, csv_path, has_header=False):
        rows = []
        with open(csv_path, 'r') as file:
            csvreader = csv.reader(file)
            if has_header:
                header = next(csvreader)
            for row in csvreader:
                rows.append(row)
        return rows

    @staticmethod
    def flush_csv_file(row, csv_path):
        # mode = 'w' if os.path.exists(csv_path) else 'a'
        FileManager.flush_file()
        FileManager.create_dirs_if_does_not_exist(csv_path)

        with open(csv_path, 'a') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(row)

    @staticmethod
    def append_row_to_csv_file(row, csv_path):
        # mode = 'w' if os.path.exists(csv_path) else 'a'
        FileManager.create_dirs_if_does_not_exist(csv_path)

        with open(csv_path, 'a') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(row)

    @staticmethod
    def get_filename_without_extension(path):
        return pathlib.Path(path).stem

    @classmethod
    def count_file_lines(cls, file_path):
        rows = cls.get_rows_from_csv_file(file_path)
        return len(rows)
