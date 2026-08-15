import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class UrlRegistry:

    def __init__(self, urls: list|str):
        """

        :param urls:
        """
        self.url_list = urls
        self.clean_url()


    @property
    def url_list(self) -> list:
        return self._url_list

    @url_list.setter
    def url_list(self, urls : str|list):
        # validate
        if isinstance(urls, str):
            self._url_list = urls.split(',')
        elif isinstance(urls, list):
            self._url_list = urls
        else:
            self._url_list = []


    @classmethod
    def read_from_file(cls, filename: str):
        """

        :param filename:
        :return:
        """
        try:
            file_path = Path(filename)
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                if not urls and filename == "urls.txt":
                    logger.info("No urls found in file %s. "
                                "Please add urls in file to find emails or specify absolute path "
                                "of the file having urls", filename)
                    sys.exit(0)
        except FileNotFoundError as fe:
            logger.error("File %s not found at current directory %s"
                         "Failed with exception %s", filename, os.getcwd(), fe)
            logger.info("Add file in current directory %s or provide absolute path on command line", os.getcwd())
            raise

        return cls(urls)


    def clean_url(self) -> None:
        """

        :return:
        """
        cleaned_urls = []
        for url in self.url_list:
            stripped = url.strip()

            # empty lines
            if not stripped:
                continue

            # add https if not present
            if not stripped.startswith('https'):
                cleaned_urls.append('https://' + stripped)
            else:
                cleaned_urls.append(stripped)

        self.url_list = cleaned_urls
