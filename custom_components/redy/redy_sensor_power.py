"""Redy Entities."""
from __future__ import annotations
from dataclasses import dataclass

from .redy_sensor import RedySensor, RedySensorEntityDescription

from edp.redy.app import PowerType


@dataclass
class RedyPowerSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    power_type: PowerType


@dataclass
class RedyPowerSensorEntityDescription(
    RedySensorEntityDescription, RedyPowerSensorEntityDescriptionMixin
):
    """Represents an Redy Sensor."""


class RedyPowerSensor(RedySensor):
    """Redy Power Sensor"""

    def __init__(self, entity_description: RedyPowerSensorEntityDescription) -> None:
        super().__init__(entity_description=entity_description)
        self._power_type = entity_description.power_type

    async def _start(self):
        """To be implemented by each child sensor"""
        self._power_type.stream(self._stream)

    async def _stop(self):
        """Stop"""

    async def _stream(self, value):
        await self._update(value)
