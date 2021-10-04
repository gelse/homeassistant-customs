"""Use serial protocol of Acer projector to obtain state of the projector."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = 'socket_projector'

CONF_WRITE_TIMEOUT: Final = 'write_timeout'
CONF_BAUDRATE: Final = 'baudrate'
CONF_TIMEOUT: Final = 'timeout'
CONF_SOCKET: Final = 'socket'
CONF_NAME: Final = 'name'
CONF_ID: Final = 'id'

ICON: Final = 'mdi:projector'

CONF_COMMAND_TEMPLATE = 'command_template'

CONF_POW_ON_CMD = 'pow_on_command'
CONF_POW_OFF_CMD = 'pow_off_command'
CONF_POW_STATE_QRY = 'pow_state_query'
CONF_POW_STATE_TMPL = 'pow_state_template'
CONF_POW_ON_STATE = 'pow_on_state'
CONF_POW_OFF_STATE = 'pow_on_state'

# attributes
LAMP: Final = 'Lamp'
LAMP_HOURS: Final = 'Lamp Hours'
INPUT_SOURCE: Final = 'Input Source'
MODEL: Final = 'Model'
LAMP_MODE: Final = 'Lamp Mode',
VOLUME: Final = 'Volume',
MUTED: Final = 'Muted'

CUSTOM_ATTRIBUTES: Final = [LAMP_HOURS, INPUT_SOURCE, MODEL, LAMP_MODE, VOLUME, MUTED]
