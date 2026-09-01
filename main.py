"""Entry point: reads a DHT sensor on a loop and publishes to MQTT."""

from __future__ import annotations

import json
import logging
import signal
import time
from logging import StreamHandler
from types import FrameType

import adafruit_dht
from adafruit_dht import DHTBase

from config import DHTType, settings
from utils.constants import boardspins
from utils.utils import connect_mqtt, on_disconnect, publish

logging.basicConfig(
    format="|%(asctime)s| [%(levelname)s] {%(module)s->%(funcName)s}: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z",
    level=settings.logging_level,
    handlers=[StreamHandler()],
)

logger = logging.getLogger(__name__)

_shutdown_requested = False


def _handle_shutdown_signal(signum: int, frame: FrameType | None) -> None:
    """Flip a flag instead of raising, so the main loop exits cleanly and
    the `finally` block below always gets a chance to release the sensor
    and disconnect from MQTT (important under `docker stop`, which sends
    SIGTERM)."""
    global _shutdown_requested
    logger.info("Received signal %s, shutting down...", signum)
    _shutdown_requested = True


def build_sensor() -> DHTBase:
    pin = boardspins[f"D{settings.dht_pin}"]
    if settings.dht_type == DHTType.DHT22:
        return adafruit_dht.DHT22(pin)
    return adafruit_dht.DHT11(pin)


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)
    signal.signal(signal.SIGINT, _handle_shutdown_signal)

    logger.info("rpi-dht service started, refresh time %s secs", settings.read_time)

    client = connect_mqtt(
        settings.mqtt_client_id,
        settings.mqtt_broker,
        settings.mqtt_port,
        settings.mqtt_username,
        settings.mqtt_password,
    )
    client.on_disconnect = on_disconnect
    client.loop_start()

    sensor = build_sensor()
    try:
        while not _shutdown_requested:
            try:
                temperature = sensor.temperature
                humidity = sensor.humidity
            except RuntimeError as exc:
                # Transient one-wire read glitches are expected and routine
                # for DHT sensors; retry on the next tick instead of dying.
                logger.warning("Reading from DHT failed: %s", exc)
                time.sleep(settings.read_time)
                continue

            if temperature is None or humidity is None:
                logger.error("Failed reading DHT sensor")
            else:
                logger.debug("Temp: %.2f °C, Hum: %.2f %%", temperature, humidity)
                publish(
                    client,
                    settings.mqtt_topic,
                    json.dumps({"temperature": temperature, "humidity": humidity}),
                )
            time.sleep(settings.read_time)
    finally:
        sensor.exit()
        client.loop_stop()
        client.disconnect()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
