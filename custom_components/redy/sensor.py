"""Support for Efergy sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_WATT, CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    ENERGY_GRID_CONSUMPTION_COST_DAY_NAME,
    ENERGY_GRID_CONSUMPTION_DAY_KEY,
    ENERGY_GRID_CONSUMPTION_DAY_NAME,
    ENERGY_GRID_INJECTION_DAY_KEY,
    ENERGY_GRID_INJECTION_DAY_NAME,
    ENERGY_SOLAR_PRODUCTION_DAY_KEY,
    ENERGY_SOLAR_PRODUCTION_DAY_NAME,
    ENERGY_GRID_CONSUMPTION_MONTH_KEY,
    ENERGY_GRID_CONSUMPTION_MONTH_NAME,
    ENERGY_GRID_INJECTION_MONTH_KEY,
    ENERGY_GRID_INJECTION_MONTH_NAME,
    ENERGY_SOLAR_PRODUCTION_MONTH_KEY,
    ENERGY_SOLAR_PRODUCTION_MONTH_NAME,
    ENERGY_GRID_CONSUMPTION_YEAR_KEY,
    ENERGY_GRID_CONSUMPTION_YEAR_NAME,
    ENERGY_GRID_INJECTION_YEAR_KEY,
    ENERGY_GRID_INJECTION_YEAR_NAME,
    ENERGY_SOLAR_PRODUCTION_YEAR_KEY,
    ENERGY_SOLAR_PRODUCTION_YEAR_NAME,
    ENERGY_GRID_CONSUMPTION_COST_DAY_KEY,
    ENERGY_GRID_CONSUMPTION_COST_MONTH_KEY,
    ENERGY_GRID_CONSUMPTION_COST_MONTH_NAME,
    ENERGY_GRID_CONSUMPTION_COST_YEAR_KEY,
    ENERGY_GRID_CONSUMPTION_COST_YEAR_NAME,
    POWER_GRID_CONSUMPTION_KEY,
    POWER_GRID_CONSUMPTION_NAME,
    POWER_GRID_INJECTION_KEY,
    POWER_GRID_INJECTION_NAME,
    POWER_GRID_PRODUCTION_KEY,
    POWER_GRID_PRODUCTION_NAME,
)

from .redy_sensor import RedySensor
from .redy_sensor_energy import RedyEnergySensor, RedyEnergySensorEntityDescription
from .redy_sensor_power import RedyPowerSensor, RedyPowerSensorEntityDescription
from .redy_sensor_energy_cost import RedyEnergyCostSensor, RedyEnergyCostSensorEntityDescription

from edp.redy.app import App, EnergyType, EnergyValues


def get_entities(app: App) -> list[RedySensor]:
    """Return the tuple of all the sensors."""
    return [
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_DAY_KEY,
                name=ENERGY_GRID_CONSUMPTION_DAY_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_day,
                energy_type=app.energy.consumed,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_INJECTION_DAY_KEY,
                name=ENERGY_GRID_INJECTION_DAY_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_day,
                energy_type=app.energy.injected,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_SOLAR_PRODUCTION_DAY_KEY,
                name=ENERGY_SOLAR_PRODUCTION_DAY_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_day,
                energy_type=app.energy.produced,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_MONTH_KEY,
                name=ENERGY_GRID_CONSUMPTION_MONTH_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_month,
                energy_type=app.energy.consumed,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_INJECTION_MONTH_KEY,
                name=ENERGY_GRID_INJECTION_MONTH_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_month,
                energy_type=app.energy.injected,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_SOLAR_PRODUCTION_MONTH_KEY,
                name=ENERGY_SOLAR_PRODUCTION_MONTH_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_month,
                energy_type=app.energy.produced,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_YEAR_KEY,
                name=ENERGY_GRID_CONSUMPTION_YEAR_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_year,
                energy_type=app.energy.consumed,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_GRID_INJECTION_YEAR_KEY,
                name=ENERGY_GRID_INJECTION_YEAR_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_year,
                energy_type=app.energy.injected,
            )
        ),
        RedyEnergySensor(
            RedyEnergySensorEntityDescription(
                key=ENERGY_SOLAR_PRODUCTION_YEAR_KEY,
                name=ENERGY_SOLAR_PRODUCTION_YEAR_NAME,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_year,
                energy_type=app.energy.produced,
            )
        ),
        RedyEnergyCostSensor(
            RedyEnergyCostSensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_COST_DAY_KEY,
                name=ENERGY_GRID_CONSUMPTION_COST_DAY_NAME,
                device_class=SensorDeviceClass.MONETARY,
                native_unit_of_measurement=CURRENCY_EURO,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_day,
                energy_type=app.energy.consumed,
            )
        ),
        RedyEnergyCostSensor(
            RedyEnergyCostSensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_COST_MONTH_KEY,
                name=ENERGY_GRID_CONSUMPTION_COST_MONTH_NAME,
                device_class=SensorDeviceClass.MONETARY,
                native_unit_of_measurement=CURRENCY_EURO,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_month,
                energy_type=app.energy.consumed,
            )
        ),
        RedyEnergyCostSensor(
            RedyEnergyCostSensorEntityDescription(
                key=ENERGY_GRID_CONSUMPTION_COST_YEAR_KEY,
                name=ENERGY_GRID_CONSUMPTION_COST_YEAR_NAME,
                device_class=SensorDeviceClass.MONETARY,
                native_unit_of_measurement=CURRENCY_EURO,
                state_class=SensorStateClass.TOTAL_INCREASING,
                energy_method=energy_year,
                energy_type=app.energy.consumed,
            )
        ),
        RedyPowerSensor(
            RedyPowerSensorEntityDescription(
                key=POWER_GRID_CONSUMPTION_KEY,
                name=POWER_GRID_CONSUMPTION_NAME,
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=POWER_WATT,
                state_class=SensorStateClass.MEASUREMENT,
                power_type=app.power.consumed,
            )
        ),
        RedyPowerSensor(
            RedyPowerSensorEntityDescription(
                key=POWER_GRID_INJECTION_KEY,
                name=POWER_GRID_INJECTION_NAME,
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=POWER_WATT,
                state_class=SensorStateClass.MEASUREMENT,
                power_type=app.power.injected,
            )
        ),
        RedyPowerSensor(
            RedyPowerSensorEntityDescription(
                key=POWER_GRID_PRODUCTION_KEY,
                name=POWER_GRID_PRODUCTION_NAME,
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=POWER_WATT,
                state_class=SensorStateClass.MEASUREMENT,
                power_type=app.power.produced,
            )
        ),
    ]


async def energy_day(energy: EnergyType) -> EnergyValues:
    """Get the today's energy."""
    return await energy.today


async def energy_month(energy: EnergyType) -> EnergyValues:
    """Get the energy of this month."""
    return await energy.this_month


async def energy_year(energy: EnergyType) -> EnergyValues:
    """Get the energy of this year."""
    return await energy.this_year


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: entity_platform.AddEntitiesCallback,
) -> None:
    """Set up Efergy sensors."""
    app: App = hass.data[DOMAIN][entry.entry_id]
    entities = get_entities(app)
    async_add_entities(entities, True)
