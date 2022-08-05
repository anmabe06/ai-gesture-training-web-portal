import os

import boto3
import pandas

from botocore.exceptions import ClientError

from .logger import logger


class S3Manager:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_s3_bucket_name, aws_s3_region='eu-west-1'):
        self.bucket_name = aws_s3_bucket_name
        self.aws_s3_region = aws_s3_region

        # Start an S3 connection
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.s3_resource = self.session.resource('s3')
        self.bucket = self.s3_resource.Bucket(self.bucket_name)
        self.s3_client = boto3.client('s3', region_name=self.aws_s3_region)

    def _sync(self, origin_path, destination_path, delete=False, exclude=None):
        """
        Args:
            delete (bool, optional): deletes destination_path files not present in origin_path
        """
        options = ' --delete' if delete else ''
        if exclude is not None:
            for item in exclude:
                options += f' --exclude "{item}"'
        os.system(f"aws s3 sync {origin_path} {destination_path}{options}")

    @property
    def bucket_uri(self):
        return f's3://{self.bucket_name}'

    @classmethod
    def is_directory(cls, s3_key):
        return s3_key[-1] == "/"

    @classmethod
    def is_file(cls, s3_key):
        return not cls.is_directory(s3_key)

    def get_s3_uri(self, s3_path):
        return f'{self.bucket_uri}/{s3_path}'

    def get_files_list(self, s3_path):
        "Gets all files names inside given s3 bucket path."
        files = []
        for obj in self.bucket.objects.all():
            remote_file_name = obj.key
            if remote_file_name.startswith(s3_path) and self.is_file(remote_file_name):
                files.append(remote_file_name[remote_file_name.rfind('/')+1:])
        return files

    def read_files_contents(self, s3_path):
        "Gets all files contents inside given s3 bucket path, indexed by file name"
        contents = {}
        for obj in self.bucket.objects.all():
            file_path = obj.key
            if file_path.startswith(s3_path) and self.is_file(file_path):
                file_name = file_path[file_path.rfind('/')+1:]
                content = pandas.read_csv(obj.get()['Body'], header=None)
                contents[file_name] = content.values.tolist()
        return contents

    def get_directories_list(self, s3_path):
        "Gets all directories names inside given s3 bucket path."
        result = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=s3_path, Delimiter='/')
        obj_list = result.get('CommonPrefixes', None)
        if obj_list is not None:
            return [o.get('Prefix').rstrip('/').split('/')[-1] for o in obj_list]
        return []

    def get_files_count(self, s3_path):
        return len(self.get_files_list(s3_path))

    def upload_local_to_s3(self, local_path, s3_path, overwrite, exclude):
        options = dict(
            delete=overwrite,
            exclude=exclude
        )
        self._sync(local_path, self.get_s3_uri(s3_path), **options)

    def download_s3_to_local(self, s3_path, local_path, overwrite):
        options = dict(
            delete=overwrite,
        )
        self._sync(self.get_s3_uri(s3_path), local_path, **options)

    def create_link(self, s3_file_path):
        "Creates s3 link from which anyone can download s3_file_path file"
        return self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket_name, 'Key': s3_file_path},
            ExpiresIn=3600
        )

    def upload_file_to_s3(self, file, s3_path):
        try:
            # response = self.s3_client.upload_file(file.name, self.bucket_name, s3_path)
            response = self.s3_client.put_object(Body=file, Bucket=self.bucket_name, Key=s3_path)
        except ClientError as e:
            logger.error(e)
