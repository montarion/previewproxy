# Use your UV base image
FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Copy UV binaries (from previous image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy app source code
COPY . .

# Install dependencies
RUN uv sync --locked --no-dev

# Expose the port the Flask app listens on
EXPOSE 6978

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use entrypoint
ENTRYPOINT ["/entrypoint.sh"]