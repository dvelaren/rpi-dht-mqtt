import os
import logging
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
    LOGGING_LEVEL = logging.INFO

class DevelopmentConfig(Config):
    """Development configuration."""
    LOGGING_LEVEL = logging.DEBUG

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