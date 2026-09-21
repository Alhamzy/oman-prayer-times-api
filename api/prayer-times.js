const fs = require("fs");
const path = require("path");

const SOURCE = {
  name: "Oman Ministry of Endowments and Religious Affairs (MARA)",
  url: "https://www.mara.gov.om/calendar_page2.asp",
  country: "Oman",
};

const ROOT = process.cwd();
const LOCATIONS_PATH = path.join(ROOT, "data", "locations.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function send(res, status, body) {
  res.status(status).setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "public, s-maxage=300, stale-while-revalidate=86400");
  return res.end(JSON.stringify(body));
}

function normalizeLocationKey(value) {
  return String(value || "muscat").trim().toLowerCase();
}

function parseMonth(value) {
  const n = Number(value);
  return Number.isInteger(n) && n >= 1 && n <= 12 ? n : null;
}

function monthFile(year, month) {
  return path.join(ROOT, "data", String(year), String(month).padStart(2, "0") + ".json");
}

function loadMonth(year, month) {
  const file = monthFile(year, month);
  if (!fs.existsSync(file)) return null;
  return readJson(file);
}

function locationByKey(locations, key) {
  return locations.find((x) => x.key === key) || null;
}

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return send(res, 405, { error: "Method not allowed" });
  }

  const locations = readJson(LOCATIONS_PATH);

  if (String(req.query.locations || "").toLowerCase() === "true") {
    return send(res, 200, {
      source: SOURCE,
      lastUpdated: "2026-09-21T00:00:00Z",
      locations,
    });
  }

  const key = normalizeLocationKey(req.query.city || req.query.location);
  const location = locationByKey(locations, key);
  if (!location) return send(res, 404, { error: `Unknown location: ${key}` });

  if (req.query.date) {
    const date = String(req.query.date);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      return send(res, 400, { error: "date must be YYYY-MM-DD" });
    }
    const [yearStr, monthStr] = date.split("-");
    const year = Number(yearStr);
    const month = Number(monthStr);
    const mirror = loadMonth(year, month);
    if (!mirror || !Array.isArray(mirror[key])) {
      return send(res, 404, { error: "Official MARA mirror is not available for the requested period" });
    }
    const record = mirror[key].find((x) => x.date === date);
    if (!record) {
      return send(res, 404, { error: "Official MARA mirror is not available for the requested period" });
    }
    return send(res, 200, {
      source: SOURCE,
      location,
      lastUpdated: "2026-09-21T00:00:00Z",
      data: record,
    });
  }

  const year = Number(req.query.year);
  if (!Number.isInteger(year)) {
    return send(res, 400, { error: "year is required for month or month-range queries" });
  }

  if (req.query.month != null) {
    const month = parseMonth(req.query.month);
    if (!month) return send(res, 400, { error: "Invalid month" });
    const mirror = loadMonth(year, month);
    if (!mirror || !Array.isArray(mirror[key])) {
      return send(res, 404, { error: "Official MARA mirror is not available for the requested period" });
    }
    return send(res, 200, {
      source: SOURCE,
      location,
      year,
      month,
      lastUpdated: "2026-09-21T00:00:00Z",
      data: mirror[key],
    });
  }

  if (req.query.fromMonth != null || req.query.toMonth != null) {
    const fromMonth = parseMonth(req.query.fromMonth);
    const toMonth = parseMonth(req.query.toMonth);
    if (!fromMonth || !toMonth || fromMonth > toMonth) {
      return send(res, 400, { error: "Invalid month range" });
    }

    const months = [];
    for (let month = fromMonth; month <= toMonth; month += 1) {
      const mirror = loadMonth(year, month);
      if (!mirror || !Array.isArray(mirror[key])) {
        return send(res, 404, { error: "Official MARA mirror is not available for the requested period" });
      }
      months.push({ month, data: mirror[key] });
    }

    return send(res, 200, {
      source: SOURCE,
      location,
      year,
      fromMonth,
      toMonth,
      lastUpdated: "2026-09-21T00:00:00Z",
      months,
    });
  }

  return send(res, 400, {
    error: "Provide locations=true, date=YYYY-MM-DD, month, or fromMonth/toMonth",
  });
};
