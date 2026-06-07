FROM python:3.12-alpine

ENV ENVIRONMENT docker

WORKDIR /rpi-dht

COPY pyproject.toml uv.lock ./

RUN python -m pip install --no-cache-dir -U pip uv && \
	apk update && apk upgrade && \
	apk add --no-cache gcc libc-dev libgpiod && \
	uv sync && \
	apk del --no-network --purge gcc libc-dev && \
	rm -rf /var/cache/apk/*

COPY main.py config.py utils.py .

ENTRYPOINT [ "uv", "run", "python", "-u", "./main.py" ]