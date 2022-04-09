"""The bosch_control_panel_cc880 integration."""
import asyncio
import logging

import voluptuous as vol
from bosch.control_panel.cc880p.cp import ControlPanel

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_PORT,
    DATA_BOSCH,
    DATA_OPTIONS_UPDATE_UNSUBSCRIBER,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the bosch_control_panel_cc880 component."""

    _LOGGER.info("Async Setup")

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ """

    _LOGGER.info("Async Setup Entry Start...")

    _success = False
    _ip = entry.data[CONF_HOST]
    _port = entry.data[CONF_PORT]
    _alarm = ControlPanel(
        ip=_ip,
        port=_port,
        loop=hass.loop,
        get_status_period_s=1.0
    )
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

    _LOGGER.info("Async Load Entry Done")

    return _success


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    _LOGGER.info("Async Unload Entry Start...")

    _success = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if _success:
        _LOGGER.info("Async Unload Entry Done")
        _alarm: ControlPanel = hass.data[DOMAIN].pop(entry.entry_id)[DATA_BOSCH]
        await _alarm.stop()
    else:
        _LOGGER.error("Async Unload Entry Error")

    return _success


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """ """

    _alarm = hass.data[DOMAIN][entry.entry_id][DATA_BOSCH]
    # TODO: Support for options update
    # _alarm.update_options(entry.options)

