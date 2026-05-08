import logging
import os

import requests

from normalizer import normalize
from sheets_client import SheetsClient
from zaim_client import ZaimAuthError, ZaimClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting zaim-sheet-sync")

    zaim = ZaimClient()
    try:
        records = zaim.fetch_yesterday()
    except ZaimAuthError as e:
        logger.error(str(e))
        raise

    logger.info("Fetched %d records from Zaim", len(records))

    for r in records:
        r["name"] = normalize(r["name"])

    sheets = SheetsClient()
    existing_ids = sheets.get_existing_zaim_ids()
    new_records = [r for r in records if r["zaim_id"] not in existing_ids]
    skipped = len(records) - len(new_records)

    if new_records:
        sheets.append_records(new_records)

    logger.info("Processed: %d, Skipped (duplicate): %d", len(new_records), skipped)

    webhook_url = os.environ.get("ROUTINE_WEBHOOK_URL")
    if webhook_url:
        try:
            resp = requests.post(webhook_url, json={"trigger": "zaim-sheet-sync"}, timeout=30)
            resp.raise_for_status()
            logger.info("Webhook posted successfully")
        except Exception as e:
            logger.warning("Webhook POST failed: %s", e)


if __name__ == "__main__":
    main()
