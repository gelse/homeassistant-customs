import logging
from logging import Logger

import serial
from typing import Optional, Union

from serial import Serial

from .messages import GetLampStateCommand, OnCommand, OffCommand
from .messages import ProjectorStateCommandConfiguration


class ProjectorConfiguration:
    def __init__(self,
                 socket_url: str,
                 timeout: int,
                 baudrate: int) -> None:
        self.__socket_url = socket_url
        self.__timeout = timeout
        self.__write_timeout = timeout
        self.__baudrate = baudrate

    @property
    def socketurl(self) -> str:
        return self.__socket_url

    @property
    def timeout(self):
        return self.__timeout

    @property
    def write_timeout(self):
        return self.__write_timeout

    @property
    def baudrate(self):
        return self.__baudrate


config = ProjectorStateCommandConfiguration(
    command_template='\r*{}#\r',
    response_template=r'\*POW=(ON|OFF)#',
    pow_on_command='pow=on',
    pow_off_command='pow=off',
    pow_state_query='pow=?',
    pow_state_on_value='ON',
    pow_state_off_value='OFF'
)


class Projector:
    projector_configuration: ProjectorConfiguration
    __id: str
    __logger: Logger
    ser: Serial

    def __init__(self,
                 projector_id: str,
                 projector_configuration: ProjectorConfiguration) -> None:
        self.projector_configuration = projector_configuration
        self.__id = projector_id
        self.__logger = logging.getLogger(__name__)

        self.ser = serial.serial_for_url(
            url=projector_configuration.socketurl,
            baudrate=projector_configuration.baudrate,
            timeout=projector_configuration.timeout,
            write_timeout=projector_configuration.write_timeout,
            do_not_open=True)

    @property
    def projector_id(self) -> str:
        return self.__id

    async def test_connection(self) -> bool:
        try:
            self.__logger.debug("Opening connection...")
            self.ser.open()
            self.__logger.debug("Closing connection...")
            self.ser.close()
        except:
            self.__logger.exception("Error on testing connection to %s", self.projector_configuration.socketurl)
            return False
        return True

    async def get_state(self) -> Optional[bool]:
        self.__logger.debug("Called get_state.")
        cmd = GetLampStateCommand(config)
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while getting Lamp state.")
        if cmd.answer == config.pow_state_on_value:
            return True
        if cmd.answer == config.pow_state_off_value:
            return False
        return None

    async def turn_on(self) -> bool:
        """Turn the projector on."""
        self.__logger.debug("Called turn_on.")
        cmd = OnCommand(config)
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer on.")
            return False
        return True

    async def turn_off(self) -> bool:
        """Turn the projector off."""
        self.__logger.debug("Called turn_off.")
        cmd = OffCommand(config)
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer off.")
            return False
        return True

    async def close(self) -> None:
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
