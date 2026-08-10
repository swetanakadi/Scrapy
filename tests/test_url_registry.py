import logging
from unittest.mock import patch, mock_open

import pytest

from scrapy.url_registry import UrlRegistry


logger = logging.getLogger(__name__)

@pytest.fixture
def mock_url():
    return "https://example.com"

@pytest.fixture
def mock_filepath():
    return "test_urls.txt"


class TestUrlRegistry:

    @patch.object(UrlRegistry,'clean_url')
    def test_url_registry_success_with_url(self, mock_clean, mock_url):
        reg = UrlRegistry(mock_url)
        assert isinstance(reg.url_list, list)
        assert len(reg.url_list) > 0
        assert reg.url_list[0] == mock_url
        mock_clean.assert_called_once()


    @patch("builtins.open", new_callable=mock_open, read_data="a.com\nhttps://b.com\nc.com")
    def test_url_registry_success_with_filepath(self, mock_file,  mock_filepath):

        reg = UrlRegistry.read_from_file(mock_filepath)

        mock_file.assert_called_with(mock_filepath, "r")
        assert reg.url_list == ['https://a.com', 'https://b.com', 'https://c.com']


    @pytest.mark.parametrize("url, expected_list",
                             [
                                 ([""], []),
                                 ("   test.com", ["https://test.com"]),
                                 (["demo.com  ", "https://demo.com"], ["https://demo.com", "https://demo.com"])
                             ])
    def test_clean_url(self, url, expected_list):
        reg = UrlRegistry(url)

        assert reg.url_list == expected_list


    def test_url_registry_file_failure(self, tmp_path):
        non_existent_file = tmp_path / "non_existent_file"

        with pytest.raises(FileNotFoundError):
            UrlRegistry.read_from_file(non_existent_file)


    @pytest.mark.parametrize("junk_init, expected_list",
                             [
                                 (34, []),
                                 (9.8, []),
                                 ({'a': 1, 'b': 2}, [])
                             ])
    def test_url_registry_empty_on_invalid_init(self, junk_init, expected_list):
        reg = UrlRegistry(junk_init)
        assert reg.url_list == expected_list
