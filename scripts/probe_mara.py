from pathlib import Path
import requests

URL = "https://www.mara.gov.om/calendar_page2.asp"
headers = {"User-Agent": "Mozilla/5.0 (compatible; OmanPrayerTimesMirror/1.0)"}

r = requests.get(URL, headers=headers, timeout=30)
r.raise_for_status()
Path("mara_probe.html").write_text(r.text, encoding="utf-8")
print("status", r.status_code)
print("url", r.url)
print("bytes", len(r.text.encode("utf-8")))
print(r.text[:20000])
