"""Config flow for redy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DEFAULT_REGION,
    DEFAULT_USER_POOL_ID,
    DEFAULT_CLIENT_ID,
    DEFAULT_IDENTITY_POOL_ID,
    DEFAULT_IDENTITY_LOGIN,
)

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("region", default=DEFAULT_REGION): str,
        vol.Required("user_pool_id", default=DEFAULT_USER_POOL_ID): str,
        vol.Required("client_id", default=DEFAULT_CLIENT_ID): str,
        vol.Required("identity_id", default=DEFAULT_IDENTITY_POOL_ID): str,
        vol.Required("identity_login", default=DEFAULT_IDENTITY_LOGIN): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # _LOGGER.debug("Creating the Redy App")

    # # Create the application
    # app = App(
    #     username=data["username"],
    #     password=data["password"],
    #     user_pool_id=data["user_pool_id"],
    #     client_id=data["client_id"],
    #     region=data["region"],
    #     identity_id=data["identity_id"],
    #     identity_login=data["identity_login"],
    # )

    # try:
    #     # Start (includes logging in)
    #     _LOGGER.debug("Starting the Redy App")
    #     await app.start()
    # except Exception as ex:
    #     raise CannotConnect from ex

    # _LOGGER.debug("Redy App Started")

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    # hub = PlaceholderHub(data["host"])

    # if not await hub.authenticate(data["username"], data["password"]):
    #     raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for redy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="Redy", data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
