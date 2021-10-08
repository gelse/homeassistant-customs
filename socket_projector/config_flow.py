from homeassistant import config_entries, data_entry_flow, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Any, Optional
from urllib.parse import urlparse
import voluptuous as vol
import logging
import serial
import re

from .const import *

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    url = data[CONF_SOCKET]
    if not urlparse(url).scheme in ['http', 'socket']:
        raise InvalidHost

    ser = None
    modelname = None
    normalized_ip = None
    try:
        ser = serial.serial_for_url(data[CONF_SOCKET],
                                    baudrate=data[CONF_BAUDRATE],
                                    timeout=data[CONF_TIMEOUT],
                                    write_timeout=data[CONF_TIMEOUT])
        ser.write('\r*modelname=?#\r'.encode('ascii'))
        ser.read_until()
        ret = ser.read_until().decode('ascii')
        modelname = re.match(r'\*MODELNAME=(.+)#', ret).group(1)
        normalized_ip = re.match(r'(\d+\.\d+\.\d+\.\d+)', data[CONF_SOCKET].split('://')[-1]).group(1).replace('.', '')
    finally:
        if ser is not None and ser.is_open:
            ser.close()

    return {
        CONF_ID: modelname + normalized_ip,
        'title': 'Projector ' + modelname,
    }


class BenqProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    init_info: Optional[dict[str, Any]]

    def __init__(self):
        self.init_info = {}

    """Config flow for a Benq projector connected via Serial"""

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info[CONF_ID])
                self._abort_if_unique_id_configured()
                user_input[CONF_ID] = info[CONF_ID]
                if user_input[CONF_FLOW_COMMAND_SWITCH]:
                    user_input['title'] = info['title']
                    self.init_info = user_input
                    return await self.async_step_user_state()
                final_userinput_dict = {**user_input, **CONF_STATE_DEFAULTS}
                _LOGGER.debug('Finished configuration with the following values: \n%s', final_userinput_dict)
                return self.async_create_entry(title=info['title'], data=final_userinput_dict)
            except InvalidHost:
                errors['host'] = 'cannot_connect'
            except Exception:
                _LOGGER.exception('Unexpected exception.')
                errors['base'] = 'unknown'

        return self.async_show_form(step_id='user',
                                    data_schema=vol.Schema({
                                        vol.Required(CONF_SOCKET, default='socket://127.0.0.1:7000'): str,
                                        vol.Optional(CONF_NAME, default='My projector'): str,
                                        vol.Optional(CONF_BAUDRATE, default=9600): vol.In([2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]),
                                        vol.Optional(CONF_TIMEOUT, default=1): vol.All(int, vol.Range(1, 10)),
                                        vol.Optional(CONF_FLOW_COMMAND_SWITCH, default=False): bool
                                    }),
                                    errors=errors)

    async def async_step_user_state(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:
        errors = {}
        if user_input is not None:
            user_input[CONF_COMMAND_TEMPLATE] = user_input[CONF_COMMAND_TEMPLATE].encode('ascii').decode('unicode_escape')
            final_userinput_dict = {**self.init_info, **user_input}
            _LOGGER.debug('Finished configuration with the following values: \n%s', final_userinput_dict)
            return self.async_create_entry(title=self.init_info['title'], data=final_userinput_dict)

        return self.async_show_form(step_id='user_state',
                                    data_schema=vol.Schema({
                                        # TODO build custom function that escapes and un-escapes \r\n\t. do not use repr/strip
                                        vol.Required(CONF_COMMAND_TEMPLATE, default=repr(CONF_STATE_DEFAULTS[CONF_COMMAND_TEMPLATE]).strip("'")): str,
                                        vol.Required(CONF_POW_ON_CMD, default=CONF_STATE_DEFAULTS[CONF_POW_ON_CMD]): str,
                                        vol.Required(CONF_POW_OFF_CMD, default=CONF_STATE_DEFAULTS[CONF_POW_OFF_CMD]): str,
                                        vol.Required(CONF_POW_STATE_QRY, default=CONF_STATE_DEFAULTS[CONF_POW_STATE_QRY]): str,
                                        vol.Required(CONF_POW_STATE_TMPL, default=CONF_STATE_DEFAULTS[CONF_POW_STATE_TMPL]): str,
                                        vol.Required(CONF_POW_ON_STATE, default=CONF_STATE_DEFAULTS[CONF_POW_ON_STATE]): str,
                                        vol.Required(CONF_POW_OFF_STATE, default=CONF_STATE_DEFAULTS[CONF_POW_OFF_STATE]): str,
                                    }),
                                    errors=errors)


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
