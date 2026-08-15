import argparse
import logging
import sys

from scrapy.url_registry import UrlRegistry
from scrapy.email_finder import EmailFinder
from scrapy.utilities import generate_csv


def setup_logging():
    """
    Basic logging setup
    :return:
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)]
            )



def main():

    setup_logging()

    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='A CLI utility to scrape emails from a url - specifically careers page of the url')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-u', '--url', help='URL/s to scrape with multiple urls passed as comma(,) separated in a string', type=str)
    group.add_argument('--file', '-f', help='File path of urls - .txt extension file. Default file present as urls.txt '
                                            'which can be populated with urls to scrape, otherwise pass the absolute file '
                                            'path having urls to scrape', type=str, default='urls.txt')

    args = parser.parse_args()

    if args.url:
        url_registry = UrlRegistry(args.url)
        logger.info("Registry initialized with %s", url_registry.url_list)
        logger.info("Scraping url %s", args.url)

    elif args.file:
        # initialize class with all URLs present in file
        logger.info("Scraping urls from %s", args.file)
        # if file path specified at command line
        url_registry = UrlRegistry.read_from_file(args.file)

    mail_finder = EmailFinder(url_registry)
    mail_directory = mail_finder.find_emails()
    generate_csv(mail_directory)


if __name__ == '__main__':
    main()
