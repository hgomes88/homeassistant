"""The bosch_control_panel_cc880 integration."""
import logging

from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models.cp import CpVersion

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_HOST,
    CONF_INSTALLER_CODE,
    CONF_MODEL,
    CONF_POLLING_PERIOD,
    CONF_PORT,
    DATA_BOSCH,
    DEVICE_ID,
    DOMAIN,
    HW_VERSION,
    MANUFACTURER,
    MODEL,
    PLATFORMS,
    SW_VERSION,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entry function during initialization of bosch control panel.

    Args:
        hass (HomeAssistant): Homeassistant object
        entry (ConfigEntry): Configuration needed for the initialization of the
            control panel

    Returns:
        bool: Return True if the setup was successfully done. False otherwise
    """

    _LOGGER.info("Async Setup Entry Start")

    # Default data is empty
    hass.data.setdefault(DOMAIN, {})

    # Create the control panel
    _alarm = await CP(
        ip=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        model=CpVersion[entry.data[CONF_MODEL]].value,
        installer_code=entry.data[CONF_INSTALLER_CODE],
        poll_period=entry.data[CONF_POLLING_PERIOD] / 1000,
        loop=hass.loop,
    ).start()

    hass.data[DOMAIN][entry.entry_id] = {DATA_BOSCH: _alarm}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Async Load Entry Done")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    _LOGGER.info("Async Unload Entry Start")

    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS
    ):
        _alarm: CP = hass.data[DOMAIN].pop(entry.entry_id)[DATA_BOSCH]
        await _alarm.stop()
        _LOGGER.info("Async Unload Entry Done")
    else:
        _LOGGER.error("Async Unload Entry Error")

    return unload_ok


async def options_update_listener(
    hass: HomeAssistant,
    entry: ConfigEntry
) -> None:
    """Update the currently available control panel.

    Args:
        hass (HomeAssistant): The Homeassistant object
        entry (ConfigEntry): The options needed to update the control panel
    """
    # _alarm = hass.data[DOMAIN][entry.entry_id][DATA_BOSCH]
    # _alarm.update_options(entry.options)
    return


class BoschControlPanelDevice(Entity):
    """Class used to link all the control panel etities into a device."""

    @property
    def device_info(self) -> dict[str, str]:
        """Get the device information.

        Returns:
            dict[str, str]: THe dictionary with the information of the device
        """
        return {
            "identifiers": {(DOMAIN, DEVICE_ID)},
            "name": TITLE,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": SW_VERSION,
            "hw_version": HW_VERSION,
            "via_device": "none",
        }
