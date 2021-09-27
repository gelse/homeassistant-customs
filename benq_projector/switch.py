from __future__ import annotations

import logging
import re

import serial
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    CONF_NAME,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .validator import socket
from .messages import *

from .const import (
    CONF_WRITE_TIMEOUT,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    LAMP_MODE,
    ICON,
    INPUT_SOURCE,
    LAMP,
    LAMP_HOURS,
    MODEL,
    DEFAULT_BAUDRATE,
    CONF_BAUDRATE,
    CONF_TIMEOUT,
    CONF_SOCKET
)

COMMANDS = {
    LAMP_HOURS: GetLampHoursCommand,
    LAMP: GetLampStateCommand,
    MODEL: GetModelNameCommand,
    INPUT_SOURCE: GetInputSourceCommand,
    LAMP_MODE: GetLampModeCommand,
}

_LOGGER = logging.getLogger(__name__)

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


class BenQSwitch(SwitchEntity):
    """Represents an BenQ Projector as a switch."""

    def __init__(
            self,
            socket_url: str,
            name: str,
            timeout: int,
            write_timeout: int,
            baudrate: int
    ) -> None:
        """Init of the BenQ projector."""
        self._serial_port = socket_url

        self.ser = serial.serial_for_url(
            url=socket_url,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=write_timeout)

        self._attr_name = name
        self._attributes = {
            LAMP_HOURS: STATE_UNKNOWN,
            INPUT_SOURCE: STATE_UNKNOWN,
            LAMP_MODE: STATE_UNKNOWN,
        }
        self._attr_icon = ICON

    def update(self):
        """Get the latest state from the projector."""
        try:
            command = GetLampStateCommand()
            command.logger = _LOGGER
            if not command.execute(self.ser):
                _LOGGER.error("Could not get state of device.")
                self._attr_available = False
                return
            self._attr_available = True
            self._attr_is_on = command.answer == "ON"

            for key in self._attributes:
                command = COMMANDS[key]()
                if command.power_needed and not self.is_on:
                    continue

                command.logger = _LOGGER
                if not command.execute(self.ser):
                    _LOGGER.error("Could not get value for '%s'.", key)
                    continue
                self._attributes[key] = command.answer

            self._attr_extra_state_attributes = self._attributes
        except Exception as exc:
            _LOGGER.error("Unexpected exception: %s", repr(exc))
            self._attr_state = STATE_UNKNOWN
            self._attr_available = False

    def turn_on(self, **kwargs):
        """Turn the projector on."""
        cmd = OnCommand()
        cmd.logger = _LOGGER
        if not cmd.execute(self.ser):
            _LOGGER.error("Error while turning beamer on.")
            return
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        """Turn the projector off."""
        cmd = OffCommand()
        cmd.logger = _LOGGER
        if not cmd.execute(self.ser):
            _LOGGER.error("Error while turning beamer off.")
            return
        self._attr_is_on = False
