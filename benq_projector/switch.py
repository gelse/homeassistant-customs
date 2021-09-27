from __future__ import annotations

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .device_as_switch import BenQSwitch
from .validator import socket

from .const import (
    CONF_WRITE_TIMEOUT,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    DEFAULT_BAUDRATE,
    CONF_BAUDRATE,
    CONF_TIMEOUT,
    CONF_SOCKET
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOCKET): socket,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.socket_timeout,
        vol.Optional(CONF_WRITE_TIMEOUT, default=DEFAULT_WRITE_TIMEOUT): cv.socket_timeout,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType,
) -> None:
    """Connect with serial port and return Acer Projector."""
    socket_url = config[CONF_SOCKET]
    name = config[CONF_NAME]
    timeout = config[CONF_TIMEOUT]
    write_timeout = config[CONF_WRITE_TIMEOUT]
    baudrate = config[CONF_BAUDRATE]

    add_entities([BenQSwitch(socket_url, name, timeout, write_timeout, baudrate)], True)


