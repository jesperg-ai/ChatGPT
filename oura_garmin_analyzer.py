# -*- coding: utf-8 -*-
"""Utility for analyzing cold baths impact on sleep using Oura and Garmin data.

This module provides functions for:
- Fetching sleep data from Oura using the Oura API and a personal access token.
- Fetching activity data from Garmin (placeholder implementation).
- Loading cold bath times from a CSV file.
- Calculating correlations between sleep metrics and cold baths.

The implementation assumes credentials are stored in the `CREDENTIALS` dictionary
below. Replace the placeholders with your actual tokens.
"""

import csv
import datetime as dt
from dataclasses import dataclass
from typing import List, Optional

import requests  # Requires installation of the 'requests' package

# Credentials for API access
CREDENTIALS = {
    "oura_token": "WZCAKZKSCSJD57V6D2DTCMEZ7HUCT6WJ",
    "garmin_client_id": "INSERT_GARMIN_CLIENT_ID",
    "garmin_client_secret": "INSERT_GARMIN_CLIENT_SECRET",
}

OURA_SLEEP_ENDPOINT = "https://api.ouraring.com/v2/usercollection/daily_sleep"

@dataclass
class SleepRecord:
    date: dt.date
    total_sleep_duration: float  # seconds
    deep_sleep_duration: Optional[float] = None
    rest_hr: Optional[float] = None

@dataclass
class ColdBathRecord:
    date: dt.date


def fetch_oura_sleep(start_date: dt.date, end_date: dt.date) -> List[SleepRecord]:
    """Fetch sleep data from Oura between start_date and end_date."""
    headers = {
        "Authorization": f"Bearer {CREDENTIALS['oura_token']}"
    }
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    resp = requests.get(OURA_SLEEP_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    records = []
    for d in data:
        records.append(
            SleepRecord(
                date=dt.date.fromisoformat(d["summary_date"]),
                total_sleep_duration=d.get("total_sleep_duration", 0),
                deep_sleep_duration=d.get("deep_sleep_duration"),
                rest_hr=d.get("resting_heart_rate"),
            )
        )
    return records


def fetch_garmin_activity(start_date: dt.date, end_date: dt.date):
    """Placeholder for fetching Garmin activity data."""
    raise NotImplementedError(
        "Fetching Garmin data requires OAuth credentials and is not implemented."
    )


def load_cold_baths(csv_file: str) -> List[ColdBathRecord]:
    """Load cold bath dates from a CSV file with a 'date' column."""
    records: List[ColdBathRecord] = []
    with open(csv_file, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            records.append(ColdBathRecord(date=dt.date.fromisoformat(row["date"])))
    return records


def correlate_baths_sleep(
    sleep: List[SleepRecord], baths: List[ColdBathRecord]
) -> float:
    """Return the correlation coefficient between cold baths and total sleep time."""
    bath_dates = {b.date for b in baths}
    paired = [
        (s.total_sleep_duration, 1 if s.date in bath_dates else 0) for s in sleep
    ]
    if not paired:
        return 0.0
    mean_sleep = sum(x for x, _ in paired) / len(paired)
    mean_bath = sum(y for _, y in paired) / len(paired)
    var_sleep = sum((x - mean_sleep) ** 2 for x, _ in paired)
    var_bath = sum((y - mean_bath) ** 2 for _, y in paired)
    cov = sum((x - mean_sleep) * (y - mean_bath) for x, y in paired)
    if var_sleep == 0 or var_bath == 0:
        return 0.0
    return cov / (var_sleep ** 0.5 * var_bath ** 0.5)


def main():
    start = dt.date.today() - dt.timedelta(days=30)
    end = dt.date.today()
    sleep_data = fetch_oura_sleep(start, end)
    baths = load_cold_baths("cold_baths.csv")
    corr = correlate_baths_sleep(sleep_data, baths)
    print(f"Correlation between cold baths and sleep duration: {corr:.2f}")


if __name__ == "__main__":
    main()
