import os
import logging
from logging import StreamHandler
from dotenv import load_dotenv

load_dotenv()

class Config:
    READ_TIME = os.environ.get("READ_TIME") or 5
    DHT_PIN = os.environ.get("DHT_PIN") or 17
    MQTT_BROKER = os.environ.get("MQTT_BROKER") or "localhost"
    MQTT_PORT = os.environ.get("MQTT_PORT") or 1883
    MQTT_TOPIC = os.environ.get("MQTT_TOPIC") or "/devices/rpi-casa"
    MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID") or "rpi-dvelas25"
    MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
    MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
    logging.basicConfig(
        format="|%(asctime)s| [%(levelname)s] {%(module)s->%(funcName)s}: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %Z",
        level=logging.INFO,
        handlers=[StreamHandler()],
    )

class DevelopmentConfig(Config):
    """Development configuration."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

class ProductionConfig(Config):
    """Production configuration."""
    pass

class DockerConfig(Config):
    """Docker configuration."""
    pass

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "docker": DockerConfig,
    "default": DevelopmentConfig,
}