"""The redy integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

from edp.redy.app import App

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up redy from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access

    _LOGGER.debug("Creating the Redy App")

    data = entry.data
    # Create the application
    app = App(
        username=data["username"],
        password=data["password"],
        user_pool_id=data["user_pool_id"],
        client_id=data["client_id"],
        region=data["region"],
        identity_id=data["identity_id"],
        identity_login=data["identity_login"],
    )

    _LOGGER.debug("Starting the app")

    await app.start()

    _LOGGER.debug("Redy App is running")

    hass.data[DOMAIN][entry.entry_id] = app

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
