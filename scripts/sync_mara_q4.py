from __future__ import annotations

import calendar
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3
from bs4 import BeautifulSoup

MARA_URL = "https://www.mara.gov.om/calendar_page2.asp"
ROOT = Path(__file__).resolve().parents[1]
LOCATIONS_PATH = ROOT / "data" / "locations.json"
YEAR = 2026
MONTHS = (10, 11, 12)
USER_AGENT = "Mozilla/5.0 (compatible; OmanPrayerTimesMirror/1.0)"

# MARA's current TLS chain is not accepted by standard hosted-runner trust stores.
# We only ingest the published timetable and validate its structure/content before
# committing it. Keep warnings quiet so workflow logs remain readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def hhmm(value: str, prayer: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"\d{1,2}:\d{2}", value):
        raise ValueError(f"Invalid time for {prayer}: {value!r}")
    hour, minute = map(int, value.split(":"))
    if not (0 <= minute <= 59):
        raise ValueError(f"Invalid minute for {prayer}: {value!r}")

    # MARA renders afternoon/evening values in 12-hour notation without AM/PM.
    if prayer == "asr" and hour < 12:
        hour += 12
    elif prayer == "maghrib" and hour < 12:
        hour += 12
    elif prayer == "isha" and hour < 12:
        hour += 12

    if not (0 <= hour <= 23):
        raise ValueError(f"Invalid hour for {prayer}: {value!r}")
    return f"{hour:02d}:{minute:02d}"


def parse_month(html: str, year: int, month: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    prayer_table = None
    date_re = re.compile(rf"^\s*\d{{1,2}}/{month}/{year}\s*$")

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if any(row.find("td") and date_re.match(row.find("td").get_text(" ", strip=True)) for row in rows):
            prayer_table = table
            break

    if prayer_table is None:
        raise ValueError(f"No MARA prayer table found for {year}-{month:02d}")

    records: list[dict] = []
    for row in prayer_table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) != 7 or not date_re.match(cells[0]):
            continue

        day, parsed_month, parsed_year = map(int, cells[0].split("/"))
        if (parsed_year, parsed_month) != (year, month):
            raise ValueError(f"Unexpected date in MARA table: {cells[0]}")

        records.append(
            {
                "date": f"{year:04d}-{month:02d}-{day:02d}",
                "fajr": hhmm(cells[1], "fajr"),
                "sunrise": hhmm(cells[2], "sunrise"),
                "dhuhr": hhmm(cells[3], "dhuhr"),
                "asr": hhmm(cells[4], "asr"),
                "maghrib": hhmm(cells[5], "maghrib"),
                "isha": hhmm(cells[6], "isha"),
            }
        )

    expected_days = calendar.monthrange(year, month)[1]
    if len(records) != expected_days:
        raise ValueError(
            f"Expected {expected_days} MARA rows for {year}-{month:02d}; got {len(records)}"
        )

    dates = [record["date"] for record in records]
    if len(set(dates)) != expected_days:
        raise ValueError(f"Duplicate/missing dates for {year}-{month:02d}")

    for record in records:
        values = [
            record["fajr"],
            record["sunrise"],
            record["dhuhr"],
            record["asr"],
            record["maghrib"],
            record["isha"],
        ]
        minutes = [int(v[:2]) * 60 + int(v[3:]) for v in values]
        if minutes != sorted(minutes):
            raise ValueError(f"Prayer order is invalid on {record['date']}: {values}")

    return records


def get_city_options(session: requests.Session) -> list[tuple[str, str]]:
    response = session.get(
        MARA_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=45,
        verify=False,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    select = soup.find("select", attrs={"name": "CityID"})
    if select is None:
        raise ValueError("MARA CityID selector was not found")
    options: list[tuple[str, str]] = []
    for option in select.find_all("option"):
        value = str(option.get("value", "")).strip()
        label = option.get_text(" ", strip=True)
        if value:
            options.append((value, label))
    if not options:
        raise ValueError("MARA CityID selector contained no options")
    return options


def fetch_month(
    session: requests.Session, city_id: str, year: int, month: int
) -> list[dict]:
    response = session.post(
        MARA_URL,
        data={"year": str(year), "month": str(month), "CityID": city_id},
        headers={"User-Agent": USER_AGENT},
        timeout=45,
        verify=False,
    )
    response.raise_for_status()
    return parse_month(response.text, year, month)


def main() -> int:
    locations = json.loads(LOCATIONS_PATH.read_text(encoding="utf-8"))
    session = requests.Session()
    options = get_city_options(session)

    if len(options) != len(locations):
        raise ValueError(
            f"MARA exposes {len(options)} CityID options but locations.json has {len(locations)} locations"
        )

    # The mirror index was created from MARA's CityID order. Guard against an
    # upstream reorder before mapping numeric IDs to our stable location keys.
    first_checks = [
        ("muscat", "Muscat"),
        ("ibra", "Ibra"),
        ("adam", "Adam"),
    ]
    for index, (key, label) in enumerate(first_checks):
        if locations[index]["key"] != key or options[index][1].strip().lower() != label.lower():
            raise ValueError(
                f"MARA location order changed near index {index}: "
                f"{options[index]!r} vs {locations[index]!r}"
            )

    # Parser regression test: September Muscat must exactly reproduce the
    # committed, previously verified MARA mirror before Q4 data is accepted.
    september_expected = json.loads(
        (ROOT / "data" / "2026" / "09.json").read_text(encoding="utf-8")
    )["muscat"]
    september_live = fetch_month(session, options[0][0], YEAR, 9)
    if september_live != september_expected:
        raise ValueError("Live MARA September Muscat data does not match the verified mirror")

    output_dir = ROOT / "data" / str(YEAR)
    output_dir.mkdir(parents=True, exist_ok=True)

    for month in MONTHS:
        month_payload: dict[str, list[dict]] = {}
        for index, (city_id, label) in enumerate(options):
            key = locations[index]["key"]
            print(f"Fetching {YEAR}-{month:02d} {key} (CityID={city_id}, {label})", flush=True)
            month_payload[key] = fetch_month(session, city_id, YEAR, month)
            time.sleep(0.10)

        target = output_dir / f"{month:02d}.json"
        target.write_text(
            json.dumps(month_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {target} with {len(month_payload)} locations", flush=True)

    metadata = {
        "source": "Oman Ministry of Endowments and Religious Affairs (MARA)",
        "sourceUrl": MARA_URL,
        "lastUpdated": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "coverageThrough": "2026-12-31",
        "year": YEAR,
        "months": [9, 10, 11, 12],
        "locationCount": len(locations),
    }
    (ROOT / "data" / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Validated MARA parser against September and mirrored {len(locations)} locations "
        f"through {metadata['coverageThrough']}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
