#!/bin/sh
# entrypoint.sh

# Default port
: "${APP_PORT:=6978}"

echo "Starting previewproxy on port $APP_PORT..."

# Run UV / Flask app binding to 0.0.0.0
exec uv run main.py --host 0.0.0.0 --port "$APP_PORT"