from __future__ import annotations

from typing import Final

DOMAIN: Final = 'socket_projector'

CONF_WRITE_TIMEOUT: Final = 'write_timeout'
CONF_BAUDRATE: Final = 'baudrate'
CONF_TIMEOUT: Final = 'timeout'
CONF_SOCKET: Final = 'socket'
CONF_NAME: Final = 'name'
CONF_ID: Final = 'id'

CONF_FLOW_COMMAND_SWITCH: Final = 'conf_flow_details'

ICON: Final = 'mdi:projector'

CONF_COMMAND_TEMPLATE: Final = 'command_template'
CONF_POW_ON_CMD: Final = 'pow_on_command'
CONF_POW_OFF_CMD: Final = 'pow_off_command'
CONF_POW_STATE_QRY: Final = 'pow_state_query'
CONF_POW_STATE_TMPL: Final = 'pow_state_template'
CONF_POW_ON_STATE: Final = 'pow_on_state'
CONF_POW_OFF_STATE: Final = 'pow_on_state'

CONF_STATE_DEFAULTS: Final = {
    CONF_COMMAND_TEMPLATE: '\r*{}#\r',
    CONF_POW_ON_CMD: 'pow=on',
    CONF_POW_OFF_CMD: 'pow=off',
    CONF_POW_STATE_QRY: 'pow=?',
    CONF_POW_STATE_TMPL: r'\*POW=(ON|OFF)#',
    CONF_POW_ON_STATE: 'ON',
    CONF_POW_OFF_STATE: 'OFF',
}

# attributes
LAMP: Final = 'Lamp'
LAMP_HOURS: Final = 'Lamp Hours'
INPUT_SOURCE: Final = 'Input Source'
MODEL: Final = 'Model'
LAMP_MODE: Final = 'Lamp Mode',
VOLUME: Final = 'Volume',
MUTED: Final = 'Muted'

CUSTOM_ATTRIBUTES: Final = {
    LAMP_HOURS: {
        'command': 'ltim=?',
        'template': r'\*LTIM=(\d+)#'
    },
    INPUT_SOURCE: {
        'command': 'sour=?',
        'template': r'\*SOUR=(\w+)#'
    },
    MODEL: {
        'command': 'modelname=?',
        'template': r'\*MODELNAME=(\w+)#'
    },
    LAMP_MODE: {
        'command': 'lampm=?',
        'template': r'\*LAMPM=(\w+)#'
    },
    VOLUME: {
        'command': 'vol=?',
        'template': r'\*VOL=(\d+)#'
    },
    MUTED: {
        'command': 'mute=?',
        'template': r'\*MUTE=(ON|OFF)#'
    }
}
