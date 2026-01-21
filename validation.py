# this is to check if an attachment has an url in it
from werkzeug.utils import import_string
import os
import socket
from urllib.parse import urlparse
import boto3
from config import TemplateSvcConfig
from gs360_api.app import get_app_config
from flask import current_app


class FindUrl:
    def __init__(self, doc_type):
        app_config: TemplateSvcConfig = get_app_config()
        self.regex = (
                r'\b(?<!@)((https?|ftp):\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(:\d+)?(\/\S*)?\b'
        )
        self.doc = doc_type
        self.path = ""
        self.file = ""
        self.domain = ''
        self.url = []
        self.aws_path = app_config.AWS_SCANNER_RFP_PATH
        self.region = app_config.AWS_REGION
        self.access_id = app_config.AWS_ACCESS_KEY_ID
        self.secret = app_config.AWS_SECRET_ACCESS_KEY
        self.bucket = app_config.AWS_S3_BUCKET

    def s3_connect(self):
        try:
            if self.doc:
                if not os.path.exists("temp/"):
                    os.makedirs("temp/")
                self.path = str(list(self.doc.values())[0])
                self.file = "temp/" + self.path.rsplit("/")[-1]
                s3 = boto3.resource(
                    "s3",
                    aws_access_key_id=self.access_id,
                    aws_secret_access_key=self.secret,
                )
                s3.meta.client.download_file(
                    self.bucket, self.aws_path + self.path, self.file
                )
                return {"connect": True}
            else:
                return {
                    "connect": False,
                    "results": "400", "message": "s3_connect else attachment type not supported",
                }
        except Exception as exc:
            return {"connect": False, "reason": f's3_connect {exc}'}

    def router(self):
        # this turns the file type into a module and class call so "if" statements are not needed
        connect = self.s3_connect()
        try:
            if connect["connect"]:
                kwargs = {"file": self.file, "regex": self.regex}
                module_name = str(list(self.doc.keys())[0]) + "_files"
                class_name = str(list(self.doc.keys())[0]).upper() + "Read"
                module = import_string(f'services.{module_name}')
                class_call = getattr(module, class_name)
                func = class_call(**kwargs)
                self.url = func.main()
                return  self.check_urls()
            else:
                return connect
        except Exception as exc:
            current_app.logger.info(f'router {exc}')
            return {
                "connect": False,
                "results": "400", "message": f"attachment type not supported {exc}",
                "error": exc,
            }

    def check_urls(self):  # code to send back results codes
        status = {"results": "200", "message": "document good"}
        if self.url:
            for url in self.url:
                if not urlparse(url).scheme:
                    self.domain = url
                    url_valid_check = self.check_if_url_valid()
                    if url_valid_check:
                        status = {"results": "400", "message": "Url found in document"}
                        return status
                else:
                    result = urlparse(url)
                    valid_url = all([result.scheme, result.netloc])
                    if valid_url:
                        status = {"results": "400", "message": "Url found in document"}
                        return status
        os.remove(self.file)
        return status

    def check_if_url_valid(self):
        domain = self.domain.split("/")[0]
        try:
            # Attempt to resolve the domain to an IP address
            socket.gethostbyname(domain)
            return True
        except socket.error:
            return False
