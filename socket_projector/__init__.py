from __future__ import annotations

import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import *
from .hub import Projector, ProjectorConfiguration, ProjectorStateCommandConfiguration, ProjectorAttributesCommandConfiguration
from .messages import AttributeCommandConfiguration

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["switch"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.

    projector_configuration = ProjectorConfiguration(
        name=entry.data[CONF_NAME],
        socket_url=entry.data[CONF_SOCKET],
        timeout=entry.data[CONF_TIMEOUT],
        baudrate=entry.data[CONF_BAUDRATE],
        statecommandconfig=ProjectorStateCommandConfiguration(
            command_template=entry.data[CONF_COMMAND_TEMPLATE],
            response_template=entry.data[CONF_POW_STATE_TMPL],
            pow_on_command=entry.data[CONF_POW_ON_CMD],
            pow_off_command=entry.data[CONF_POW_OFF_CMD],
            pow_state_query=entry.data[CONF_POW_STATE_QRY],
            pow_state_on_value=entry.data[CONF_POW_ON_STATE],
            pow_state_off_value=entry.data[CONF_POW_OFF_STATE]
        ),
        attributecommandconfig=ProjectorAttributesCommandConfiguration(
            command_template=entry.data[CONF_COMMAND_TEMPLATE],
            attr_lamphours_config=AttributeCommandConfiguration(
                attribute_command='ltim=?',
                attribute_template=r'\*LTIM=(\d+)#'
            )
        )
    )

    hass.data[DOMAIN][entry.entry_id] = Projector(
        projector_id=entry.data[CONF_ID],
        projector_configuration=projector_configuration
        )

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(
                    entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
