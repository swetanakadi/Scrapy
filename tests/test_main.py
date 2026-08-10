import sys
from unittest.mock import patch

import pytest

from scrapper import main


class TestMain:

    @pytest.mark.parametrize("args, expected_msg",
                             [
                             (["scrapper.py", "-u", "test.com"], "Scraping url test.com"),
                             (["scrapper.py", "-f", "test.txt"], "Scraping urls from test.txt"),
                             (["scrapper.py"], "Scraping urls from urls.txt default file"),
                             ])
    def test_main_success(self, args, expected_msg):
        with patch.object(sys, "argv", args):
            main()


    @pytest.mark.parametrize("args, expected_msg",
                             [
                                 (["scrappy.py", "-u", "-f", "test.txt"], ""),
                                 (["scrappy.py", "-f"], ""),
                                 (["scrappy.py", "-t"], "")
                             ])
    def test_main_failure(self, args, expected_msg):
        with patch.object(sys, "argv", args):
            with pytest.raises(SystemExit):
                main()
