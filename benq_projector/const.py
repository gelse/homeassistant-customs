"""Use serial protocol of Acer projector to obtain state of the projector."""
from __future__ import annotations

from typing import Final

from homeassistant.const import STATE_OFF, STATE_ON

CONF_WRITE_TIMEOUT: Final = "write_timeout"
CONF_BAUDRATE: Final = "baudrate"
CONF_TIMEOUT: Final = "timeout"
CONF_SOCKET: Final = "socket"

DEFAULT_NAME: Final = "Benq Projector"
DEFAULT_TIMEOUT: Final = 4
DEFAULT_WRITE_TIMEOUT: Final = 4

DEFAULT_BAUDRATE: Final = 9600

ICON: Final = "mdi:projector"

# attributes
LAMP: Final = "Lamp"
LAMP_HOURS: Final = "Lamp Hours"
INPUT_SOURCE: Final = "Input Source"
MODEL: Final = "Model"
LAMP_MODE: Final = "Lamp Mode"
