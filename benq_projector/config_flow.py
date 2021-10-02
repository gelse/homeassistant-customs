from homeassistant import config_entries, data_entry_flow
from typing import Any, Optional
from .const import DOMAIN
import voluptuous as vol
from .validator import socket


class BenqProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for a Benq projector connected via Serial"""
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:

        if user_input is not None:
            return self.async_create_entry(
                title="Benq projector configuration",
                data=user_input
            )

            # multi-step: return await self.async_step_second() with async_step_second signature like this one
            # finishing config:
            # return self.async_create_entry(
            #   title="Title of the entry",
            #   data={
            #     "something_special": user_input["username"]
            #   })
            # abort config:
            # return self.async_abort(reason="not_supported")

        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("socket"): socket,
            vol.Optional("name", default="Benq Projector"): str,
            vol.Optional("baudrate", default=9600): vol.In([2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]),
            vol.Optional("timeout", default=1): vol.All(int, vol.Range(1, 10))
        }))

#
#    async def async_step_commands1(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:
#        if user_input is not None:
#            pass
#        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
#
#    async def async_step_commands2(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:
#        if user_input is not None:
#            return self.async_create_entry()
