"""Support for Bosch Control Panel CC880P in Homeassistant."""

from datetime import datetime, timedelta
import logging

from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models.cp import (
    Area,
    ArmingMode,
    Availability,
    ControlPanelEntity,
    Id,
    Output,
    Siren,
    Time,
    Zone,
)
from bosch.control_panel.cc880p.models.listener import BaseControlPanelListener
import voluptuous as vol

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)
from homeassistant.config_entries import ConfigEntry
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
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from . import BoschControlPanelDevice
from .const import DATA_BOSCH, DOMAIN, SERVICE_OUTPUT, SERVICE_SIREN

_LOGGER = logging.getLogger(__name__)

# Icon to be used by default for the control panel
ICON = "mdi:security"

# Schema for executing the siren on/off service
SERVICE_SIREN_SCHEMA = vol.Schema({vol.Required(CONF_COMMAND): cv.string})

# Schema to set an output on/off
SERVICE_OUTPUT_SCHEMA = vol.Schema(
    {vol.Required(CONF_ID): cv.positive_int, vol.Required(CONF_COMMAND): cv.string}
)

TWO_MINUTES = 60 * 2


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up entry."""
    _LOGGER.debug("Async Setup Entry Alarm Control Panel")

    # Get the instance of the control panel
    _alarm: CP = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]

    async_add_entities([BoschAlarmControlPanel(_alarm)])


async def async_unload_entry(hass: HomeAssistant, config_entry):
    """Unload entry."""
    _LOGGER.debug("Async Unload Entry Alarm Control Panel")


async def async_remove_entry(hass: HomeAssistant, entry) -> None:
    """Handle removal of an entry."""
    _LOGGER.debug("Async Remove Entry Alarm Control Panel")


def _strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    if val in ("n", "no", "f", "false", "off", "0"):
        return 0
    raise ValueError(f"invalid truth value {val!r}")


class BoschAlarmControlPanel(
    BoschControlPanelDevice, AlarmControlPanelEntity, BaseControlPanelListener
):
    """Bosch Control Panel."""

    def __init__(self, alarm: CP) -> None:
        """Initialize the control panel.

        Args:
            alarm (CP): Object representation of the control panel
        """
        self._state = STATE_UNKNOWN
        self._transition_state: str | None = None
        self._alarm: CP = alarm
        self._manual_trigger: bool = False

    @property
    def code_format(self):
        """Regex for code format or None if no code is required."""
        return CodeFormat.NUMBER

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
        return self._alarm.control_panel.availability.available

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
        # Else if siren is triggered, show that the siren was triggered
        elif self._alarm.control_panel.siren.on:
            self._state = STATE_ALARM_TRIGGERED
        # Else show any other alarm state
        else:
            mode = self._alarm.control_panel.areas[1].mode
            if mode == ArmingMode.DISARMED and self._state != STATE_ALARM_DISARMED:
                self._state = STATE_ALARM_DISARMED
            elif (
                mode == ArmingMode.ARMED_AWAY and self._state != STATE_ALARM_ARMED_AWAY
            ):
                self._state = STATE_ALARM_ARMED_AWAY
            elif (
                mode == ArmingMode.ARMED_STAY and self._state != STATE_ALARM_ARMED_NIGHT
            ):
                self._state = STATE_ALARM_ARMED_NIGHT

        return self._state

    @property
    def _attr_extra_state_attributes(self):
        """Return the state attributes."""
        c_p = self._alarm.control_panel
        state_attr = {
            "time": f"{c_p.time_utc.hour:02d}:{c_p.time_utc.minute:02d}:00",
            "siren": int(c_p.siren.on),
            "outputs": " ".join([str(int(out.on)) for _, out in c_p.outputs.items()]),
            "zones_triggered": " ".join(
                [str(int(zone.triggered)) for _, zone in c_p.zones.items()]
            ),
            "zones_enabled": " ".join(
                [str(int(zone.enabled)) for _, zone in c_p.zones.items()]
            ),
        }

        return state_attr

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return (
            AlarmControlPanelEntityFeature.TRIGGER
            # | AlarmControlPanelEntityFeature.ARM_NIGHT
            | AlarmControlPanelEntityFeature.ARM_AWAY
        )

    async def async_added_to_hass(self) -> None:
        """Initialize the control panel when it is added to hass."""
        _LOGGER.info("Starting the Bosch Control Panel")
        self.hass.services.async_register(
            DOMAIN, SERVICE_SIREN, self._siren_service, schema=SERVICE_SIREN_SCHEMA
        )
        self.hass.services.async_register(
            DOMAIN, SERVICE_OUTPUT, self._out_service, schema=SERVICE_OUTPUT_SCHEMA
        )
        self._alarm.add_listener(self)

        _LOGGER.info("Started the Bosch Control Panel")

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup the control panel when it is about to be removed from hass."""
        _LOGGER.info("Stopping the Bosch Control Panel")
        self._alarm.remove_listener(self)
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
            await self._alarm.set_siren(False)
            # Clear the manual trigger
            self._manual_trigger = False
        # If alarm is armed anyway, proceed with the disarm, otherwise don't do anything
        elif self.state not in [STATE_ALARM_DISARMING, STATE_ALARM_DISARMED]:
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
            # Force update of the transition state
            await self.async_update_ha_state(force_refresh=True)
            # Send the code to change the state
            await self._alarm.send_keys(keys=code)
            self._transition_state = None
            # Force to get the status again
            # This is needed because the control panel doesn't return the
            # current status in the first message
            await self._alarm.get_status()
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error("Couldn't change the alarm to %s: %s", transition_state, ex)
            self._transition_state = None
            # Force update of the transition state
            await self.async_update_ha_state(force_refresh=True)

    def _time_synced(self) -> bool:
        cp_time = self._alarm.control_panel.time.time
        cur_time = datetime.now().time().replace(second=0, microsecond=0)
        cp_timedelta = timedelta(hours=cp_time.hour, minutes=cp_time.minute)
        cur_timedelta = timedelta(hours=cur_time.hour, minutes=cur_time.minute)
        diff_seconds = abs(cur_timedelta - cp_timedelta).total_seconds()

        return diff_seconds < TWO_MINUTES

    async def _sync_time(self):
        try:
            if self._time_synced():
                # Need to set the time in the control panel
                _LOGGER.info("Time is synchronized")
            else:
                _LOGGER.warning("Synchronizing the time")
                await self._alarm.set_time()
        except Exception:  # pylint: disable=broad-exception-caught
            _LOGGER.exception("Time synchronization failed")

    async def _siren_service(self, call: ServiceCall):
        status = bool(_strtobool(call.data[CONF_COMMAND]))
        await self._alarm.set_siren(status)
        self._manual_trigger = status

    async def _out_service(self, call: ServiceCall):
        idd: Id = call.data[CONF_ID]
        status = bool(_strtobool(call.data[CONF_COMMAND]))
        await self._alarm.set_output(idd, status)

    async def on_availability_changed(self, entity: Availability):  # noqa: D102
        _LOGGER.debug("Availability changed: %s", entity)
        await self.async_update_ha_state(force_refresh=True)

    async def on_siren_changed(self, entity: Siren):  # noqa: D102
        _LOGGER.debug("Siren changed: %s", entity)
        await self.async_update_ha_state(force_refresh=True)

    async def on_area_changed(self, entity: Area):
        _LOGGER.debug("Area changed: %s", entity)
        await self.async_update_ha_state(force_refresh=True)

    async def on_zone_changed(
        self, id: Id, entity: Zone
    ):  # pylint: disable=redefined-builtin
        _LOGGER.debug("Zone[%d] changed: %s", id, entity)
        await self.async_update_ha_state(force_refresh=True)

    async def on_output_changed(
        self, id: Id, entity: Output
    ):  # pylint: disable=redefined-builtin
        _LOGGER.debug("Output[%d] changed: %s", id, entity)
        await self.async_update_ha_state(force_refresh=True)

    async def on_time_changed(self, entity: Time):  # pylint: disable=redefined-builtin
        _LOGGER.debug("Time changed: %s", entity)
        await self._sync_time()
        await self.async_update_ha_state(force_refresh=True)

    async def on_changed(  # pylint: disable=redefined-builtin
        self, entity: ControlPanelEntity, id: Id | None = None
    ):
        await self.async_update_ha_state(force_refresh=True)
