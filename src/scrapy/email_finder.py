import csv
import os
import re
import logging
import threading

from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError, Error
from urllib.parse import urljoin

from url_registry import UrlRegistry


logger = logging.getLogger(__name__)

# Create a thread-local storage object
thread_local = threading.local()

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PATTERN = r'/careers/?$'

CSV_FILE = "scraped_emails.csv"

# Initialize CSV structure
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Target Domain", "Found Email", "Source Strategy", "Page URL"])

class EmailFinder:

    def __init__(self, url_registry: UrlRegistry):
        self.url_registry = url_registry
        self.max_workers = min(len(url_registry.url_list), 4)
        print("Initializing max workers with count", min(len(url_registry.url_list), 4))


    def worker_initializer(self):
        print("Initialized each thread with playwright and browser started")
        thread_local.playwright = sync_playwright().start()
        thread_local.browser = thread_local.playwright.chromium.launch(headless=False)
        thread_local.context = thread_local.browser.new_context()
        print("Initialized each thread with playwright and browser done")


    def find_emails(self):
        """

        :return:
        """
        with ThreadPoolExecutor(max_workers=self.max_workers, initializer=self.worker_initializer) as executor:
            results = executor.map(self.scrape_site, self.url_registry.url_list)
            logger.info("Results: %s", results)

        for mail in results:
            print(f"Scraped data for {mail} = {mail.values()}")
        self.cleanup_workers()

    def scrape_site(self, base_url: str):
        """

        :param base_url:
        :return:
        """

        mail_list = dict()
        print("Processing site: ", base_url)
        page = thread_local.context.new_page()
        career_links = self.find_career_pages(page, base_url)
        print("All career links:", career_links)

        if len(career_links) == 0:
            # try with suffix "careers" on base_url
            url = urljoin(base_url, "/careers")
            mail_links = self.find_mail_id_from_careers_page(page, url)
            mail_list[url] = mail_links

        for link in career_links:
            # find mail from generic site and not specific to region
            if bool(re.search(PATTERN, link)):
                mail_links = self.find_mail_id_from_careers_page(page, link)
                mail_list[link] = mail_links

        print(f"Found {len(mail_list)} mails {mail_list}")
        return mail_list

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

                # count of career links will be 0 if not found at the given url
                # If so try with url/careers
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


    # cleanup
    def cleanup_workers(self):
        print("cleanup of each thread started")
        # close browser and opened contexts
        if hasattr(thread_local, 'context'):
            thread_local.context.close()
        if hasattr(thread_local, 'browser'):
            thread_local.browser.close()
        if hasattr(thread_local, 'playwright'):
            thread_local.playwright.stop()
        print("cleanup of each thread finished")


if __name__ == "__main__":
    target_websites = [
        "https://example.com"
    ]
    registry = UrlRegistry(target_websites)

    test_obj = EmailFinder(registry)
    test_obj.find_emails()



# NOT SITES WITH THEIR
# 1. Open the site using playwright
# 2. Find careers page from the rendered html - in header, footer or nav bar
# 3.
#   3.1 If found, navigate to new url, wait until loaded, search mail_id
#         3.11 If found collect the mail_id
#   3.2  If not found, add careers as prefix or suffix to the existing url
#             navigate to url, wait until loaded and search mail_id
#          3.12 If found collect mail_id
#               else add to validation API

# navigate:
# page.goto("https://example.com")

# Navigate to careers page and then find email address



