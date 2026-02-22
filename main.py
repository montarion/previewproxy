import json
import os
import time
import threading
import requests
import socket
import ipaddress
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

CACHE_FILE = "cache.json"
CACHE_TTL = 60 * 60  # 1 hour

lock = threading.Lock()

# Load cache
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

# ─────────────────────────────────────
# Security: Block private/internal IPs
# ─────────────────────────────────────
def is_safe_url(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)

        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_reserved
            or ip_obj.is_link_local
        ):
            return False

        return True

    except Exception:
        return False


# ─────────────────────────────────────
# OG Metadata Endpoint
# GET /preview?url=https://...
# ─────────────────────────────────────
@app.route("/preview")
def preview():
    url = request.args.get("url")
    if not url or not is_safe_url(url):
        return jsonify({"error": "Invalid or unsafe URL"}), 400

    now = time.time()

    with lock:
        cached = cache.get(url)
        if cached:
            if CACHE_TTL is None or now - cached["timestamp"] < CACHE_TTL:
                return jsonify(cached["data"])

    try:
        page = requests.get(
            url, headers=headers, allow_redirects=True, timeout=10
        ).text

        soup = BeautifulSoup(page, "html.parser")

        def get_meta(prop):
            tag = soup.find("meta", property=f"og:{prop}")
            return tag["content"] if tag and tag.get("content") else None

        title = (
            get_meta("title")
            or soup.find("title").text.strip()
            if soup.find("title")
            else None
        )

        resdict = {
            "title": title,
            "description": get_meta("description"),
            "image": get_meta("image"),
            "url": get_meta("url") or url,
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    with lock:
        cache[url] = {
            "timestamp": now,
            "data": resdict,
        }
        save_cache()

    return jsonify(resdict)


# ─────────────────────────────────────
# Image Proxy Endpoint
# GET /image?url=https://...
# ─────────────────────────────────────
@app.route("/image")
def image_proxy():
    url = request.args.get("url")
    if not url or not is_safe_url(url):
        return jsonify({"error": "Invalid or unsafe URL"}), 400

    try:
        r = requests.get(
            url,
            headers=headers,
            allow_redirects=True,
            timeout=10,
            stream=True
        )

        content_type = r.headers.get("Content-Type", "image/svg")
        r.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        return Response(
            r.iter_content(chunk_size=8192),
            content_type=content_type,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run("0.0.0.0", 6978, debug=True)