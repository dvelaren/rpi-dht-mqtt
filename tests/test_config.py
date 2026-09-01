from __future__ import annotations

import logging

from config import DHTType, Environment, Settings


def test_defaults() -> None:
    settings = Settings.model_construct()
    assert settings.read_time == 5
    assert settings.dht_pin == 17
    assert settings.dht_type == DHTType.DHT22
    assert settings.mqtt_port == 1883


def test_env_vars_are_cast_to_correct_types(monkeypatch) -> None:
    monkeypatch.setenv("READ_TIME", "10")
    monkeypatch.setenv("DHT_PIN", "4")
    monkeypatch.setenv("MQTT_PORT", "8883")
    settings = Settings()
    assert settings.read_time == 10
    assert isinstance(settings.read_time, int)
    assert settings.dht_pin == 4
    assert settings.mqtt_port == 8883


def test_logging_level_follows_environment() -> None:
    dev = Settings.model_construct(environment=Environment.DEVELOPMENT)
    prod = Settings.model_construct(environment=Environment.PRODUCTION)
    assert dev.logging_level == logging.DEBUG
    assert prod.logging_level == logging.INFO
