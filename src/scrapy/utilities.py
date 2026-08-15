import os
import csv
import logging

logger = logging.getLogger(__name__)

CSV_FILE = os.getenv("OUTPUT_FILE", "scraped_emails.csv")


headers = ["URL", "Emails"]

def generate_csv(mail_directory: list):
    logger.info("Generating csv file")
    try:
        with open(CSV_FILE, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for record in mail_directory:
                for url, mails in record.items():
                    row = [url, ", ".join(mails)]
                    writer.writerow(row)
    except (IOError, AttributeError) as e:
        logger.exception("Exception occurred with %s", str(e))
    else:
        logger.info("Successfully generated output in file %s", CSV_FILE)
