# Oman Prayer Times API

A lightweight JSON API for **official Oman prayer times**, sourced from the published timetable of the **Oman Ministry of Endowments and Religious Affairs (MARA)**.

The API currently mirrors **86 Oman locations** and supports prayer-time lookup by **date, month, or month range**.

> This is an independent API wrapper/mirror. It is not an official Ministry API.

## Base URL

Use the deployed application host followed by:

```text
/api/prayer-times
```

Example:

```text
https://<your-domain>/api/prayer-times
```

## Quick examples

### Prayer times for one date

```http
GET /api/prayer-times?city=muscat&date=2026-09-16
```

Example response:

```json
{
  "source": {
    "name": "Oman Ministry of Endowments and Religious Affairs (MARA)",
    "url": "https://www.mara.gov.om/calendar_page2.asp",
    "country": "Oman"
  },
  "location": {
    "key": "muscat",
    "name": "Muscat"
  },
  "lastUpdated": "2026-09-16T12:37:54.040568+00:00",
  "data": {
    "date": "2026-09-16",
    "fajr": "04:38",
    "sunrise": "05:54",
    "dhuhr": "12:07",
    "asr": "15:34",
    "maghrib": "18:15",
    "isha": "19:26"
  }
}
```

### One month

```http
GET /api/prayer-times?city=nizwa&year=2026&month=10
```

### Several months

```http
GET /api/prayer-times?city=sohar&year=2026&fromMonth=9&toMonth=12
```

### List supported locations

```http
GET /api/prayer-times?locations=true
```

## Query parameters

| Parameter | Required | Description |
|---|---:|---|
| `city` | No | MARA location key, e.g. `muscat`, `salalah`, `nizwa`, `sohar`. Defaults to `muscat`. |
| `location` | No | Alias for `city`. |
| `date` | No | Single date in `YYYY-MM-DD` format. |
| `year` | No | Year to query. Current mirrored dataset: `2026`. |
| `month` | No | One month, `1`–`12`. |
| `fromMonth` | No | First month in a range. |
| `toMonth` | No | Last month in a range. |
| `locations` | No | Set to `true` to list all supported MARA location keys. |

## Current coverage

The current mirror contains **September through December 2026** for all locations exposed by MARA's timetable selector.

Examples include:

`muscat`, `salalah`, `nizwa`, `sohar`, `sur`, `ibri`, `buraimi`, `al-duqm`, `barka`, `bahla`, `quriyat`, `samail`, `suwaiq`, `shinas`, `liwa`, `masirah`, `mirbat`, `taqah`, `yanqul`, and others.

Use:

```http
GET /api/prayer-times?locations=true
```

to get the authoritative list supported by the current mirror.

## Prayer fields

Every daily record contains:

- `fajr`
- `sunrise`
- `dhuhr`
- `asr`
- `maghrib`
- `isha`

All times are normalized to **24-hour `HH:mm` format** in Oman local prayer-time context.

## Errors

Typical errors return JSON with an `error` field.

Example:

```json
{
  "error": "Unknown location: xyz"
}
```

Common causes:

- unsupported location key
- invalid date format
- invalid month
- requested year/month not present in the current mirror

## Data source and refresh

The source of truth is the public MARA prayer timetable:

```text
https://www.mara.gov.om/calendar_page2.asp
```

A scraper discovers MARA's available locations, reads the published timetable, normalizes it, validates known values, and commits a static JSON mirror.

The mirror is refreshed automatically with **GitHub Actions**. Runtime API calls read from the local mirror instead of querying MARA on every request.

This makes the API:

- fast
- free-tier friendly
- resilient to MARA downtime
- consistent with the official published timetable

## Validation

Muscat is checked against the known official value for **2026-09-16**:

| Prayer | Time |
|---|---:|
| Fajr | 04:38 |
| Sunrise | 05:54 |
| Dhuhr | 12:07 |
| Asr | 15:34 |
| Maghrib | 18:15 |
| Isha | 19:26 |

## Notes

- Prayer times are **adhan times**, not mosque-specific iqamah times.
- Mosque iqamah offsets should be applied separately in the consuming application.
- Supported locations follow MARA's own location names and keys.
- This project does not calculate prayer times astronomically; it mirrors the Ministry's published timetable.

For endpoint details and response shapes, see [API.md](docs/API.md).
