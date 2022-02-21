"""The bosch_control_panel_cc880 integration."""
import asyncio
import logging

import voluptuous as vol
from .alarm import Alarm

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DATA_BOSCH, DATA_OPTIONS_UPDATE_UNSUBSCRIBER, DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the bosch_control_panel_cc880 component."""

    _LOGGER.info("Async Setup")

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    _LOGGER.info("Async Setup Entry")

    _success = False
    _alarm = Alarm()
    _success = await _alarm.start()

    if _success:

        hass.data[DOMAIN][entry.entry_id] = {
            DATA_BOSCH: _alarm,
            DATA_OPTIONS_UPDATE_UNSUBSCRIBER: entry.add_update_listener(
                options_update_listener
            ),
        }

        for component in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, component)
            )

    return _success


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    _LOGGER.info("Async Unload Entry")

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    # if unload_ok:
    #     hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _alarm = hass.data[DOMAIN][entry.entry_id][DATA_BOSCH]
    # TODO: Support for options update
    # _alarm.update_options(entry.options)

