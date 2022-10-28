"""Redy Sensor."""
from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import STATE_OK

from .const import LOGGER
from .redy_device import RedyDevice

@dataclass
class RedySensorEntityDescriptionMixin:
    """Mixin for required keys."""


@dataclass
class RedySensorEntityDescription(
    SensorEntityDescription, RedySensorEntityDescriptionMixin
):
    """Represents an Redy Sensor."""

class RedySensor(RedyDevice, SensorEntity):
    """Redy Sensor Entity."""

    def __init__(self, entity_description: SensorEntityDescription) -> None:
        super().__init__()
        self.entity_description = entity_description
        self._attr_unique_id = f"redy/{self.entity_description.key}"
        self._attr_state = STATE_OK

    async def async_added_to_hass(self) -> None:
        """When a Redy entity is added to hass."""
        LOGGER.info("Starting the entity %s", self.entity_description.name)
        await self._start()
        LOGGER.info("Started the entity %s", self.entity_description.name)

    async def async_will_remove_from_hass(self) -> None:
        """When a Redy entity is to be removed from hass."""
        LOGGER.info("Stopping the entity %s", self.entity_description.name)
        await self._stop()
        LOGGER.info("Stopped the entity %s", self.entity_description.name)

    async def _update(self, value):
        """When called, it forces the sync of the value with homeassistant."""
        self._attr_native_value = value
        await self.async_update_ha_state()

    @abstractmethod
    async def _start(self):
        """To be implemented by each child Redy sensor."""

    @abstractmethod
    async def _stop(self):
        """To be implemented by each child Redy sensor"""