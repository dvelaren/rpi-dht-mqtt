"""Test fixtures.

`board` and `adafruit_dht` only import successfully on real Raspberry Pi
hardware (they probe /proc/cpuinfo, GPIO chips, etc. at import time). We
stub both modules in `sys.modules` *before* any of our own modules import
them, so the whole test suite can run on a laptop or in CI.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

# Stubbed at import time (not inside a fixture): pytest imports every test
# module during collection, and those modules import `utils.constants`,
# which imports the real `board` package at module scope. The stub has to
# exist in sys.modules before that first import happens, or collection
# itself fails on non-Raspberry-Pi machines (dev laptops, CI).
_board_stub = types.ModuleType("board")
for _i in range(28):
    setattr(_board_stub, f"D{_i}", _i)

_dht_stub = types.ModuleType("adafruit_dht")
_dht_stub.DHTBase = MagicMock  # type: ignore[attr-defined]
_dht_stub.DHT11 = MagicMock  # type: ignore[attr-defined]
_dht_stub.DHT22 = MagicMock  # type: ignore[attr-defined]

sys.modules.setdefault("board", _board_stub)
sys.modules.setdefault("adafruit_dht", _dht_stub)
