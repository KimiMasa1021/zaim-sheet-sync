import argparse
import logging
import os
from datetime import date, datetime

import requests

from normalizer import normalize
from sheets_client import SheetsClient
from zaim_client import ZaimAuthError, ZaimClient


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Zaim records to Google Sheets")
    parser.add_argument(
        "--start-date",
        default=None,
        help="Fetch records from this date (YYYY-MM-DD) through today. "
        "If omitted, fetches yesterday only.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    logger.info("Starting zaim-sheet-sync")

    zaim = ZaimClient()
    try:
        if args.start_date:
            datetime.strptime(args.start_date, "%Y-%m-%d")
            end_date = date.today().strftime("%Y-%m-%d")
            logger.info("Fetching range %s to %s", args.start_date, end_date)
            records = zaim.fetch_range(args.start_date, end_date)
        else:
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
