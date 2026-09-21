# Oman Prayer Times API

A lightweight JSON API for Oman prayer times sourced from the published timetable of the Oman Ministry of Endowments and Religious Affairs (MARA).

> This is an independent API wrapper/mirror. It is not an official Ministry API.

## Production base URL

```text
https://oman-prayer-times-api.vercel.app/api/prayer-times
```

## Query modes

### List supported location keys

```http
GET /api/prayer-times?locations=true
```

### Single date

```http
GET /api/prayer-times?city=muscat&date=2026-09-16
```

### Single month

```http
GET /api/prayer-times?city=muscat&year=2026&month=9
```

### Month range

```http
GET /api/prayer-times?city=muscat&year=2026&fromMonth=9&toMonth=12
```

## Current bootstrap coverage

The API runtime and query contract are live.

The repository currently contains:
- the initial MARA location-key index used by the prototype;
- one verified MARA prayer-time record for Muscat on 2026-09-16;
- strict errors when a requested period has not yet been mirrored.

Verified Muscat record for 2026-09-16:

| Prayer | Time |
|---|---:|
| Fajr | 04:38 |
| Sunrise | 05:54 |
| Dhuhr | 12:07 |
| Asr | 15:34 |
| Maghrib | 18:15 |
| Isha | 19:26 |

The API does **not** fabricate prayer times for dates or locations that are not present in the committed static mirror. Missing coverage returns:

```json
{
  "error": "Official MARA mirror is not available for the requested period"
}
```

## Data structure

```text
data/
  locations.json
  2026/
    09.json
api/
  prayer-times.js
```

Additional verified months and locations can be added by extending the JSON mirror without changing the API contract.

## Source

MARA published prayer timetable:

```text
https://www.mara.gov.om/calendar_page2.asp
```

Runtime requests read the committed JSON mirror rather than querying MARA on every page load.

## Notes

- Prayer values are Athan times, not mosque-specific Iqamah times.
- Mosque-specific Iqamah rules belong in the consuming application.
- Location keys exposed by this API are the only location values the prayer-times app should accept.
- All prayer values use 24-hour `HH:mm` format.

See [docs/API.md](docs/API.md) for the API contract.
