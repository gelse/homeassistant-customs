import re
import sys
from abc import ABC
from logging import Logger
from typing import Optional, AnyStr, Union, Pattern

from serial import Serial, SerialException


class AttributeCommandConfiguration:
    attribute_command: str
    attribute_template: str

    def __init__(self,
                 attribute_command: str,
                 attribute_template: str):
        self.attribute_command = attribute_command
        self.attribute_template = attribute_template


class ProjectorCommandConfiguration(ABC):
    command_template: str

    def __init__(self,
                 command_template: str):
        self.command_template = command_template


class ProjectorStateCommandConfiguration(ProjectorCommandConfiguration):
    pow_on_command: str
    pow_off_command: str
    pow_state_qry: str
    response_template: str
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
        super().__init__(command_template)
        self.pow_on_command = pow_on_command
        self.pow_off_command = pow_off_command
        self.pow_state_qry = pow_state_query
        self.response_template = response_template
        self.pow_state_on_value = pow_state_on_value
        self.pow_state_off_value = pow_state_off_value


class ProjectorAttributesCommandConfiguration(ProjectorCommandConfiguration):
    attr_lamphours_config: AttributeCommandConfiguration

    def __init__(self,
                 command_template: str,
                 attr_lamphours_config: AttributeCommandConfiguration):
        super().__init__(command_template)
        self.attr_lamphours_config = attr_lamphours_config


class BaseSerialCommand(ABC):
    _command_configuration: Union[ProjectorCommandConfiguration, ProjectorAttributesCommandConfiguration]
    _command: str
    _logger: Optional[Logger]
    _answer: Optional[str]
    _power_needed: bool
    _answer_template: Pattern[AnyStr]

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
                 response_template: str,
                 command_configuration: ProjectorCommandConfiguration,
                 logger: Optional[Logger] = None):
        self._command_configuration = command_configuration
        self._command = command
        self._logger = logger
        self._answer = None
        self._power_needed = True
        if self._logger is not None:
            self._logger.debug('Creating command %s with query %s and pattern %s', type(self).__name__, repr(self._command), repr(response_template))
        self._answer_template = re.compile(response_template)

    @property
    def logger(self) -> Union[Logger, PrintLogger]:
        return self._logger or BaseSerialCommand.PrintLogger()

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
                self.logger.debug('match found!')
                self._answer = match.group(1)
                self.logger.debug('match saved: %s', self._answer)
                return True
            else:
                self.logger.debug('Could not find match for %s with pattern %s', raw_answer, self._answer_template)
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
    def __init__(self, conf: ProjectorStateCommandConfiguration, logger: Optional[Logger] = None):
        super().__init__(conf.pow_on_command, conf.response_template, conf, logger)
        self._power_needed = False


class OffCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorStateCommandConfiguration, logger: Optional[Logger] = None):
        super().__init__(conf.pow_off_command, conf.response_template, conf, logger)


class GetLampStateCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorStateCommandConfiguration, logger: Optional[Logger] = None):
        super().__init__(conf.pow_state_qry, conf.response_template, conf, logger)
        self._power_needed = False


class GetLampHoursCommand(BaseSerialCommand):
    def __init__(self, conf: ProjectorAttributesCommandConfiguration, logger: Optional[Logger] = None):
        super().__init__(conf.attr_lamphours_config.attribute_command, conf.attr_lamphours_config.attribute_template, conf, logger)
        self._power_needed = False

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
