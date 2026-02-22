# preview proxy
Super simple proxy that lets you fetch whatever random website. Includes caching.

# Basic installation:

Nothing really, just run with uv:
```
uv run main.py
```

# Usage:
```
uv run main.py
```

And then on your website:

```javascript
preres = await fetch("[your domain]/preview?url=https://ogp.me")
res = await preres.json()
```

This results in

```json
{
  "description": "The Open Graph protocol enables any web page to become a rich object in a social graph.",
  "image": "https://ogp.me/logo.png",
  "title": "Open Graph protocol",
  "url": "https://ogp.me/"
}
```
# NOTE: nginx proxy

if you're behind nginx,  you MUST add the following to your configuration, inside the location block:

```
add_header 'Access-Control-Allow-Credentials' 'true';
add_header Cross-Origin-Resource-Policy cross-origin always;
```

## [TODO: explain that we can proxy images as well]
```javascript
img.src = "[your domain]/image?url=https%3A%2F%2Fogp.me%2Flogo.png"

```



# Docker

There's also a docker image here: [TODO: upload to image registry]

You can run it with the following command:

```bash
docker run -d -p [port]:6978 previewproxy
```

