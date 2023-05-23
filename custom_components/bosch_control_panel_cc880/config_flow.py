"""Config flow for bosch_control_panel_cc880 integration."""
from ipaddress import ip_address
import logging
from typing import Any

from bosch.control_panel.cc880p.cp import CP
from bosch.control_panel.cc880p.models.cp import CpVersion
import voluptuous as vol

from homeassistant.config_entries import CONN_CLASS_LOCAL_POLL, ConfigFlow
from homeassistant.const import CONF_BASE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .config_validation import SchemaType, SchemaTypes
from .const import (  # pylint:disable=unused-import
    CONF_CODE_REGEX,
    CONF_DEFAULT_POLLING_PERIOD,
    CONF_DEFAULT_PORT,
    CONF_HOST,
    CONF_INSTALLER_CODE,
    CONF_MODEL,
    CONF_POLLING_PERIOD,
    CONF_PORT,
    DOMAIN,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

SCHEMA_TYPES = SchemaTypes(
    {
        CONF_HOST: SchemaType(
            str, vol.All(str, vol.Any(cv.url, ip_address), msg="invalid_host")
        ),
        CONF_PORT: SchemaType(int, vol.All(cv.port, msg="invalid_port")),
        CONF_MODEL: SchemaType(
            SelectSelector(
                SelectSelectorConfig(
                    options=sorted([cp.name for cp in CpVersion]),
                    mode=SelectSelectorMode.DROPDOWN,
                )
            )
        ),
        CONF_INSTALLER_CODE: SchemaType(
            str,
            vol.All(
                str, cv.matches_regex(CONF_CODE_REGEX), msg="invalid_installer_code"
            ),
        ),
        CONF_POLLING_PERIOD: SchemaType(
            int, vol.All(cv.positive_int, msg="invalid_polling_period")
        ),
    }
)


def _schema(data: dict[str, Any] = None, validation=False):
    """Get the schema to be applied.

    If is the first time the validation occurs (data = None), then the
        default values are applied.
    If the validation is not happening the first time, the previously
        inserted values will be used as default.
    If validation flag is used, then a schema for backend validation is
        used, otherwise, a presentation schema is returned.
        This is needed because there are some limitations on providing all
        kinds of validation to the frontend.
    """
    host = vol.UNDEFINED
    port = CONF_DEFAULT_PORT
    code = vol.UNDEFINED
    pol_period = CONF_DEFAULT_POLLING_PERIOD

    if data:
        host = data.get(CONF_HOST, host)
        port = data.get(CONF_PORT, port)
        code = data.get(CONF_INSTALLER_CODE, code)
        pol_period = data.get(CONF_POLLING_PERIOD, pol_period)

    schemas = SCHEMA_TYPES.get_schemas(validation)

    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): schemas[CONF_HOST],
            vol.Required(CONF_PORT, default=port): schemas[CONF_PORT],
            vol.Required(CONF_MODEL, default=CpVersion.S16_V14.name): schemas[
                CONF_MODEL
            ],
            vol.Optional(CONF_INSTALLER_CODE, default=code): schemas[
                CONF_INSTALLER_CODE
            ],
            vol.Optional(CONF_POLLING_PERIOD, default=pol_period): schemas[
                CONF_POLLING_PERIOD
            ],
        }
    )


def _validation_schema(data: dict[str, Any] = None):
    """Return the validation schema.

    Applies the previous inputs as defaults if any.
    """
    return _schema(data, True)


def _presentation_schema(data: dict[str, Any] = None):
    """Return the validation schema.

    Applies the previous inputs as defaults if any.
    """
    return _schema(data, False)


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the inputs.

    Args:
        hass (HomeAssistant): Homeassistant object
        data : The data to validate
    """

    errors = {}
    try:
        _validation_schema()(data)
    except vol.MultipleInvalid as exc:
        for error in exc.errors:
            path = error.path[0]
            msg = error.msg
            errors[path] = msg
    except:  # pylint: disable=bare-except
        errors[CONF_BASE] = "unknown"

    # Try to connect and start the control panel
    cp = CP(  # pylint: disable=invalid-name
        ip=data[CONF_HOST],
        port=data[CONF_PORT],
        model=CpVersion[data[CONF_MODEL]].value,
        installer_code=data[CONF_INSTALLER_CODE],
        poll_period=data[CONF_POLLING_PERIOD] / 1000,
        loop=hass.loop,
    )
    try:
        await cp.start()
        assert cp.control_panel.availability.available
    except Exception:  # pylint: disable=broad-exception-caught
        errors[CONF_BASE] = "cannot_connect"
    finally:
        await cp.stop()

    return errors


class ControlPanelConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for bosch_control_panel_cc880."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        _LOGGER.info("Async Step User")
        errors = {}

        if user_input is not None:
            errors = await _validate_input(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title=TITLE, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_presentation_schema(user_input),
            errors=errors,
        )
