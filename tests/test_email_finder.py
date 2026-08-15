from unittest.mock import patch, MagicMock

import pytest

from scrapy.email_finder import EmailFinder, UrlRegistry

@pytest.fixture
def mock_url_registry():
    return UrlRegistry(["https://example.com", "https://test.com"])

@pytest.fixture
def mock_playwright_objects():
    with patch('scrapy.email_finder.sync_playwright') as mock_sync_playwright:
        # opened using 'with'
        playwright = mock_sync_playwright.return_value.__enter__.return_value
        browser = playwright.chromium.launch.return_value
        context = browser.new_context.return_value
        page = context.new_page.return_value

        yield {
            "playwright": playwright,
            "browser": browser,
            "context": context,
            "page": page
        }

@pytest.fixture
def mock_page():
    return MagicMock()


class TestEmailFinder:

    # make parameterized
    @pytest.mark.parametrize("mock_url_registry, expected_workers",
                             [
                                 (UrlRegistry(["http://example.com"]), 1),
                                 (UrlRegistry(["http://example.com", "http://example.com"]), 2),
                                 (UrlRegistry(["http://example.com", "https://test1.com",
                                               "https://test3.com", "https://test2.com", "https://test4.com",
                                              "https://test5.com"]), 4),
                                 (UrlRegistry([]), 1),

                             ])
    def test_init(self, mock_url_registry, expected_workers):
        """
        Tests initialization of thread workers for url registry
        :param mock_url_registry:
        :param expected_workers:
        :return:
        """
        mock_email_finder = EmailFinder(mock_url_registry)
        assert mock_email_finder.max_workers == expected_workers

    @patch.object(EmailFinder, "scrape_site")
    def test_find_emails(self, mock_scrape_site, mock_url_registry):
        """
        Given 2 URLs
        When scraping them
        Then return the results from both sites
        :return:
        """
        mock_scrape_site.side_effect = [{"https://example.com": ["careers@example.com"],}, {"https://test.com": []}]
        mock_email_finder = EmailFinder(mock_url_registry)

        result = mock_email_finder.find_emails()

        assert len(result) == 2
        assert {'https://example.com': ['careers@example.com']} in result
        assert {'https://test.com': []} in result


    @patch.object(EmailFinder, "find_mail_id_from_careers_page")
    @patch.object(EmailFinder, "find_career_pages")
    def test_scrape_site_with_generic_url(self, mock_find_career_pages, mock_find_mail_id,
                                          mock_playwright_objects, mock_url_registry):
        """
        Given a site with a generic careers URL
        When the site is scraped
        Then emails from that careers URL are returned
        :return:
        """
        mock_find_career_pages.return_value = ["https://example.com/careers"]
        mock_find_mail_id.return_value = ["example@careers.com"]

        mock_email_finder = EmailFinder(mock_url_registry)

        result = mock_email_finder.scrape_site(mock_url_registry.url_list[0])

        assert len(result) == 1
        assert 'https://example.com/careers' in result
        assert result['https://example.com/careers'] == ["example@careers.com"]
        assert mock_playwright_objects['page'].closed()
        assert mock_playwright_objects['browser'].closed()


    @patch.object(EmailFinder, "find_mail_id_from_careers_page")
    @patch.object(EmailFinder, "find_career_pages")
    def test_scrape_site_with_no_career_links(self, mock_find_career_pages, mock_find_mail_id,
                                              mock_playwright_objects, mock_url_registry, mock_page):
        """
        Given a site without career links
        When the site is scraped
        Then /careers is tried
        And emails from that page are returned
        :return:
        """
        mock_find_career_pages.return_value = []
        mock_find_mail_id.return_value = ["test@careers.com"]

        mock_email_finder = EmailFinder(mock_url_registry)

        result = mock_email_finder.scrape_site(mock_url_registry.url_list[1])

        assert len(result) == 1
        assert 'https://test.com/careers' in result
        assert result['https://test.com/careers'] == ["test@careers.com"]
        assert mock_playwright_objects['browser'].closed()


    @patch.object(EmailFinder, "find_mail_id_from_careers_page")
    @patch.object(EmailFinder, "find_career_pages")
    def test_scrape_site_with_no_mails(self, mock_find_career_pages,mock_find_mail_id,
                                       mock_playwright_objects, mock_url_registry):
        """
        Given a site that fails
        When the site is scraped
        Then no emails are returned
        :return:
        """
        mock_find_career_pages.return_value = ["https://example.com/careers"]
        mock_find_mail_id.return_value = []

        mock_email_finder = EmailFinder(mock_url_registry)

        result = mock_email_finder.scrape_site(mock_url_registry.url_list[0])

        assert len(result) == 1
        assert 'https://example.com/careers' in result
        assert result['https://example.com/careers'] == []
        assert mock_playwright_objects['page'].closed()
        assert mock_playwright_objects['browser'].closed()


    def test_sites_with_career_links(self, mock_url_registry, mock_page):
        """
        Given HTML with career links
        When career links are searched
        Then absolute career URLs are returned
        :return:
        """
        response = MagicMock()
        response.ok = True
        response.status = 200

        mock_page.goto.return_value = response

        career_locator = MagicMock()

        link = MagicMock()
        link.get_attribute.return_value = "/careers"

        career_locator.count.return_value = 1
        career_locator.all.return_value = [link]

        mock_page.locator.return_value = career_locator

        email_finder = EmailFinder(mock_url_registry)

        result = email_finder.find_career_pages(
            mock_page,
            "https://example.com",
        )

        assert result == ["https://example.com/careers"]


    def test_sites_with_no_career_links(self, mock_url_registry, mock_page):
        """
        Given HTML without career links
        When career links are searched
        Then an empty list is returned
        :return:
        """

        response = MagicMock()
        response.ok = True
        response.status = 200

        mock_page.goto.return_value = response

        career_locator = MagicMock()
        career_locator.count.return_value = 0
        career_locator.all.return_value = []

        mock_page.locator.return_value = career_locator

        email_finder = EmailFinder(mock_url_registry)

        result = email_finder.find_career_pages(
            mock_page,
            "https://example.com",
        )

        assert result == []

    def test_sites_that_return_failure_response(self, mock_url_registry, mock_page):
        """
        Given a non-successful HTTP response
        When career links are searched
        Then an empty list is returned
        :return:
        """
        response = MagicMock()
        response.ok = False
        response.status = 404

        mock_page.goto.return_value = response

        email_finder = EmailFinder(mock_url_registry)

        result = email_finder.find_career_pages(
            mock_page,
            "https://example.com",
        )

        assert result == []

    def test_mail_id_deduplication(self, mock_page, mock_url_registry):
        """
        Given HTML containing duplicate emails
        When email extraction runs
        Then each email appears only once
        :return:
        """
        response = MagicMock()
        response.ok = True
        response.status = 200

        mock_page.goto.return_value = response

        mock_html = """
        <html>
            <body>
                <div>Contact example@careers.com</div>
                <footer>
                    <div>Contact example@careers.com</div>
                </footer>
            </body>
        </html>
        """
        mock_page.content.return_value = mock_html

        email_finder = EmailFinder(mock_url_registry)

        result = email_finder.find_mail_id_from_careers_page(
            mock_page,
            "https://example.com/careers",
        )

        assert result == ["example@careers.com"]


