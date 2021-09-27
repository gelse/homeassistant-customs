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
from .messages import GetLampStateCommand

from .const import (
    CMD_DICT,
    CONF_WRITE_TIMEOUT,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    LAMP_MODE,
    ICON,
    INPUT_SOURCE,
    LAMP,
    LAMP_HOURS,
    DEFAULT_BAUDRATE,
    CONF_BAUDRATE,
    CONF_TIMEOUT,
    CONF_SOCKET
)

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

    def _write_read(self, msg):
        """Write to the projector and read the return."""

        ret = ""
        # Sometimes the projector won't answer for no reason or the projector
        # was disconnected during runtime.
        # This way the projector can be reconnected and will still work
        try:
            if not self.ser.is_open:
                _LOGGER.debug("Connecting to %s", self._serial_port)
                self.ser.open()
            _LOGGER.debug("sending <%s>", repr(msg))
            self.ser.write(msg.encode("ascii"))

            # the first answer is the question
            ret = self.ser.read_until()
            _LOGGER.debug("ignored message: %s", repr(ret))
            # the second answer is what we want
            ret = self.ser.read_until().decode("ascii")

        except serial.SerialException:
            _LOGGER.error("Problem communicating with %s", self._serial_port)
        self.ser.close()
        return ret

    def _write_read_format(self, msg):
        """Write msg, obtain answer and format output."""
        # answers are formatted as ***\answer\r***
        answer = self._write_read(msg)
        _LOGGER.debug("analyzing answer: %s", repr(answer))
        if answer == "*Block item#\r\n":
            return STATE_UNKNOWN
        match = re.search(r"=(.+)#", answer)
        if match:
            return match.group(1)
        _LOGGER.error("could not analyze %s", repr(answer))
        return STATE_UNKNOWN

    def update(self):
        """Get the latest state from the projector."""

        try:
            command = GetLampStateCommand()
            command.logger = _LOGGER
            command.execute(self.ser)

        answer = self._write_read_format(CMD_DICT[LAMP])
        _LOGGER.debug("<update> answer is: %s", repr(answer))
        if answer == "ON":
            self._attr_is_on = True
            self._attr_available = True
        elif answer == "OFF":
            self._attr_is_on = False
            self._attr_available = True
        else:
            _LOGGER.warning("unknown status: %s", repr(answer))
            self._attr_available = False

        for key in self._attributes:
            msg = CMD_DICT.get(key)
            if msg:
                answer = self._write_read_format(msg)
                _LOGGER.debug("Answer to <%s>: %s", repr(msg), repr(answer))
                self._attributes[key] = answer
        self._attr_extra_state_attributes = self._attributes

    def turn_on(self, **kwargs):
        """Turn the projector on."""
        msg = CMD_DICT[STATE_ON]
        self._write_read(msg)
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        """Turn the projector off."""
        msg = CMD_DICT[STATE_OFF]
        self._write_read(msg)
        self._attr_is_on = False
