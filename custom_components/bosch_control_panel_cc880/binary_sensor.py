"""Support for Bosch Control Panel CC880P Zones in Homeassistant."""

import logging

from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models.cp import Availability, Id, Zone
from bosch.control_panel.cc880p.models.listener import BaseControlPanelListener

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from . import BoschControlPanelDevice
from .const import DATA_BOSCH, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up entry."""
    _LOGGER.debug("Async Setup Entry Bosch Alarm Zone")

    _alarm: CP = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]
    async_add_entities(
        BoschAlarmZone(_alarm, id, zone)
        for id, zone in _alarm.control_panel.zones.items()
    )


async def async_unload_entry(hass: HomeAssistant, config_entry):
    """Unload entry."""
    _LOGGER.debug("Async Unload Entry Bosch Alarm Zone")


async def async_remove_entry(hass: HomeAssistant, entry) -> None:
    """Handle removal of an entry."""
    _LOGGER.debug("Async Remove Entry Bosch Alarm Zone")


class BoschAlarmZone(
    BoschControlPanelDevice, BinarySensorEntity, BaseControlPanelListener
):
    """Zone of bosch control panel."""

    def __init__(self, alarm: CP, idd: Id, zone: Zone) -> None:
        """Initialize Bosh Alarm Zone object.

        Args:
            alarm (CP): The bosch control panel object
            idd (Id): The number/id of this zone
            zone (Zone): Zone object
        """
        self._alarm: CP = alarm
        self._id: Id = idd
        self._zone: Zone = zone
        self._is_on = False
        self._state = STATE_UNKNOWN
        self._attr_device_class = BinarySensorDeviceClass.MOTION

    async def async_added_to_hass(self) -> None:
        """Initialize the zone when it is added to hass."""
        _LOGGER.info("Starting the Bosch Control Panel Zone %d", self._id)
        self._alarm.add_listener(self)
        await self.async_update_ha_state(force_refresh=True)
        _LOGGER.info("Started the Bosch Control Panel Zone %d", self._id)

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup the zone when it is about to be removed from hass."""
        self._alarm.remove_listener(self)
        _LOGGER.info("Stopping the Bosch Control Panel Zone %d", self._id)
        _LOGGER.info("Stopped the Bosch Control Panel Zone %d", self._id)

    @property
    def is_on(self) -> bool:
        """Whether the one is triggered.

        Returns:
            bool: True of is triggered. False otherwise
        """
        return self._zone.triggered

    @property
    def unique_id(self):
        """Return a unique ID to use for this device."""
        return f"bosch_zone_{self._id}"

    @property
    def name(self):
        """Return the name of the device."""
        return f"bosch_zone_{self._id}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._alarm.control_panel.availability.available

    async def on_zone_trigger_changed(
        self, id: Id, entity: Zone
    ):  # pylint: disable=redefined-builtin
        if id == self._id:
            _LOGGER.debug("Zone[%d] trigger changed: %s", id, entity)
            await self.async_update_ha_state(force_refresh=True)

    async def on_availability_changed(self, entity: Availability):  # noqa: D102
        _LOGGER.debug("Availability changed: %s", entity)
        await self.async_update_ha_state(force_refresh=True)
