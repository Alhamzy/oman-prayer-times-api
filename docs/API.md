# API Reference

## Endpoint

```http
GET /api/prayer-times
```

Production:

```text
https://oman-prayer-times-api.vercel.app/api/prayer-times
```

The endpoint supports four query modes.

## 1. List locations

```http
GET /api/prayer-times?locations=true
```

Returns the location keys currently exposed by the API. The consuming prayer-times application must use these keys rather than accepting free-text locations.

## 2. Single date

```http
GET /api/prayer-times?city=muscat&date=2026-09-16
```

Parameters:
- `city`: optional, defaults to `muscat`
- `location`: optional alias for `city`
- `date`: `YYYY-MM-DD`

Successful response:

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
  "lastUpdated": "ISO-8601 timestamp",
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

## 3. Single month

```http
GET /api/prayer-times?city=muscat&year=2026&month=9
```

Returns the committed records for that location/month.

## 4. Month range

```http
GET /api/prayer-times?city=muscat&year=2026&fromMonth=9&toMonth=12
```

Returns each mirrored month in the requested range. The entire request fails if a requested month/location has not yet been mirrored.

## Time format

All prayer values use 24-hour `HH:mm`.

## Errors

Invalid date:

```json
{"error":"date must be YYYY-MM-DD"}
```

Invalid month:

```json
{"error":"Invalid month"}
```

Unknown location:

```json
{"error":"Unknown location: example"}
```

Missing static mirror:

```json
{"error":"Official MARA mirror is not available for the requested period"}
```

## Current coverage note

The API implementation is live, but the committed timetable mirror is intentionally bootstrap-sized until additional MARA records are verified and committed. The service never invents missing prayer times.

## Source

Oman Ministry of Endowments and Religious Affairs (MARA):

```text
https://www.mara.gov.om/calendar_page2.asp
```

This API is an independent wrapper/mirror and is not an official Ministry API.
