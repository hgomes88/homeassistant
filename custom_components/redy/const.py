"""Constants for the redy integration."""

import logging


DOMAIN = "redy"

DEFAULT_REGION = "eu-west-1"
DEFAULT_USER_POOL_ID = f"{DEFAULT_REGION}_7qre3K7aN"
DEFAULT_CLIENT_ID = "78fe04ngpmrualq67a5p59sbeb"
DEFAULT_IDENTITY_POOL_ID = f"{DEFAULT_REGION}:a9a52b46-1722-49a0-8f8b-e8532c12abef"
DEFAULT_IDENTITY_LOGIN = (
    f"cognito-idp.{DEFAULT_REGION}.amazonaws.com/{DEFAULT_USER_POOL_ID}"
)

ENERGY_GRID_CONSUMPTION_DAY_KEY = "energy_grid_consumption_day"
ENERGY_GRID_CONSUMPTION_DAY_NAME = "Energy Grid Consumption Today"
ENERGY_GRID_CONSUMPTION_COST_DAY_KEY = "energy_grid_consumption_cost_day"
ENERGY_GRID_CONSUMPTION_COST_DAY_NAME = "Energy Grid Consumption Cost Today"

ENERGY_GRID_INJECTION_DAY_KEY = "energy_grid_injection_day"
ENERGY_GRID_INJECTION_DAY_NAME = "Energy Grid Injection Today"

ENERGY_SOLAR_PRODUCTION_DAY_KEY = "energy_solar_production_day"
ENERGY_SOLAR_PRODUCTION_DAY_NAME = "Energy Solar Production Today"

ENERGY_GRID_CONSUMPTION_MONTH_KEY = "energy_grid_consumption_month"
ENERGY_GRID_CONSUMPTION_MONTH_NAME = "Energy Grid Consumption This Month"
ENERGY_GRID_CONSUMPTION_COST_MONTH_KEY = "energy_grid_consumption_cost_month"
ENERGY_GRID_CONSUMPTION_COST_MONTH_NAME = "Energy Grid Consumption Cost This Month"

ENERGY_GRID_INJECTION_MONTH_KEY = "energy_grid_injection_month"
ENERGY_GRID_INJECTION_MONTH_NAME = "Energy Grid Injection This Month"

ENERGY_SOLAR_PRODUCTION_MONTH_KEY = "energy_solar_production_month"
ENERGY_SOLAR_PRODUCTION_MONTH_NAME = "Energy Solar Production This Month"

ENERGY_GRID_CONSUMPTION_YEAR_KEY = "energy_grid_consumption_year"
ENERGY_GRID_CONSUMPTION_YEAR_NAME = "Energy Grid Consumption This Year"
ENERGY_GRID_CONSUMPTION_COST_YEAR_KEY = "energy_grid_consumption_cost_year"
ENERGY_GRID_CONSUMPTION_COST_YEAR_NAME = "Energy Grid Consumption Cost This Year"

ENERGY_GRID_INJECTION_YEAR_KEY = "energy_grid_injection_year"
ENERGY_GRID_INJECTION_YEAR_NAME = "Energy Grid Injection This Year"

ENERGY_SOLAR_PRODUCTION_YEAR_KEY = "energy_solar_production_year"
ENERGY_SOLAR_PRODUCTION_YEAR_NAME = "Energy Solar Production This Year"

POWER_GRID_CONSUMPTION_KEY = "power_grid_consumption"
POWER_GRID_CONSUMPTION_NAME = "Power Grid Consumption"

POWER_GRID_INJECTION_KEY = "power_grid_injection"
POWER_GRID_INJECTION_NAME = "Power Grid Injection"

POWER_GRID_PRODUCTION_KEY = "power_grid_production"
POWER_GRID_PRODUCTION_NAME = "Power Grid Production"

LOGGER = logging.getLogger(__package__)
