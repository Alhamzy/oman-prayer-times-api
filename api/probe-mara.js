module.exports = async function handler(req, res) {
  try {
    const r = await fetch("https://www.mara.gov.om/calendar_page2.asp", {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; OmanPrayerTimesMirror/1.0)" },
    });
    const html = await r.text();

    const forms = [...html.matchAll(/<form\b[\s\S]*?<\/form>/gi)].map(m => m[0]);
    const compact = forms.map((form, i) => ({
      index: i,
      openTag: (form.match(/<form\b[^>]*>/i) || [""])[0],
      selects: [...form.matchAll(/<select\b[^>]*>[\s\S]*?<\/select>/gi)].map(x => x[0]),
      inputs: [...form.matchAll(/<input\b[^>]*>/gi)].map(x => x[0]),
    }));

    res.status(200).json({
      upstreamStatus: r.status,
      finalUrl: r.url,
      formCount: forms.length,
      forms: compact,
      head: html.slice(0, 4000),
    });
  } catch (e) {
    res.status(500).json({ error: String(e && e.stack || e) });
  }
};
