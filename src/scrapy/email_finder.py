import re
import logging
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import TimeoutError, Error, sync_playwright
from urllib.parse import urljoin

from scrapy.url_registry import UrlRegistry


logger = logging.getLogger(__name__)
thread_local = threading.local()

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PATTERN = r'/careers/?$'


class EmailFinder:

    def __init__(self, url_registry: UrlRegistry):
        self.url_registry = url_registry
        workers = min(len(url_registry.url_list), 4)
        self.max_workers = workers
        logger.info("Initializing max workers with count %s", self.max_workers)


    @property
    def max_workers(self):
        return self._max_workers

    @max_workers.setter
    def max_workers(self, value):
        # keep at least one worker
        self._max_workers = value if value > 0 else 1

    def find_emails(self) -> list:
        """

        :return:
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.scrape_site, url) for url in self.url_registry.url_list]
            logger.info("Results: %s", futures)

            for future in as_completed(futures):
                logger.info("Scraped data for %s", future.result())
                results.append(future.result())

        return results

    def scrape_site(self, base_url: str):
        """

        :param base_url:
        :return:
        """

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            mail_directory = dict()
            try:
                logger.info("Processing site: %s", base_url)

                # Original url already points to careers
                if "career" in base_url:
                    career_links = [base_url]
                else:
                    career_links = self.find_career_pages(page, base_url)
                    logger.info("All career links: %s", career_links)

                # count of career links will be 0 if not found at the given url
                # If so try with url/careers
                if len(career_links) == 0:
                    # try with suffix "careers" on base_url
                    url = urljoin(base_url, "/careers")
                    mail_links = self.find_mail_id_from_careers_page(page, url)
                    mail_directory[url] = mail_links

                for link in career_links:
                    # find mail from generic site and not specific to region
                    if bool(re.search(PATTERN, link)):
                        mail_links = self.find_mail_id_from_careers_page(page, link)
                        mail_directory[link] = mail_links

                logger.info("Found %s mails %s", len(mail_directory), mail_directory)
                return mail_directory
            except Exception as e:
                logger.info("Exception occurred %s", str(e))
                return mail_directory
            finally:
                page.close()
                browser.close()
                logger.info("Browser and page closed")

    def find_career_pages(self, page, url: str) -> list[str]:
        # navigate to the desired site
        result_set = set()
        try:
            response = page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            # wait until page is loaded

            if response.ok:
                logger.info("URL: %s", page.url)
                logger.info("Title: %s", page.title())

                all_links = page.locator("a").count()
                logger.info("all links %s", all_links)

                # 1. Locate the anchor tag containing the word "Careers"
                career_links = page.locator('a[href*="careers"]')
                career_link_count = career_links.count()
                logger.info("Career links: %s", career_link_count)

                for link in career_links.all():
                    # if relative path present, make absolute path
                    url = urljoin(url, link.get_attribute("href"))
                    result_set.add(url)
            elif response.status != 200:
                logger.info("Response from the server: %s", response.status)
                return []
        except (TimeoutError, Error) as e:
            logger.exception("Exception occurred as %s", str(e))
            raise
        except Exception as e:
            logger.exception("Main exception as %s", str(e))

        return list(result_set)

    def find_mail_id_from_careers_page(self, page, url: str) -> list[str]:
        email_set = set()
        try:
            response = page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            if response.ok:
                logger.info("Career page URL: %s", page.url)
                logger.info("Career page title: %s", page.title())

                html = page.content()
                emails = EMAIL_PATTERN.findall(html)
                logger.info("Emails: %s", emails)
                # de-duplicate and send
                for email in emails:
                    email_set.add(email)

            elif response.status != 200:
                logger.info("Response from the server: %s", response.status)
                return []
        except (TimeoutError, Error) as e:
            logger.exception("Exception occurred as %s", str(e))
            raise
        except Exception as e:
            logger.exception("Main exception as %s", str(e))
        return list(email_set)
