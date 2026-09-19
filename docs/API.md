# API Reference

## Endpoint

```http
GET /api/prayer-times
```

The endpoint supports four main query modes.

---

## 1. List locations

```http
GET /api/prayer-times?locations=true
```

Returns all location keys available in the current MARA mirror.

Use the returned `key` as the `city` parameter in prayer-time requests.

---

## 2. Single date

```http
GET /api/prayer-times?city=salalah&date=2026-09-16
```

### Parameters

- `city`: optional, defaults to `muscat`
- `location`: optional alias for `city`
- `date`: required in this mode; format `YYYY-MM-DD`

### Response shape

```json
{
  "source": {
    "name": "Oman Ministry of Endowments and Religious Affairs (MARA)",
    "url": "https://www.mara.gov.om/calendar_page2.asp",
    "country": "Oman"
  },
  "location": {
    "key": "salalah",
    "name": "Salalah"
  },
  "lastUpdated": "ISO-8601 timestamp",
  "data": {
    "date": "2026-09-16",
    "fajr": "05:00",
    "sunrise": "06:12",
    "dhuhr": "12:24",
    "asr": "15:45",
    "maghrib": "18:31",
    "isha": "19:38"
  }
}
```

---

## 3. Single month

```http
GET /api/prayer-times?city=nizwa&year=2026&month=10
```

### Parameters

- `city`: optional; defaults to `muscat`
- `year`: year to read from the mirror
- `month`: integer from `1` to `12`

### Response shape

```json
{
  "source": { "...": "..." },
  "location": {
    "key": "nizwa",
    "name": "Nizwa"
  },
  "year": 2026,
  "month": 10,
  "lastUpdated": "ISO-8601 timestamp",
  "data": [
    {
      "date": "2026-10-01",
      "fajr": "HH:mm",
      "sunrise": "HH:mm",
      "dhuhr": "HH:mm",
      "asr": "HH:mm",
      "maghrib": "HH:mm",
      "isha": "HH:mm"
    }
  ]
}
```

---

## 4. Month range

```http
GET /api/prayer-times?city=sohar&year=2026&fromMonth=9&toMonth=12
```

### Parameters

- `city`: optional; defaults to `muscat`
- `year`: year to read from the mirror
- `fromMonth`: first month, `1`–`12`
- `toMonth`: final month, `1`–`12`

`fromMonth` must be less than or equal to `toMonth`.

### Response shape

```json
{
  "source": { "...": "..." },
  "location": {
    "key": "sohar",
    "name": "Sohar"
  },
  "year": 2026,
  "fromMonth": 9,
  "toMonth": 12,
  "lastUpdated": "ISO-8601 timestamp",
  "months": [
    {
      "month": 9,
      "data": []
    },
    {
      "month": 10,
      "data": []
    }
  ]
}
```

---

## Location behavior

Location matching is based on the keys generated from MARA's published location selector.

Examples:

```text
muscat
salalah
nizwa
sohar
sur
ibri
buraimi
al-duqm
quriyat
barka
bahla
samail
suwaiq
shinas
liwa
masirah
mirbat
taqah
yanqul
```

Call the locations endpoint instead of hard-coding the complete list:

```http
GET /api/prayer-times?locations=true
```

---

## Time format

All prayer values use:

```text
HH:mm
```

Example:

```text
04:38
18:15
19:26
```

Times represent MARA's published local prayer timetable for the selected Oman location.

---

## Error responses

### Invalid date

```json
{
  "error": "date must be YYYY-MM-DD"
}
```

### Invalid month

```json
{
  "error": "Invalid month"
}
```

### Unknown location

```json
{
  "error": "Unknown location: example"
}
```

### Data not mirrored

```json
{
  "error": "Official MARA mirror is not available for the requested period"
}
```

---

## Source

Oman Ministry of Endowments and Religious Affairs (MARA):

```text
https://www.mara.gov.om/calendar_page2.asp
```

This API is an independent wrapper/mirror and is **not an official Ministry API**.
