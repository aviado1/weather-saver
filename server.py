from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from this folder
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

app = Flask(__name__, static_folder=".", static_url_path="")

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY") or ""
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY") or ""

@app.route("/api/weather")
def api_weather():
    q = request.args.get("q")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "Missing OpenWeather API key"}), 500

    params = {"appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "en"}
    if q:
        params["q"] = q
    elif lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    else:
        return jsonify({"error": "Provide city name or coordinates"}), 400

    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=15)
        if r.status_code != 200:
            return jsonify({"error": r.text}), r.status_code
        d = r.json()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

    out = {
        "name": d.get("name"),
        "country": d.get("sys", {}).get("country"),
        "temp": round(d.get("main", {}).get("temp", 0)),
        "feels_like": round(d.get("main", {}).get("feels_like", 0)),
        "condition": (d.get("weather") or [{}])[0].get("description"),
        "icon": (d.get("weather") or [{}])[0].get("icon"),
        "wind_speed": d.get("wind", {}).get("speed"),
        "wind_deg": d.get("wind", {}).get("deg"),
        "clouds": d.get("clouds", {}).get("all"),
    }
    return jsonify(out)

@app.route("/api/photos")
def api_photos():
    q = request.args.get("q", "city skyline")

    # If no Pexels key, return a placeholder image list so the UI still works
    if not PEXELS_API_KEY:
        photos = [{
            "url": f"https://picsum.photos/seed/{q.replace(' ', '%20')}/1920/1080",
            "alt": "Placeholder photo",
            "photographer": "Picsum",
            "photographer_url": "https://picsum.photos"
        }]
        return jsonify({"photos": photos})

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": q, "orientation": "landscape", "size": "large", "per_page": 14}

    try:
        r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        if r.status_code != 200:
            return jsonify({"error": r.text}), r.status_code
        data = r.json()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

    photos = []
    for p in data.get("photos", []):
        src = p.get("src", {})
        url = src.get("landscape") or src.get("large") or src.get("original")
        if not url:
            continue
        photos.append({
            "url": url,
            "alt": p.get("alt") or "Photo",
            "photographer": p.get("photographer"),
            "photographer_url": p.get("photographer_url")
        })

    if not photos:
        photos = [{
            "url": f"https://picsum.photos/seed/{q.replace(' ', '%20')}/1920/1080",
            "alt": "Placeholder photo",
            "photographer": "Picsum",
            "photographer_url": "https://picsum.photos"
        }]

    return jsonify({"photos": photos})

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    print("DEBUG env path:", ENV_PATH)
    print("DEBUG OW key length:", len(OPENWEATHER_API_KEY))
    print("DEBUG PEXELS key length:", len(PEXELS_API_KEY))
    app.run(host="0.0.0.0", port=5000, debug=True)
