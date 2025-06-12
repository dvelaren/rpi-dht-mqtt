FROM python:3.12-slim-bookworm

WORKDIR /rpi-dht

COPY requirements.txt .

RUN apt-get update -y && \
	apt-get upgrade -y && \
	apt-get install gcc libc6-dev libgpiod2 -y && \
	pip install --no-cache-dir -U pip && \
	pip install --no-cache-dir -r requirements.txt

RUN	apt autoremove -y && \
	apt remove --purge -y gcc libc6-dev python3-rpi.gpio

COPY main.py config.py .

RUN chmod +rx main.py config.py
COPY utils utils

# Using `python -u` to disable output buffering, ensuring real-time logs for the application.
ENTRYPOINT [ "python", "-u", "main.py" ]
