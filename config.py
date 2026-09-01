"""Application configuration.

Environment variables are the single source of truth. pydantic-settings
validates and type-casts them once at import time, so the rest of the
codebase can trust `settings.read_time` is already an `int`, `settings.
dht_pin` is a valid GPIO number, etc., instead of re-parsing strings
everywhere.
"""

from __future__ import annotations

import logging
from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class DHTType(StrEnum):
    DHT11 = "DHT11"
    DHT22 = "DHT22"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    read_time: int = Field(default=5, ge=1, description="Seconds between sensor reads")
    dht_pin: int = Field(default=17, ge=0, le=27, description="BCM GPIO pin number")
    dht_type: DHTType = DHTType.DHT22

    mqtt_broker: str = "localhost"
    mqtt_port: int = Field(default=1883, ge=1, le=65535)
    mqtt_topic: str = "/devices/rpi-casa"
    mqtt_client_id: str = "rpi-dvelas25"
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    @property
    def logging_level(self) -> int:
        return logging.DEBUG if self.environment == Environment.DEVELOPMENT else logging.INFO


settings = Settings()
