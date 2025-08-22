// api/weather.js
export default async function handler(req, res) {
  try {
    const { lat, lon, q } = req.query;
    const key = process.env.OPENWEATHER_API_KEY;
    if (!key) return res.status(500).json({ error: "Missing server key" });

    const params = new URLSearchParams({ appid: key, units: "metric", lang: "he" });
    if (lat && lon) { params.set("lat", lat); params.set("lon", lon); }
    else if (q) { params.set("q", q); }
    else { return res.status(400).json({ error: "Provide lat and lon or q" }); }

    const r = await fetch(`https://api.openweathermap.org/data/2.5/weather?${params.toString()}`);
    if (!r.ok) return res.status(r.status).json({ error: await r.text() });
    const d = await r.json();

    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=60");
    return res.json({
      name: d.name,
      country: d.sys?.country,
      temp: Math.round(d.main?.temp),
      feels_like: Math.round(d.main?.feels_like),
      condition: d.weather?.[0]?.description,
      icon: d.weather?.[0]?.icon,
      wind_speed: d.wind?.speed,
      wind_deg: d.wind?.deg,
      clouds: d.clouds?.all
    });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
