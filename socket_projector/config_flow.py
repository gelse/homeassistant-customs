from homeassistant import config_entries, data_entry_flow, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Any, Optional
from urllib.parse import urlparse
import voluptuous as vol
import logging
import serial
import re

from .const import DOMAIN, CONF_TIMEOUT, CONF_BAUDRATE, CONF_SOCKET, CONF_NAME, CONF_ID


_LOGGER = logging.getLogger(__name__)


DATA_SCHEMA = vol.Schema({
                            vol.Required(CONF_SOCKET): str,
                            vol.Optional(CONF_NAME, default="Benq Projector"): str,
                            vol.Optional(CONF_BAUDRATE, default=9600): vol.In([2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]),
                            vol.Optional(CONF_TIMEOUT, default=1): vol.All(int, vol.Range(1, 10))
                        })


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:

    url = data[CONF_SOCKET]
    if not urlparse(url).scheme in ["http", "socket"]:
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
        "title": "Projector " + modelname,
    }


class BenqProjectorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Benq projector configuration", data=user_input)

        return self.async_show_form(step_id="init",
                                    data_schema=vol.Schema({
                                        vol.Optional(CONF_NAME, default=self.config_entry.options.get(CONF_NAME)): str,
                                        vol.Optional(CONF_BAUDRATE, default=self.config_entry.options.get(CONF_BAUDRATE)): vol.In([2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]),
                                        vol.Optional(CONF_TIMEOUT, default=self.config_entry.options.get(CONF_TIMEOUT)): vol.All(int, vol.Range(1, 10))
                                    }),
                                    errors=errors)


class BenqProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for a Benq projector connected via Serial"""
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info[CONF_ID])
                self._abort_if_unique_id_configured()
                user_input[CONF_ID] = info[CONF_ID]
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidHost:
                errors["host"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user",
                                    data_schema=DATA_SCHEMA,
                                    errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return BenqProjectorOptionsFlow(config_entry)


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
