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

LAMP_MODE: Final = "Lamp Mode"

ICON: Final = "mdi:projector"

INPUT_SOURCE: Final = "Input Source"

LAMP: Final = "Lamp"
LAMP_HOURS: Final = "Lamp Hours"

MODEL: Final = "Model"

# Commands known to the projector
CMD_DICT: Final[dict[str, str]] = {
    LAMP: "\r*pow=?#\r",
    LAMP_HOURS: "\r*ltim=?#\r",
    INPUT_SOURCE: "\r*sour=?#\r",
    LAMP_MODE: "\r*lampm=?#\r",
    MODEL: "\r*modelname=?#\r",
    STATE_ON: "\r*pow=on#\r",
    STATE_OFF: "\r*pow=off#\r",
}
