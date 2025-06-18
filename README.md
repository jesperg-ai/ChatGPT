# ChatGPT Sleep and Cold Bath Analyzer

This repository contains a simple Python script for correlating your cold bath
habit with sleep data from Oura. If you sync Garmin via Strava kommer dina
kortare kallbadspass automatiskt dyka upp som träningspass i Oura.

## Setup
1. Installera de nödvändiga Python‑paketen:
   ```bash
   python3 -m pip install requests matplotlib
   ```
    (Internetanslutning krävs för att hämta paketen.)

2. Sätt miljövariabeln `OURA_TOKEN` med ditt personliga access token.
3. (Valfritt) Ändra sökvägen `EXPORT_DIR` i `oura_garmin_analyzer.py` om du
   vill spara graferna på en annan plats.

## Hämta din Oura-token
1. Logga in på [Oura Cloud](https://cloud.ouraring.com/).
2. Klicka på ditt profilfoto uppe till höger och välj “Personal access tokens”.
3. Skapa ett nytt token och kopiera värdet.
4. Sätt miljövariabeln `OURA_TOKEN` med värdet från ditt token.

## Running the script
```
python3 oura_garmin_analyzer.py
```
The script fetches the last 30 days of Oura sleep data and
identifierar kallbad genom att leta efter korta morgonpass i Oura
(mellan 06:00 och 10:00, 2–5 minuter). Resultatet blir korrelationen
mellan kallbad och total sovtid. Dessutom skapas filen
`sleep_vs_coldbath.png` som visar sömnlängd per dag där dagar med
kallbad markeras i en annan färg.
Efter körning skapas även `report.html` som innehåller bilden och
öppnas automatiskt i din webbläsare. Du kan öppna den filen senare för
att se grafen igen. Dessutom sparas varje dag en ny
bild i `C:\Users\JesperGunnarson\Dropbox\J Privat\Health\Kallbad`
med filnamnet `sleep_vs_coldbath_YYYY-MM-DD.png` (där datumet motsvarar
dagens datum).

## Disclaimer
This script uses the Oura API and expects valid credentials. Network access is
required to download data from Oura, vilket kan vara begränsat i vissa
miljöer.
