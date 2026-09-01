# syntax=docker/dockerfile:1

# --- builder: resolve & install deps with uv, isolated from the runtime image ---
FROM ghcr.io/astral-sh/uv:0.5-python3.12-bookworm-slim AS builder

WORKDIR /rpi-dht

# Build deps needed only to compile a couple of native extensions (e.g. lgpio).
# Removed again after `uv sync` so they never reach the runtime image.
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y gcc libc6-dev libgpiod2 && \
    rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy only the manifest/lock first so dependency install is cached
# independently of application code changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY main.py config.py ./
COPY utils utils
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- runtime: slim image, no compilers ---
FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y libgpiod2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /rpi-dht

COPY --from=builder /rpi-dht /rpi-dht

# Runs as root, intentionally: `lgpio` creates a notification FIFO
# (.lgd-nfy0) in the working directory at import time, and needs direct
# access to /dev/gpiochip*. Both break under a non-root user in ways that
# don't resolve just by chown'ing files (see the "xCreatePipe" / "No such
# file or directory" crash if you try switching this to USER app). Since
# the compose file already runs this container with `privileged: true`
# for GPIO access, a non-root user here isn't buying real isolation
# anyway — so root keeps the one thing that actually needs unrestricted
# hardware access working.
ENV PATH="/rpi-dht/.venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "-u", "main.py"]
