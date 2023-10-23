FROM python:3.10-alpine

ENV ENVIRONMENT docker

WORKDIR /rpi-dht

COPY requirements.txt .

RUN pip install -U pip
RUN apk update && apk upgrade
RUN apk add --no-cache gcc libc-dev libgpiod
RUN pip install --no-cache-dir rpi.gpio
RUN pip install --no-cache-dir adafruit-circuitpython-dht
# RUN pip install --no-cache-dir Adafruit-Blinka
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del --no-network --purge gcc libc-dev

COPY main.py config.py utils.py .
# RUN chmod +x /rpi-dht/*.py

# Hack
# RUN wget https://github.com/adafruit/Adafruit_Blinka/raw/main/src/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein64
# RUN cp libgpiod_pulsein64 /usr/local/lib/python3.10/site-packages/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein64
# RUN chmod u=rwx,g=rwx,o=rwx /usr/local/lib/python3.10/site-packages/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein64

ENTRYPOINT [ "python", "-u", "./main.py" ]