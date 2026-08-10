import logging


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
        logger.info("Setter called with %s", urls)
        # validate
        if isinstance(urls, str):
            self._url_list = [urls]
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
            with open(filename, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError as fe:
            logger.exception("File not found %s", fe)
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
