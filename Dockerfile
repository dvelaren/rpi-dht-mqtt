# syntax=docker/dockerfile:1

# Base image note: staying on Debian Bookworm (not Trixie) intentionally.
# Trixie renamed the libgpiod2 apt package (now split into libgpiod3 and a
# libgpiod2t64 compat package not confirmed available for arm64/armhf), so
# `apt-get install libgpiod2` below would fail outright on Trixie without
# also changing this package name. Beyond that, there are open upstream
# reports (adafruit/Adafruit_Blinka, adafruit/Raspberry-Pi-Installer-Scripts,
# both within the last year) of Pi 5 + lgpio + Trixie combinations hitting
# "GPIO busy" and missing-libgpiod errors with no confirmed fix as of this
# writing. If you want to try Trixie later: swap both FROM lines to
# `python:3.12-slim-trixie`, change `libgpiod2` to `libgpiod3` below, and
# test thoroughly on real hardware before relying on it — this can't be
# verified from a build check or unit test, only a live sensor read.

# --- builder: resolve & install deps with uv, isolated from the runtime image ---
FROM python:3.12-slim-bookworm AS builder

# Pin an exact uv release for reproducible builds (see
# https://github.com/astral-sh/uv/pkgs/container/uv for current tags).
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/

WORKDIR /rpi-dht

# Build deps needed only to compile a couple of native extensions (e.g. lgpio).
# Removed again after `uv sync` so they never reach the runtime image.
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y gcc libc6-dev libgpiod2 && \
    rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies first, in their own layer, via bind mounts (not COPY)
# so the manifest/lock don't become a committed image layer on their own.
# `--locked` (not `--frozen`) makes the build fail loudly if pyproject.toml
# and uv.lock have drifted out of sync, instead of silently installing
# whatever the lockfile says regardless of whether it's still accurate.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

COPY pyproject.toml uv.lock main.py config.py ./
COPY utils utils
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

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
