import logging
import serial

from .messages import GetLampStateCommand, OnCommand, OffCommand


class Projector:
    def __init__(
            self,
            projector_id: str,
            socket_url: str,
            timeout: int,
            write_timeout: int,
            baudrate: int
    ) -> None:
        self.__id = projector_id
        self.__socket_url = socket_url
        self.__logger = logging.getLogger(__name__)

        self.ser = serial.serial_for_url(
            url=socket_url,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=write_timeout,
            do_not_open=True)

    @property
    def projector_id(self):
        return self.__id

    async def test_connection(self) -> bool:
        try:
            self.__logger.debug("Opening connection...")
            self.ser.open()
            self.__logger.debug("Closing connection...")
            self.ser.close()
        except:
            self.__logger.exception("Error on testing connection to %s", self.__socket_url)
            return False
        return True

    async def get_state(self) -> bool:
        self.__logger.debug("Called get_state.")
        cmd = GetLampStateCommand()
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while getting Lamp state.")
        return cmd.answer == "ON"

    async def turn_on(self) -> bool:
        """Turn the projector on."""
        self.__logger.debug("Called turn_on.")
        cmd = OnCommand()
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer on.")
            return False
        return True

    async def turn_off(self) -> bool:
        """Turn the projector off."""
        self.__logger.debug("Called turn_off.")
        cmd = OffCommand()
        cmd.logger = self.__logger
        if not cmd.execute(self.ser):
            self.__logger.error("Error while turning beamer off.")
            return False
        return True

    async def close(self) -> None:
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
