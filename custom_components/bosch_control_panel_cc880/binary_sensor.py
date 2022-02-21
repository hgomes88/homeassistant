import asyncio
import logging
from uuid import uuid4

from .alarm import Alarm, Zone
from .const import DATA_BOSCH, DOMAIN

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    BinarySensorEntity,
)
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up entry."""

    _LOGGER.debug("Async Setup Entry Bosch Alarm Zone")

    _alarm: Alarm = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]
    async_add_entities(BoschAlarmZone(_alarm, zone) for zone in _alarm.zones)


async def async_unload_entry(hass, config_entry):
    """Unload entry."""

    _LOGGER.debug("Async Unload Entry Bosch Alarm Zone")


async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""

    _LOGGER.debug("Async Remove Entry Bosch Alarm Zone")


class BoschAlarmZone(BinarySensorEntity):
    """Bosch Zone"""

    def __init__(self, alarm: Alarm, zone=Zone) -> None:
        """Initalize Bosh Alarm Zone object"""

        self._alarm: Alarm = alarm
        self._zone: Zone = zone
        self._is_on = False
        self._state = STATE_UNKNOWN

        _LOGGER.info(f"Starting the Bosch Control Panel Zone {self._zone.number}")

        asyncio.create_task(self._init())

        _LOGGER.info(f"Started the Bosch Control Panel Zone {self._zone.number}")

    async def _init(self):
        self._alarm.add_zone_listener(self._zone.number, self._zone_listener)

    @property
    def is_on(self):
        return self._zone.triggered

    @property
    def state(self):
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def device_class(self):
        return DEVICE_CLASS_MOTION

    @property
    def unique_id(self):
        """Return a unique ID to use for this device."""
        return f"bosch_zone_{self._zone.number}"

    @property
    def name(self):
        """Return the name of the device."""
        return self._zone.name or f"bosch_zone_{self._zone.number}"

    async def _zone_listener(self, zone: Zone):
        await self.async_update_ha_state()
