import sys
import re

from serial import Serial, SerialException
from logging import Logger
from typing import Optional, List, AnyStr, Union
from abc import ABC


class ProjectorCommandConfiguration(ABC):
    command_template: str
    response_template: str

    def __init__(self,
                 command_template: str,
                 response_template: str):
        self.command_template = command_template
        self.response_template = response_template


class ProjectorStateCommandConfiguration(ProjectorCommandConfiguration):
    pow_on_command: str
    pow_off_command: str
    pow_state_qry: str
    pow_state_on_value: str
    pow_state_off_value: str

    def __init__(self,
                 command_template: str,
                 response_template: str,
                 pow_on_command: str,
                 pow_off_command: str,
                 pow_state_query: str,
                 pow_state_on_value: str,
                 pow_state_off_value: str):
        super().__init__(command_template, response_template)
        self.pow_on_command = pow_on_command
        self.pow_off_command = pow_off_command
        self.pow_state_qry = pow_state_query
        self.pow_state_on_value = pow_state_on_value
        self.pow_state_off_value = pow_state_off_value


class BaseSerialCommand(ABC):
    _command_configuration: ProjectorCommandConfiguration
    _command: str
    _logger: Optional[Logger]
    _answer: Optional[str]
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

    def __init__(self,
                 command: str,
                 command_configuration: ProjectorCommandConfiguration):
        self._command_configuration = command_configuration
        self._command = command
        self._logger = None
        self._answer = None
        self._power_needed = True
        self._answer_template = re.compile(command_configuration.response_template)

    @property
    def logger(self) -> Union[Logger, PrintLogger]:
        return self._logger or BaseSerialCommand.PrintLogger()

    @logger.setter
    def logger(self, value: Logger):
        self._logger = value

    @property
    def answer(self) -> str:
        return self._answer

    @property
    def power_needed(self) -> bool:
        return self._power_needed

    def get_command(self) -> str:
        return self._command_configuration.command_template.format(self._command)

    def execute(self, ser: Serial) -> bool:
        try:
            if not ser.is_open:
                self.logger.debug("connecting to serial.")
                ser.open()
            self.logger.debug('sending <%s>.', repr(self.get_command()))
            ser.write(self.get_command().encode('ascii'))
            self.logger.debug('reading first answer.')
            answer_to_skip = ser.read_until()
            self.logger.debug('first answer line: <%s>.', repr(answer_to_skip))
            self.logger.debug('reading second answer.')
            raw_answer = ser.read_until().decode('ascii')
            self.logger.debug('second answer line: <%s>.', repr(raw_answer))
            ser.close()
            self.logger.debug('parsing answer.')

            match = self._answer_template.match(raw_answer)
            if match:
                self.logger.debug("match found!")
                self._answer = match.group(1)
                self.logger.debug("match saved: %s", self._answer)
                return True
            else:
                self._answer = raw_answer
                return False
        except SerialException as serialException:
            self.logger.error("exception happened when communicating:\n%s", serialException)
            return False
        except:
            self.logger.error("unexpected error: %s", sys.exc_info())
            return False
        finally:
            if ser.is_open:
                ser.close()


class OnCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorStateCommandConfiguration):
        super().__init__(conf.pow_on_command, conf)
        self._power_needed = False


class OffCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorStateCommandConfiguration):
        super().__init__(conf.pow_off_command, conf)


class GetLampStateCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorStateCommandConfiguration):
        super().__init__(conf.pow_state_qry, conf)
        self._power_needed = False

#
# class GetLampHoursCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "ltim=?"
#         self.__add_expected_regex(r'LTIM=(\d+)')
#         self._power_needed = False
#
#
# class GetInputSourceCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "sour=?"
#         self.__add_expected_regex(r'SOUR=(\w+)')
#
#
# class GetLampModeCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "lampm=?"
#         self.__add_expected_regex(r'LAMPM=(\w+)')
#
#
# class GetModelNameCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "modelname=?"
#         self.__add_expected_regex(r'MODELNAME=(\w+)')
#         self._power_needed = False
#
#
# class GetMuteStateCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "mute=?"
#         self._power_needed = False
#         self.__add_expected_regex(r'MUTE=(ON|OFF)')
#
#
# class MuteOnCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "mute=on"
#         self._power_needed = False
#         self.__add_expected_regex(r'MUTE=(ON)')
#
#
# class MuteOffCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "mute=off"
#         self._power_needed = False
#         self.__add_expected_regex(r'MUTE=(OFF)')
#
#
# class GetVolumeCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "vol=?"
#         self._power_needed = False
#         self.__add_expected_regex(r'VOL=(\d+)')
#
#
# class IncreaseVolumeCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "vol=+"
#         self._power_needed = False
#         self.__add_expected_regex(r'VOL=(\+)')
#
#
# class DecreaseVolumeCommand(BaseSerialCommand):
#     def __init__(self):
#         super().__init__()
#         self._command = "vol=-"
#         self._power_needed = False
#         self.__add_expected_regex(r'VOL=(\-)')
#
#
# class CustomCommand(BaseSerialCommand):
#     def __init__(self, command: str):
#         super().__init__()
#         self._command = command
#         self._power_needed = False
#
#
# COMMANDS = {
#     LAMP_HOURS: GetLampHoursCommand,
#     LAMP: GetLampStateCommand,
#     MODEL: GetModelNameCommand,
#     INPUT_SOURCE: GetInputSourceCommand,
#     LAMP_MODE: GetLampModeCommand,
#     VOLUME: GetVolumeCommand,
#     MUTED: GetMuteStateCommand
# }
