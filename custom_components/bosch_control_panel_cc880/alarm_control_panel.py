import asyncio
import logging
from signal import alarm

from .const import DATA_BOSCH, DOMAIN
from .alarm import Alarm, ArmingMode

from homeassistant.components.alarm_control_panel import (
    FORMAT_NUMBER,
    AlarmControlPanelEntity,
)
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_DISARMING,
    STATE_ALARM_TRIGGERED,
    STATE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:security"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up entry."""

    # Create the bosch alarm system

    _LOGGER.debug("Async Setup Entry Alarm Control Panel")

    _alarm = hass.data[DOMAIN][config_entry.entry_id][DATA_BOSCH]

    async_add_entities([BoschAlarmControlPanel(_alarm)])


async def async_unload_entry(hass, config_entry):
    """Unload entry."""

    _LOGGER.debug("Async Unload Entry Alarm Control Panel")


async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""

    _LOGGER.debug("Async Remove Entry Alarm Control Panel")


class BoschAlarmControlPanel(AlarmControlPanelEntity):
    """Bosch Control Panel."""

    def __init__(self, alarm: Alarm) -> None:

        _LOGGER.info("Starting the Bosch Control Panel")

        self._state = STATE_UNKNOWN
        self._tmp_state = STATE_UNKNOWN
        self._alarm: Alarm = alarm

        asyncio.create_task(self._init())

        _LOGGER.info("Started the Bosch Control Panel")

    async def _init(self):
        pass

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
    def changed_by(self):
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
    def state(self):
        """Return the state of the device."""
        if self._tmp_state is not STATE_UNKNOWN:
            self._state = self._tmp_state
        else:
            mode = self._alarm.areas[1].mode
            if mode == ArmingMode.DISARMED and self._state != STATE_ALARM_DISARMED:
                self._state = STATE_ALARM_DISARMED
            elif (
                mode == ArmingMode.ARMED_AWAY and self._state != STATE_ALARM_ARMED_AWAY
            ):
                self._state = STATE_ALARM_ARMED_AWAY
            elif mode == ArmingMode.ARMED_STAY and self.state != STATE_ALARM_ARMED_HOME:
                self._state = STATE_ALARM_ARMED_HOME

        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY

    async def _change_state(self, code, state):
        self._tmp_state = state
        await self.async_update_ha_state()
        await self._alarm.send_keys(code)
        self._tmp_state = STATE_UNKNOWN
        await self.async_update_ha_state(force_refresh=True)

    async def async_alarm_disarm(self, code=None):
        _LOGGER.info("Disarming with code %s", code)
        if self.state not in [STATE_ALARM_DISARMING, STATE_ALARM_DISARMED]:
            await self._change_state(code=f"{code}0#", state=STATE_ALARM_DISARMING)

    async def async_alarm_arm_home(self, code=None):
        _LOGGER.info("Arming Home with code %s", code)
        if self.state == STATE_ALARM_DISARMED:
            await self._change_state(code=f"{code}0*", state=STATE_ALARM_ARMING)

    async def async_alarm_arm_away(self, code=None):
        _LOGGER.info("Arming Away with code %s", code)
        if self.state == STATE_ALARM_DISARMED:
            await self._change_state(code=f"{code}0#", state=STATE_ALARM_ARMING)

    def alarm_trigger(self, code=None):
        _LOGGER.info("Triggering the Alarm with code %s", code)

    def async_alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""

        _LOGGER.info("Arming with custom bypass with code %s", code)

    async def async_update(self):
        _LOGGER.info("Forced Update")
        await self._alarm.get_status_cmd()
