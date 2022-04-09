import asyncio
import logging
from uuid import uuid4

from bosch.control_panel.cc880p.cp import ControlPanel
from bosch.control_panel.cc880p.models import Zone
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

    _alarm: ControlPanel = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]
    async_add_entities(BoschAlarmZone(_alarm, zone) for zone in list(_alarm.zones.values()))


async def async_unload_entry(hass, config_entry):
    """Unload entry."""

    _LOGGER.debug("Async Unload Entry Bosch Alarm Zone")


async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""

    _LOGGER.debug("Async Remove Entry Bosch Alarm Zone")


class BoschAlarmZone(BinarySensorEntity):
    """Bosch Zone"""

    def __init__(self, alarm: ControlPanel, zone: Zone) -> None:
        """Initalize Bosh Alarm Zone object"""

        self._alarm: ControlPanel = alarm
        self._zone: Zone = zone
        self._is_on = False
        self._state = STATE_UNKNOWN

    async def _init(self):
        self._alarm.add_zone_listener(self._zone.number, self._zone_listener)

    async def async_added_to_hass(self) -> None:
        _LOGGER.info("Starting the Bosch Control Panel Zone %d", self._zone.number)
        await self._init()
        _LOGGER.info("Started the Bosch Control Panel Zone %d", self._zone.number)

    async def async_will_remove_from_hass(self) -> None:
        _LOGGER.info("Stopping the Bosch Control Panel Zone %d", self._zone.number)
        _LOGGER.info("Stopped the Bosch Control Panel Zone %d", self._zone.number)

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
