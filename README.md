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
preres = await fetch("[your domain]/url/https://ogp.me")
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

# Docker

There's also a docker image here: [TODO: upload to image registry]

You can run it with the following command:

```bash
docker run -d -p [port]:6978 previewproxy
```

