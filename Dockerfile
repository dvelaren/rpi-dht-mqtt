FROM python:3.11-slim-bookworm

ENV ENVIRONMENT docker

WORKDIR /rpi-dht

COPY requirements.txt .

RUN pip install -U pip
RUN apt update && apt upgrade
RUN apt install gcc libc6-dev libgpiod2 -y
RUN pip install --no-cache-dir RPi.GPIO
RUN pip install --no-cache-dir adafruit-blinka
RUN pip install --no-cache-dir adafruit-circuitpython-dht
RUN pip install --no-cache-dir -r requirements.txt

RUN apt remove --purge -y gcc libc6-dev
RUN apt autoremove -y

COPY main.py config.py .
COPY utils utils

ENTRYPOINT [ "python", "-u", "main.py" ]