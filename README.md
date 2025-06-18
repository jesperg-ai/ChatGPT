# ChatGPT Sleep and Cold Bath Analyzer

This repository contains a simple Python script for correlating your cold bath
habit with sleep data from Oura and Garmin. The Garmin portion is currently a
placeholder and will need to be completed with valid API calls and credentials.

## Setup
1. Install the required Python package:
   ```bash
   python3 -m pip install requests
   ```
    (Internet access is required to install the package.)
2. Set environment variables `OURA_TOKEN`, `GARMIN_CLIENT_ID` och
   `GARMIN_CLIENT_SECRET` med dina egna värden.
3. Create a CSV file named `cold_baths.csv` with a header `date` and dates in
   `YYYY-MM-DD` format when you took cold baths.

## Hämta din Oura-token
1. Logga in på [Oura Cloud](https://cloud.ouraring.com/).
2. Klicka på ditt profilfoto uppe till höger och välj “Personal access tokens”.
3. Skapa ett nytt token och kopiera värdet.
4. Sätt miljövariabeln `OURA_TOKEN` med värdet från ditt token.

## Running the script
```
python3 oura_garmin_analyzer.py
```
The script fetches the last 30 days of Oura sleep data, loads your cold bath
dates from `cold_baths.csv`, and prints the correlation between taking a cold
bath and the total sleep duration.

## Disclaimer
This script uses the Oura API and expects valid credentials. Garmin data fetching
is not yet implemented. Network access is required to download data from Oura,
which may not function in restricted environments.
