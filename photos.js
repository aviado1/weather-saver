// api/photos.js
export default async function handler(req, res) {
  try {
    const query = req.query.q || "city skyline";
    const key = process.env.PEXELS_API_KEY;
    if (!key) return res.status(500).json({ error: "Missing Pexels key" });

    const url = `https://api.pexels.com/v1/search?${new URLSearchParams({
      query,
      orientation: "landscape",
      size: "large",
      per_page: "12"
    }).toString()}`;

    const r = await fetch(url, { headers: { Authorization: key } });
    if (!r.ok) return res.status(r.status).json({ error: await r.text() });
    const data = await r.json();

    const photos = (data.photos || []).map(p => ({
      url: p.src?.landscape || p.src?.large || p.src?.original,
      alt: p.alt || "Photo",
      photographer: p.photographer,
      photographer_url: p.photographer_url
    }));

    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=60");
    return res.json({ photos });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
