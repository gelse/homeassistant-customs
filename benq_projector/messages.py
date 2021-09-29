import sys
import re

from serial import Serial, SerialException
from logging import Logger
from typing import Optional, List, AnyStr

from .const import (
    LAMP_MODE,
    INPUT_SOURCE,
    LAMP,
    LAMP_HOURS,
    MODEL,
    VOLUME,
    MUTED
)


class BaseSerialCommand:
    _command: str
    _answer: Optional[str]
    _expected: List[re.Pattern[AnyStr]]
    _logger: Optional[Logger]
    _power_needed: bool

    class PrintLogger:
        def __print__(self, message: str, *args):
            if not args:
                print(message)
            print(message, args)

        def error(self, message: str, *args):
            self.__print__("ERROR: " + message, args)

        def debug(self, message: str, *args):
            self.__print__("DEBUG: " + message, args)

        def info(self, message: str, *args):
            self.__print__("INFO: " + message, args)

        def warn(self, message: str, *args):
            self.__print__("WARN: " + message, args)

    def __init__(self):
        self._command = ""
        self._logger = None
        self._answer = None
        self._expected = []
        self._power_needed = True

    @property
    def logger(self):
        return self._logger or BaseSerialCommand.PrintLogger()

    @logger.setter
    def logger(self, value: Logger):
        self._logger = value

    @property
    def answer(self):
        return self._answer

    @property
    def power_needed(self):
        return self._power_needed

    def add_expected_regex(self, regex: str):
        self._expected.append(re.compile(r'\*' + regex + r'#\r\n'))

    def __repr__(self):
        return "\r*" + self._command + "#\r"

    def execute(self, ser: Serial):
        try:
            if not ser.is_open:
                self.logger.debug("connecting to serial.")
                ser.open()
            self.logger.debug("sending <%s>.", repr(self).replace('\r', r'\r'))
            ser.write(repr(self).encode("ascii"))
            self.logger.debug("reading first answer.")
            answer_to_skip = ser.read_until()
            self.logger.debug("first answer line: <%s>.", repr(answer_to_skip))
            self.logger.debug("reading second answer.")
            raw_answer = ser.read_until().decode("ascii")
            self.logger.debug("second answer line: <%s>.", repr(raw_answer))
            ser.close()
            self.logger.debug("parsing %s expections.", len(self._expected))
            for expected in self._expected:
                match = expected.match(raw_answer)
                if match:
                    self.logger.debug("match found!")
                    self._answer = match.group(1)
                    self.logger.debug("match saved: %s", self._answer)
                    break
            if not self._answer:
                self._answer = raw_answer
                return not any(self._expected)

        except SerialException as serialException:
            self.logger.error("exception happened when communicating:\n%s", serialException)
            return False
        except:
            self.logger.error("unexpected error: %s", sys.exc_info()[0])
            return False
        else:
            return True
        finally:
            if ser.is_open:
                ser.close()


class OnCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=on"
        self.add_expected_regex("POW=(ON)")
        self._power_needed = False


class OffCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=off"
        self.add_expected_regex("POW=(OFF)")


class GetLampStateCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=?"
        self.add_expected_regex("POW=(ON|OFF)")
        self._power_needed = False


class GetLampHoursCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "ltim=?"
        self.add_expected_regex(r'LTIM=(\d+)')
        self._power_needed = False


class GetInputSourceCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "sour=?"
        self.add_expected_regex(r'SOUR=(\w+)')


class GetLampModeCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "lampm=?"
        self.add_expected_regex(r'LAMPM=(\w+)')


class GetModelNameCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "modelname=?"
        self.add_expected_regex(r'MODELNAME=(\w+)')
        self._power_needed = False


class GetMuteStateCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "mute=?"
        self._power_needed = False
        self.add_expected_regex(r'MUTE=(ON|OFF)')


class MuteOnCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "mute=on"
        self._power_needed = False
        self.add_expected_regex(r'MUTE=(ON)')


class MuteOffCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "mute=off"
        self._power_needed = False
        self.add_expected_regex(r'MUTE=(OFF)')


class GetVolumeCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "vol=?"
        self._power_needed = False
        self.add_expected_regex(r'VOL=(\d+)')


class IncreaseVolumeCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "vol=+"
        self._power_needed = False
        self.add_expected_regex(r'VOL=(\+)')


class DecreaseVolumeCommand(BaseSerialCommand):
    def __init__(self):
        super().__init__()
        self._command = "vol=-"
        self._power_needed = False
        self.add_expected_regex(r'VOL=(\-)')


class CustomCommand(BaseSerialCommand):
    def __init__(self, command: str):
        super().__init__()
        self._command = command
        self._power_needed = False


COMMANDS = {
    LAMP_HOURS: GetLampHoursCommand,
    LAMP: GetLampStateCommand,
    MODEL: GetModelNameCommand,
    INPUT_SOURCE: GetInputSourceCommand,
    LAMP_MODE: GetLampModeCommand,
    VOLUME: GetVolumeCommand,
    MUTED: GetMuteStateCommand
}
