import json
import os
import time
import threading
import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

CACHE_FILE = "cache.json"
CACHE_TTL = 60 * 60  # 1 hour (set to None to disable expiry)

lock = threading.Lock()

# Load cache at startup
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


ogtypes = ["title", "description", "image", "url"]

@app.route("/url/<path:url>")
def readurl(url):
    now = time.time()

    with lock:
        cached = cache.get(url)

        if cached:
            if CACHE_TTL is None or now - cached["timestamp"] < CACHE_TTL:
                return jsonify(cached["data"])

    # Not cached or expired → fetch
    page = requests.get(url, headers=headers, timeout=10).text
    print("fetched")
    soup = BeautifulSoup(page, features="html.parser")

    resdict = {}
    for t in ogtypes:
        res = soup.find("meta", property=f"og:{t}")
        resdict[t] = res["content"] if res else None

    # Save to cache
    with lock:
        cache[url] = {
            "timestamp": now,
            "data": resdict,
        }
        save_cache()

    return jsonify(resdict)

app.run("0.0.0.0", 6978, debug=True)