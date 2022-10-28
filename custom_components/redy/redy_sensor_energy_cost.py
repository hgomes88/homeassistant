"""Redy Sensor Energy."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections.abc import Callable, Awaitable

from homeassistant.helpers.event import async_track_time_interval

from .redy_sensor import RedySensor, RedySensorEntityDescription
from .const import LOGGER

from edp.redy.app import EnergyType, EnergyValues
from edp.redy.services.api import ResponseError

@dataclass
class RedyEnergyCostSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    energy_method: Callable[[EnergyType], Awaitable[EnergyValues]]
    energy_type: EnergyType


@dataclass
class RedyEnergyCostSensorEntityDescription(
    RedySensorEntityDescription, RedyEnergyCostSensorEntityDescriptionMixin
):
    """Represents an Redy Sensor."""

    refresh_interval_s = 30*5


class RedyEnergyCostSensor(RedySensor):
    """Redy Energy Sensor"""

    def __init__(self, entity_description: RedyEnergyCostSensorEntityDescription) -> None:
        super().__init__(entity_description=entity_description)

        self._energy_method = entity_description.energy_method
        self._energy_type = entity_description.energy_type
        self._refresh_interval_s = entity_description.refresh_interval_s

    async def _start(self):
        """To be implemented by each child sensor"""
        await self._refresh()
        async_track_time_interval(
            self.hass, self._refresh_task, timedelta(seconds=self._refresh_interval_s)
        )

    async def _stop(self):
        """Stop"""

    async def _refresh(self):
        try:
            energy = await self._energy_method(self._energy_type)
            await self._update(energy.total.cost)
        except ResponseError:
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            diff_sec = (now-midnight).seconds
            if diff_sec > 60*60:
                LOGGER.error("Error")
        except Exception: # pylint: disable=broad-except
            LOGGER.exception("Error")

    async def _refresh_task(self, now):
        await self._refresh()
