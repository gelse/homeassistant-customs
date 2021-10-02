from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor

import asyncio
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .hub import Projector
from .const import DOMAIN
from homeassistant.const import STATE_UNKNOWN

_executor = ThreadPoolExecutor(10)


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add cover for passed config_entry in HA."""
    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    projector = hass.data[DOMAIN][config_entry.entry_id]

    # The next few lines find all of the entities that will need to be added
    # to HA. Note these are all added to a list, so async_add_devices can be
    # called just once.
    new_devices = []
    projector_entity = ConfiguredProjector(projector)
    new_devices.append(projector_entity)

    # If we have any new devices, add them
    if new_devices:
        async_add_entities(new_devices)


class ConfiguredProjector(SwitchEntity):
    def __init__(self, projector: Projector) -> None:
        self._projector = projector
        self._attr_is_on = False

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        await self._projector.close()

    async def async_update(self):
        self._attr_available = await self._projector.test_connection()
        if not self._attr_available:
            self._attr_state = STATE_UNKNOWN
        self._attr_is_on = await self._projector.get_state()
        # TODO load further custom attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        if await self._projector.turn_on():
            self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        if await self._projector.turn_off():
            self._attr_is_on = False

    @property
    def unique_id(self) -> str:
        """Return Unique ID string."""
        return self._projector.projector_id
