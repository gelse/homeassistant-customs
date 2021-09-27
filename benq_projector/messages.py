import sys
import re

from serial import Serial, SerialException
from logging import Logger
from typing import Optional, List, AnyStr


class BaseCommand:
    _command: str
    _answer: Optional[str]
    _expected: Optional[List[re.Pattern[AnyStr]]]
    _logger: Optional[Logger]

    def __init__(self):
        self._command = ""
        self._logger = None
        self._answer = None
        self._expected = None

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value: Logger):
        self._logger = value

    @property
    def command(self):
        return self._command

    @property
    def answer(self):
        return self._answer

    def add_expected_regex(self, regex: str):
        self._expected.append(re.compile('\\*' + regex + '#\\r\\n'))

    def __repr__(self):
        return "\r*" + self._command + "#\r"

    def execute(self, ser: Serial):
        try:
            if not ser.is_open:
                ser.open()
            self._logger.debug("sending <%s>", repr(self))
            ser.write(repr(self).encode("ascii"))
            ser.read_until()
            raw_answer = ser.read_until().decode("ascii")
            for expected in self._expected:
                match = expected.match(raw_answer)
                if match:
                    self._answer = match.group(1)
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


class OnCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=on"


class OffCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=off"
        self.add_expected_regex("POW=(ON|OFF)")


class GetLampStateCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "pow=?"


class GetLampHoursCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "ltim=?"


class GetInputSourceCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "sour=?"


class GetLampModeCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "lampm=?"


class GetModelNameCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "modelname=?"


class GetMuteStateCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "mute=?"


class GetVolumeStateCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._command = "vol=?"

