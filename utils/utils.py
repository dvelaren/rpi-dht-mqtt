"""MQTT connection helpers."""

from __future__ import annotations

import logging
import time

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import CallbackAPIVersion, DisconnectFlags, MQTTMessageInfo
from paho.mqtt.enums import MQTTErrorCode
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from utils.constants import (
    FIRST_RECONNECT_DELAY,
    MAX_RECONNECT_COUNT,
    MAX_RECONNECT_DELAY,
    RECONNECT_RATE,
)

logger = logging.getLogger(__name__)


def connect_mqtt(
    client_id: str,
    broker: str,
    port: int,
    username: str | None,
    password: str | None,
) -> mqtt_client.Client:
    def on_connect(
        client: mqtt_client.Client,
        userdata: object,
        flags: object,
        reason_code: ReasonCode,
        properties: Properties | None,
    ) -> None:
        if reason_code == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, reason code: %s", reason_code)

    client = mqtt_client.Client(CallbackAPIVersion.VERSION2, client_id)
    if username is not None:
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client: mqtt_client.Client, topic: str, msg: str) -> None:
    result: MQTTMessageInfo = client.publish(topic, msg)
    if result.rc == MQTTErrorCode.MQTT_ERR_SUCCESS:
        logger.info("Sent `%s` to topic `%s`", msg, topic)
    else:
        logger.error("Failed to send message to topic %s (rc=%s)", topic, result.rc)


def on_disconnect(
    client: mqtt_client.Client,
    userdata: object,
    disconnect_flags: DisconnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None = None,
) -> None:
    # NOTE: with CallbackAPIVersion.VERSION2, paho-mqtt 2.x invokes this
    # callback with 5 positional args (client, userdata, disconnect_flags,
    # reason_code, properties). The old 3-arg signature (client, userdata, rc)
    # raised TypeError as soon as a disconnect actually happened.
    logger.info("Disconnected with reason code: %s", reason_code)

    # Reason code 0 ("Normal disconnection") is what we get back from our
    # own call to client.disconnect() during a graceful shutdown — not a
    # dropped connection. Reconnecting in that case just opens a new
    # connection that immediately gets abandoned when the process exits.
    # Only unexpected disconnects (dropped network, broker restart, etc.)
    # should trigger the retry loop.
    if reason_code == 0:
        logger.info("Clean disconnect, not attempting to reconnect.")
        return

    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logger.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logger.info("Reconnected successfully!")
            return
        except OSError as err:
            logger.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay = min(reconnect_delay * RECONNECT_RATE, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logger.error("Reconnect failed after %s attempts. Exiting...", reconnect_count)
