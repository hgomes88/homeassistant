"""Constants for the bosch_control_panel_cc880 integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "bosch_control_panel_cc880"

PLATFORMS: Final = [Platform.ALARM_CONTROL_PANEL, Platform.BINARY_SENSOR]

DATA_BOSCH: Final = "bosch"

DATA_OPTIONS_UPDATE_UNSUBSCRIBER: Final = "options_update_unsubscriber"

TITLE: Final = "Bosch Alarm"
DEVICE_ID: Final = "bosch_control_panel"
MANUFACTURER: Final = "Bosch"
MODEL: Final = "cc880p"
SW_VERSION: Final = "v1.16"
HW_VERSION: Final = "unknown"


CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_MODEL: Final = "model"
CONF_INSTALLER_CODE: Final = "installer_code"
CONF_POLLING_PERIOD: Final = "polling_period"

# Only digits between 4 and 7 characters
CONF_DEFAULT_PORT: Final = 8899
# Pooling period in milliseconds
CONF_DEFAULT_POLLING_PERIOD = 1000
CONF_CODE_REGEX: Final = r"^\d{4,7}$"

CONF_STEP_CONNECTION = "conn"

SERVICE_SIREN: Final = "siren"
SERVICE_OUTPUT: Final = "output"
