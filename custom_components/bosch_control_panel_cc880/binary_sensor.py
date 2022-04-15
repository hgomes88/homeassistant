"""Support for Bosch Control Panel CC880P Zones in Homeassistant."""

import logging

from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models import Zone
from bosch.control_panel.cc880p.models import ControlPanelModel
from bosch.control_panel.cc880p.models import Id
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

    _alarm: CP = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]
    async_add_entities(BoschAlarmZone(_alarm, id, zone) for id, zone in _alarm.control_panel.zones.items())


async def async_unload_entry(hass, config_entry):
    """Unload entry."""
    _LOGGER.debug("Async Unload Entry Bosch Alarm Zone")


async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""
    _LOGGER.debug("Async Remove Entry Bosch Alarm Zone")


class BoschAlarmZone(BinarySensorEntity):
    """Zone of bosch control panel."""

    def __init__(self, alarm: CP, idd: Id, zone: Zone) -> None:
        """Initialize Bosh Alarm Zone object.

        Args:
            alarm (CP): The bosch control panel object
            id (Id): The numer/id of this zone
            zone (Zone): Zone object
        """
        self._alarm: CP = alarm
        self._id: Id = idd
        self._zone: Zone = zone
        self._is_on = False
        self._state = STATE_UNKNOWN

    async def _init(self):
        self._alarm.add_control_panel_listener(self._zone_listener)

    async def async_added_to_hass(self) -> None:
        """Initialize the zone when it is added to hass."""
        _LOGGER.info("Starting the Bosch Control Panel Zone %d", self._id)
        await self._init()
        _LOGGER.info("Started the Bosch Control Panel Zone %d", self._id)

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup the zone when it is about to be removed from hass."""
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
    def state(self) -> str:
        """Return the state of the zone.

        Returns:
            str: Returns 'on' if is triggered. 'off' otherwise
        """
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def device_class(self) -> str:
        """Return the class of the device.

        Returns:
            str: The class of the device
        """
        return DEVICE_CLASS_MOTION

    @property
    def unique_id(self):
        """Return a unique ID to use for this device."""
        return f"bosch_zone_{self._id}"

    @property
    def name(self):
        """Return the name of the device."""
        return f"bosch_zone_{self._id}"

    async def _zone_listener(self, _: Id, zone: ControlPanelModel):
        if isinstance(zone, Zone):
            await self.async_update_ha_state()
