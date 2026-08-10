import csv
import os
import re
import logging
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError, Error


logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PATTERN = r'/careers/?$'

CSV_FILE = "scraped_emails.csv"

# Initialize CSV structure
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Target Domain", "Found Email", "Source Strategy", "Page URL"])


def save_to_csv(domain, email, source, page_url):
    """Appends unique discovered email to CSV."""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([domain, email, source, page_url])


def scrape_site(base_url):
    """

    :param base_url:
    :return:
    """

    mail_list = dict()
    print(f"\n[+] Processing Site: {base_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        career_links = find_career_pages(page, base_url)
        print("All career links:", career_links)

        if len(career_links) == 0:
            # try with suffix "careers" on base_url
            url = base_url+"/careers"
            mail_links = find_mail_id_from_careers_page(page, url)
            mail_list[url] = mail_links

        for link in career_links:
            # find mail from generic site and not specific to region
            if bool(re.search(PATTERN, link)):
                mail_links = find_mail_id_from_careers_page(page, link)
                mail_list[link] = mail_links

        print(f"\n[+] Found {len(mail_list)} mails {mail_list}")

        browser.close()


def find_career_pages(page, url:str) -> list[str]:
    # navigate to the desired site
    result_set = set()
    try:
        response = page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        # wait until page is loaded

        if response.ok:
            print("URL:", page.url)
            print("Title:", page.title())

            print("HTML careers:", "careers" in page.content().lower())

            all_links = page.locator("a").count()
            print("all links", all_links)

            # 1. Locate the anchor tag containing the word "Careers"
            career_links = page.locator('a[href*="careers"]')

            # count of career links will be 0 if not found at the given url
            # If so try with url/careers
            career_link_count = career_links.count()
            print("Career links:", career_link_count)

            for link in career_links.all():
                # if relative path present, make absolute path
                url = urljoin(url, link.get_attribute("href"))
                result_set.add(url)
        elif response.status != 200:
            print("Response from the server: %s", response.status)
            return []
    except (TimeoutError, Error) as e:
        print("Exception occurred as %s", str(e))
        raise
    except Exception as e:
        print("Main exception as %s", str(e))

    return list(result_set)


def find_mail_id_from_careers_page(page, url):
    email_set = set()
    try:
        response = page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        if response.ok:
            print("Career page URL:", page.url)
            print("Career page title:", page.title())

            html = page.content()

            emails = EMAIL_PATTERN.findall(html)
            print("Emails:", emails)
            # de-duplicate and send
            for email in emails:
                email_set.add(email)

        elif response.status != 200:
            print("Response from the server: %s", response.status)
            return []
    except (TimeoutError, Error) as e:
        print("Exception occurred as %s", str(e))
        raise
    except Exception as e:
        print("Main exception as %s", str(e))
    return list(email_set)


if __name__ == "__main__":
    target_websites = [
        "https://www.xyz.com/"
    ]

    for site in target_websites:
        scrape_site(site)



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



