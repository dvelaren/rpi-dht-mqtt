"""Shared constants: GPIO pin lookup and MQTT reconnect tuning."""

import board

# Maps "D0".."D27" -> the corresponding board pin object, so main.py can
# look up a pin by the numeric GPIO value coming from settings.dht_pin.
boardspins = {f"D{i}": getattr(board, f"D{i}") for i in range(28)}

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
