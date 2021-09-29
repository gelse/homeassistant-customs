from homeassistant import config_entries, data_entry_flow
from typing import Any, Optional
from .const import DOMAIN
import voluptuous as vol
from .validator import socket


class BenqProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for a Benq projector connected via Serial"""
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> data_entry_flow.FlowResult:

        if user_input is not None:
            # second step, the user input is filled here. validate the data, like connect the serial.
            # if something is wrong, return dictionary with errors, key is the field name; "base" is special key for error without field.
            # multi-step: return await self.async_step_second() with async_step_second signature like this one
            # finishing config:
            # return self.async_create_entry(
            #   title="Title of the entry",
            #   data={
            #     "something_special": user_input["username"]
            #   })
            # abort config:
            # return self.async_abort(reason="not_supported")
            pass

        data_schema = {
            vol.Required("socket"): socket,
            vol.Optional("name", default="Benq Projector"): str,
            vol.Optional("baudrate", default=9600): int,
            vol.Optional("timeout", default=1): int
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))
