import sys
from unittest.mock import patch, MagicMock

import pytest

from scrapper import main


class TestMain:

    @pytest.mark.parametrize(
        "args, expected_filepath",
        [
            (["scrapper.py", "-f", "test.txt"], "test.txt"),
            (["scrapper.py"], "urls.txt"),
        ],
    )
    @patch("scrapper.generate_csv")
    @patch("scrapper.EmailFinder")
    @patch("scrapper.UrlRegistry.read_from_file")
    def test_main_with_file(self, mock_read_from_file,mock_email_finder,
            mock_generate_csv,args,expected_filepath,):

        mock_registry = MagicMock()
        mock_registry.url_list = ["https://example.com"]
        mock_read_from_file.return_value = mock_registry

        expected_results = [
            {"https://example.com": ["test@example.com"]}
        ]
        mock_email_finder.return_value.find_emails.return_value = expected_results

        with patch.object(sys, "argv", args):
            main()

        mock_read_from_file.assert_called_once_with(expected_filepath)



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
                
