from __future__ import annotations

from unittest.mock import MagicMock, patch

from paho.mqtt.enums import MQTTErrorCode
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.reasoncodes import ReasonCode

from utils.utils import connect_mqtt, on_disconnect, publish


def test_connect_mqtt_sets_credentials_and_connects() -> None:
    with patch("utils.utils.mqtt_client.Client") as client_cls:
        client = client_cls.return_value
        result = connect_mqtt("client-1", "broker.local", 1883, "user", "pass")

        client.username_pw_set.assert_called_once_with("user", "pass")
        client.connect.assert_called_once_with("broker.local", 1883)
        assert result is client


def test_connect_mqtt_skips_credentials_when_no_username() -> None:
    with patch("utils.utils.mqtt_client.Client") as client_cls:
        client = client_cls.return_value
        connect_mqtt("client-1", "broker.local", 1883, None, None)
        client.username_pw_set.assert_not_called()


def test_publish_logs_success(caplog) -> None:
    client = MagicMock()
    client.publish.return_value.rc = MQTTErrorCode.MQTT_ERR_SUCCESS
    with caplog.at_level("INFO"):
        publish(client, "topic/x", '{"temperature": 21.0}')
    assert "Sent" in caplog.text


def test_publish_logs_failure(caplog) -> None:
    client = MagicMock()
    client.publish.return_value.rc = MQTTErrorCode.MQTT_ERR_NO_CONN
    with caplog.at_level("ERROR"):
        publish(client, "topic/x", "{}")
    assert "Failed to send message" in caplog.text


def test_on_disconnect_accepts_v2_callback_signature() -> None:
    """Regression test for the VERSION2 callback signature bug: paho-mqtt
    2.x calls on_disconnect with 5 positional args, not 3."""
    client = MagicMock()
    client.reconnect.return_value = None
    unexpected = ReasonCode(PacketTypes.DISCONNECT, "Unspecified error")
    on_disconnect(
        client, None, disconnect_flags=MagicMock(), reason_code=unexpected, properties=None
    )
    client.reconnect.assert_called_once()


def test_on_disconnect_skips_reconnect_on_clean_shutdown(caplog) -> None:
    """Regression test: reason code 0 ("Normal disconnection") is what we
    get back from our own client.disconnect() call during graceful
    shutdown. Reconnecting at that point just opens a connection that's
    immediately abandoned when the process exits."""
    client = MagicMock()
    clean = ReasonCode(PacketTypes.DISCONNECT, "Normal disconnection")
    with caplog.at_level("INFO"):
        on_disconnect(
            client, None, disconnect_flags=MagicMock(), reason_code=clean, properties=None
        )
    client.reconnect.assert_not_called()
    assert "not attempting to reconnect" in caplog.text
