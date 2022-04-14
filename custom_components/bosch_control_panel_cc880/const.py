"""Constants for the bosch_control_panel_cc880 integration."""

from typing import Final


DOMAIN: Final = "bosch_control_panel_cc880"

PLATFORMS: Final = ["alarm_control_panel", "binary_sensor"]

DATA_BOSCH: Final = "bosch"

DATA_OPTIONS_UPDATE_UNSUBSCRIBER: Final = "options_update_unsubscriber"

TITLE: Final = "Bosch Alarm"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"

SERVICE_SIREN: Final = "siren"
SERVICE_OUTPUT: Final = "output"
