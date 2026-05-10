import logging
import os
import time
from datetime import date, timedelta

from requests_oauthlib import OAuth1Session

ZAIM_API_BASE = "https://api.zaim.net/v2"
_RETRY_DELAYS = [1, 2, 4]
logger = logging.getLogger(__name__)


class ZaimAuthError(Exception):
    pass


class ZaimClient:
    def __init__(self):
        self._session = OAuth1Session(
            client_key=os.environ["ZAIM_CONSUMER_KEY"],
            client_secret=os.environ["ZAIM_CONSUMER_SECRET"],
            resource_owner_key=os.environ["ZAIM_ACCESS_TOKEN"],
            resource_owner_secret=os.environ["ZAIM_ACCESS_TOKEN_SECRET"],
        )

    def fetch_yesterday(self) -> list[dict]:
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self._fetch_money(yesterday, yesterday)

    def fetch_range(self, start_date: str, end_date: str) -> list[dict]:
        return self._fetch_money(start_date, end_date)

    def _fetch_money(self, start_date: str, end_date: str) -> list[dict]:
        url = f"{ZAIM_API_BASE}/home/money"
        params = {"mapping": 1, "limit": 100, "start_date": start_date, "end_date": end_date}
        logger.info("Zaim API request: %s params=%s", url, params)

        for delay in [*_RETRY_DELAYS, None]:
            resp = self._session.get(url, params=params)
            logger.info("Zaim API response: status=%d", resp.status_code)
            if resp.status_code == 401:
                raise ZaimAuthError("Zaim authentication failed (401)")
            if resp.status_code < 500:
                resp.raise_for_status()
                body = resp.json()
                money_list = body.get("money", [])
                logger.info("Zaim API money count=%d (mode filter removed for diagnosis)", len(money_list))
                if money_list:
                    modes = [m.get("mode") for m in money_list]
                    logger.info("Zaim API modes in response: %s", modes)
                    logger.info("Zaim API first record: %s", money_list[0])
                else:
                    logger.info("Zaim API returned empty money list. Full body keys: %s", list(body.keys()))
                payment_list = [m for m in money_list if m.get("mode") == "payment"]
                logger.info("Zaim API payment count=%d (after local mode filter)", len(payment_list))
                return [
                    {
                        "zaim_id": str(m["id"]),
                        "date": m["date"],
                        "amount": m["amount"],
                        "name": m.get("place") or m.get("name", ""),
                    }
                    for m in payment_list
                ]
            if delay is not None:
                time.sleep(delay)

        resp.raise_for_status()
        return []
