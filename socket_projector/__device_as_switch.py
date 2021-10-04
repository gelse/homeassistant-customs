import serial
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_UNKNOWN

from .const import ICON, CUSTOM_ATTRIBUTES
from .messages import COMMANDS, GetLampStateCommand, OnCommand, OffCommand


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
        self.__logger = logging.getLogger(__name__)

        self.ser = serial.serial_for_url(
            url=socket_url,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=write_timeout)

        self._attr_name = name

        for attribute in CUSTOM_ATTRIBUTES:
            self._attr_extra_state_attributes[attribute] = STATE_UNKNOWN

        self._attr_icon = ICON

    def update(self):
        """Get the latest state from the projector."""
        try:
            command = GetLampStateCommand()
            command.logger = self.__logger
            if not command.execute(self.ser):
                self.__logger.error("Could not get state of device.")
                self._attr_available = False
                return
            self._attr_available = True
            self._attr_is_on = command.answer == "ON"

            for attribute in CUSTOM_ATTRIBUTES:
                command = COMMANDS[attribute]()
                if command.power_needed and not self.is_on:
                    continue

                command.logger = self.__logger
                if not command.execute(self.ser):
                    self.__logger.error("Could not get value for '%s'.", attribute)
                    continue
                self._attr_extra_state_attributes[attribute] = command.answer

        except Exception as exc:
            self.__logger.error("Unexpected exception: %s", repr(exc))
            self._attr_state = STATE_UNKNOWN
            self._attr_available = False

    def turn_on(self, **kwargs):
        """Turn the projector on."""
        cmd = OnCommand()
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer on.")
            return
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        """Turn the projector off."""
        cmd = OffCommand()
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer off.")
            return
        self._attr_is_on = False
