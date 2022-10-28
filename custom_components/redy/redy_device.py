"""Redy Device."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN

class RedyDevice(Entity):
    """Redy Device."""

    def __init__(self) -> None:
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "redy")},
            name="Redy"
        )
