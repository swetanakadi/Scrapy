import argparse
import logging
import sys

from scrapy.url_registry import UrlRegistry


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
    parser = argparse.ArgumentParser(description='Scrapper')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-u', '--url', help='URL to scrape', type=str)
    group.add_argument('--file', '-f', help='File path of urls - .txt extension file', type=str, default='urls.txt')

    args = parser.parse_args()

    if args.url:
        url_registry = UrlRegistry(args.url)
        logger.info("Registry initialized with %s", url_registry.url_list)
        logger.info("Scraping url %s", args.url)
    elif args.file:
        # initialize class with all URLs present in file
        logger.info("Scraping urls from %s", args.file)



if __name__ == '__main__':
    main()
