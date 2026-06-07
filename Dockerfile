FROM python:3.12-slim-bookworm

WORKDIR /rpi-dht

COPY pyproject.toml uv.lock ./

RUN apt-get update -y && \
	apt-get upgrade -y && \
	apt-get install -y gcc libc6-dev libgpiod2 && \
	python -m pip install --no-cache-dir -U pip uv && \
	uv sync && \
	apt-get remove --purge -y gcc libc6-dev && \
	apt-get autoremove -y && \
	rm -rf /var/lib/apt/lists/*

COPY main.py config.py .
COPY utils utils

RUN chmod +rx main.py config.py

ENTRYPOINT [ "uv", "run", "python", "-u", "main.py" ]
