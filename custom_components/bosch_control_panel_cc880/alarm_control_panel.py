"""Support for Bosch Control Panel CC880P in Homeassistant."""

from distutils.util import strtobool
import logging
from typing import Optional
import voluptuous as vol

from . import BoschControlPanelDevice

from .const import DATA_BOSCH, DOMAIN, SERVICE_OUTPUT, SERVICE_SIREN
from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models import ArmingMode
from bosch.control_panel.cc880p.models import Id
from bosch.control_panel.cc880p.models import ControlPanelModel
from bosch.control_panel.cc880p.models import Siren
from bosch.control_panel.cc880p.models import Area

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.components.alarm_control_panel import (
    FORMAT_NUMBER,
    AlarmControlPanelEntity,
)
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_NIGHT,
    SUPPORT_ALARM_TRIGGER,
)
from homeassistant.const import (
    CONF_COMMAND,
    CONF_ID,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_DISARMING,
    STATE_ALARM_TRIGGERED,
    STATE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:security"

SERVICE_SIREN_SCHEMA = vol.Schema({vol.Required(CONF_COMMAND): cv.string})

SERVICE_OUTPUT_SCHEMA = vol.Schema({
    vol.Required(CONF_ID): cv.positive_int,
    vol.Required(CONF_COMMAND): cv.string
})


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up entry."""
    _LOGGER.debug("Async Setup Entry Alarm Control Panel")

    _alarm: CP = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]

    async_add_entities([BoschAlarmControlPanel(_alarm)])


async def async_unload_entry(hass, config_entry):
    """Unload entry."""
    _LOGGER.debug("Async Unload Entry Alarm Control Panel")


async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""
    _LOGGER.debug("Async Remove Entry Alarm Control Panel")


class BoschAlarmControlPanel(BoschControlPanelDevice, AlarmControlPanelEntity):
    """Bosch Control Panel."""

    def __init__(self, alarm: CP) -> None:
        """Initialize the control panel.

        Args:
            alarm (CP): Object representation of the control panel
        """
        self._state = STATE_UNKNOWN
        self._transition_state: Optional[str] = None
        self._alarm: CP = alarm
        self._manual_trigger: bool = False
        self._unavailable_count: int = 0

    @property
    def code_format(self):
        """Regex for code format or None if no code is required."""
        return FORMAT_NUMBER

    @property
    def unique_id(self):
        """Return a unique ID to use for this device."""
        return "bosch_control_panel"

    @property
    def name(self):
        """Return the name of the device."""
        return "bosch_control_panel"

    @property
    def changed_by(self) -> str:
        """Indicate who/what made the last change.

        Returns:
            str: Who/what made the change
        """
        return "The best person"

    @property
    def code_arm_required(self):
        """Whether the code is required for arm actions."""
        return True

    @property
    def icon(self):
        """Return the icon."""
        return ICON

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._is_available()

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return False

    @property
    def state(self):
        """Return the state of the device."""
        # If is arming, or disarming, always present that status
        if self._transition_state:
            self._state = self._transition_state
        # Else if siren is triggere Show that the siren was triggered
        elif self._alarm.control_panel.siren.on:
            self._state = STATE_ALARM_TRIGGERED
        # Else show any other alarm state
        else:
            mode = self._alarm.control_panel.areas[1].mode
            if mode == ArmingMode.DISARMED and self._state != STATE_ALARM_DISARMED:
                self._state = STATE_ALARM_DISARMED
            elif (
                mode == ArmingMode.ARMED_AWAY
                and self._state != STATE_ALARM_ARMED_AWAY
            ):
                self._state = STATE_ALARM_ARMED_AWAY
            elif (
                mode == ArmingMode.ARMED_STAY
                and self._state != STATE_ALARM_ARMED_NIGHT
            ):
                self._state = STATE_ALARM_ARMED_NIGHT

        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes."""
        c_p = self._alarm.control_panel
        state_attr = {
            'time': f'{c_p.time_utc.hour:02d}:{c_p.time_utc.minute:02d}:00',
            'siren': int(c_p.siren.on),
            'outputs': " ".join([str(int(out.on)) for _, out in c_p.outputs.items()]),
            'zones_triggered': " ".join([str(int(zone.triggered)) for _, zone in c_p.zones.items()]),
            'zones_enabled': " ".join([str(int(zone.enabled)) for _, zone in c_p.zones.items()])
        }

        state_attr.update(super().state_attributes)
        return state_attr

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_TRIGGER | SUPPORT_ALARM_ARM_NIGHT | SUPPORT_ALARM_ARM_AWAY

    async def async_added_to_hass(self) -> None:
        """Initialize the control pannel when it is added to hass."""
        _LOGGER.info("Starting the Bosch Control Panel")
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_SIREN,
            self._siren_service,
            schema=SERVICE_SIREN_SCHEMA
        )
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_OUTPUT,
            self._out_service,
            schema=SERVICE_OUTPUT_SCHEMA
        )
        self._alarm.add_control_panel_listener(self._listener)

        _LOGGER.info("Started the Bosch Control Panel")

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup the control panel when it is about to be removed from hass."""
        _LOGGER.info("Stopping the Bosch Control Panel")
        self.hass.services.async_remove(DOMAIN, SERVICE_SIREN)
        self.hass.services.async_remove(DOMAIN, SERVICE_OUTPUT)
        _LOGGER.info("Stopped the Bosch Control Panel")

    async def async_alarm_disarm(self, code=None):
        """Disarm the alarm.

        Args:
            code (str, optional): The code to disarm. Defaults to None.
        """
        _LOGGER.info("Disarming")
        if self._manual_trigger:
            # Disable Siren and get the status forcing update
            await self._alarm.set_siren(False, update=True)
            # Clear the manual trigger
            self._manual_trigger = False
            # Ask hass to update the state of the alarm
            await self.async_update_ha_state()
        # If alarm is armed anyway, proceed with the disarm, otherwise dont' do anythign
        if self.state not in [STATE_ALARM_DISARMING, STATE_ALARM_DISARMED]:
            await self._change_state(
                code=f"{code}#", transition_state=STATE_ALARM_DISARMING
            )

    async def async_alarm_arm_night(self, code=None):
        """Arm the alarm in night mode.

        Args:
            code (str, optional): The code to arm. Defaults to None.
        """
        _LOGGER.info("Arming Night")
        if self.state == STATE_ALARM_DISARMED:
            await self._change_state(
                code=f"{code}*", transition_state=STATE_ALARM_ARMING
            )

    async def async_alarm_arm_away(self, code=None):
        """Arm the alarm in away mode.

        Args:
            code (str, optional): The code to arm. Defaults to None.
        """
        _LOGGER.info("Arming Away")
        if self.state == STATE_ALARM_DISARMED:
            await self._change_state(
                code=f"{code}#", transition_state=STATE_ALARM_ARMING
            )

    async def async_alarm_trigger(self, code=None):
        """Trigger the alarm.

        Args:
            code (str, optional): The code to trigger the alarm. Defaults to None.
        """
        _LOGGER.info("Triggering the Alarm")
        await self._alarm.set_siren(True)
        self._manual_trigger = True

    async def async_alarm_arm_custom_bypass(self, code=None) -> None:
        """Arm the alarm using a custom bypass.

        Args:
            code (str, optional): The code to arm the alarm. Defaults to None.
        """
        _LOGGER.info("Arming with custom")

    async def _change_state(self, code, transition_state):
        try:
            # Change the status to the transition state
            self._transition_state = transition_state
            # Force update of the transtition state
            await self.async_update_ha_state()
            # Send the code to change the state
            await self._alarm.send_keys(keys=code, update=True)
            self._transition_state = None
            # Force the update
            await self.async_update_ha_state()
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error("Couldn't change the alarm to %s: %s", transition_state, ex)
            self._transition_state = None
            # Force update of the transtition state
            await self.async_update_ha_state()

    def _is_available(self):
        # Considered available while it doesn't fail 3 times in a row
        return self._unavailable_count < 3

    def _set_available(self, available: bool = True):
        if available:
            self._unavailable_count = 0
        else:
            self._unavailable_count += 1

    async def _listener(self, _: Id, c_p: ControlPanelModel):
        if isinstance(c_p, (Siren, Area)):
            await self.async_update_ha_state()

        # Always update te availability
        self._set_available(self._alarm.control_panel.availability.available)

        return True

    async def _siren_service(self, call: ServiceCall):
        status = bool(strtobool(call.data[CONF_COMMAND]))
        await self._alarm.set_siren(status, update=True)
        self._manual_trigger = status

    async def _out_service(self, call: ServiceCall):
        idd: Id = call.data[CONF_ID]
        status = bool(strtobool(call.data[CONF_COMMAND]))
        await self._alarm.set_output(idd, status, update=True)
