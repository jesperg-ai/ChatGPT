# -*- coding: utf-8 -*-
"""Utility for analyzing cold baths impact on sleep using data from Oura.

This module provides functions for:
- Fetching sleep data from Oura via the Oura API.
- Fetching workout sessions from Oura and identifying cold baths.
- Calculating correlations between sleep metrics and kallbad.

Credentials are read from the environment variable `OURA_TOKEN` and stored in
the `CREDENTIALS` dictionary.
"""

import datetime as dt
import os
from dataclasses import dataclass
from typing import List, Optional

import requests  # Requires installation of the 'requests' package
import matplotlib.pyplot as plt
import webbrowser

# Folder where daily plots will be stored
EXPORT_DIR = r"C:\Users\JesperGunnarson\Dropbox\J Privat\Health\Kallbad"

# Credentials for API access
CREDENTIALS = {
    # Set this environment variable before running the script
    "oura_token": os.getenv("OURA_TOKEN"),
}

OURA_SLEEP_ENDPOINT = "https://api.ouraring.com/v2/usercollection/daily_sleep"
OURA_WORKOUT_ENDPOINT = "https://api.ouraring.com/v2/usercollection/workout"

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
    token = CREDENTIALS["oura_token"]
    if not token:
        raise EnvironmentError("OURA_TOKEN is not set")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    resp = requests.get(OURA_SLEEP_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print("Sömn-JSON:", data)
    data = data.get("data", [])
    records = []
    for d in data:
        # The API typically exposes the date under the key "day". Fall back to
        # "summary_date" if necessary to avoid KeyError.
        date_str = d.get("day") or d.get("summary_date")
        if not date_str:
            # Skip entries that lack a date field entirely.
            continue
        records.append(
            SleepRecord(
                date=dt.date.fromisoformat(date_str),
                total_sleep_duration=d.get("total_sleep_duration", 0),
                deep_sleep_duration=d.get("deep_sleep_duration"),
                rest_hr=d.get("resting_heart_rate"),
            )
        )
    return records


def fetch_oura_cold_baths(start_date: dt.date, end_date: dt.date) -> List[ColdBathRecord]:
    """Detect cold baths from Oura workouts between start_date and end_date."""
    token = CREDENTIALS["oura_token"]
    if not token:
        raise EnvironmentError("OURA_TOKEN is not set")
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    resp = requests.get(OURA_WORKOUT_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    records: List[ColdBathRecord] = []
    for w in data:
        start_str = w.get("start_datetime") or w.get("start_time")
        if not start_str:
            continue
        # Handle trailing "Z" by converting to offset aware string
        start_dt = dt.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        duration = float(w.get("duration", 0))
        if 6 <= start_dt.hour < 10 and 120 <= duration <= 300:
            records.append(ColdBathRecord(date=start_dt.date()))
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


def plot_sleep_vs_baths(
    sleep: List[SleepRecord],
    baths: List[ColdBathRecord],
    out_path: str = "sleep_vs_coldbath.png",
) -> None:
    """Create a bar plot showing sleep duration and mark days with cold baths."""
    bath_dates = {b.date for b in baths}
    sleep_sorted = sorted(sleep, key=lambda s: s.date)
    dates = [s.date.strftime("%Y-%m-%d") for s in sleep_sorted]
    hours = [s.total_sleep_duration / 3600 for s in sleep_sorted]
    colors = ["tab:blue" if s.date in bath_dates else "tab:gray" for s in sleep_sorted]
    plt.figure(figsize=(10, 4))
    plt.bar(dates, hours, color=colors)
    plt.ylabel("Sömn (timmar)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def open_file_in_browser(path: str) -> None:
    """Open the given file in the default web browser."""
    abs_path = os.path.abspath(path)
    webbrowser.open(f"file://{abs_path}")


def generate_html_report(image_path: str, html_path: str) -> None:
    """Create a simple HTML page displaying the given image."""
    img_name = os.path.basename(image_path)
    html_content = f"""
    <html>
      <head>
        <meta charset='utf-8'>
        <title>Sömn och kallbad</title>
      </head>
      <body>
        <h1>Sömn och kallbad</h1>
        <img src='{img_name}' alt='Sleep vs Coldbath plot'>
      </body>
    </html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    start = dt.date.today() - dt.timedelta(days=30)
    end = dt.date.today()
    sleep_data = fetch_oura_sleep(start, end)
    baths = fetch_oura_cold_baths(start, end)
    corr = correlate_baths_sleep(sleep_data, baths)
    print(f"Correlation between cold baths and sleep duration: {corr:.2f}")
    filename = f"sleep_vs_coldbath_{dt.date.today().isoformat()}.png"
    out_path = os.path.join(EXPORT_DIR, filename)
    plot_sleep_vs_baths(sleep_data, baths, out_path)
    html_path = os.path.join(EXPORT_DIR, "report.html")
    generate_html_report(out_path, html_path)
    open_file_in_browser(html_path)


if __name__ == "__main__":
    main()
