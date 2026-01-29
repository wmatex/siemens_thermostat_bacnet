from typing import Any, Optional

from .bacnet import (
    DEFAULT_BACNET_PORT,
    DeviceProperty,
    ObjectType,
    BACnetClient,
    DeviceState,
    ReadValue,
)

from .const import (
    DEVICE_PROPERTIES,
    TEMPERATURE_SENSOR,
    PUMP_POSITION,
    PRESENT_HEATING_SETPOINT,
    BUILT_IN_ROOM_AIR_RELATIVE_HUMIDITY_SENSOR,
    AUTOMATION_STATION_DIAGNOSTICS,
    IO_BUS_DIAGNOSTICS,
    ROOM_TEMPERATURE_RESULT,
    PRESENT_HEATING_SETPOINT_COMFORT,
    PRESENT_HEATING_SETPOINT_ECONOMY,
    PRESENT_HEATING_SETPOINT_UNOCCUPIED,
    PRESENT_HEATING_SETPOINT_PROTECTION,
    HEATING_SETPOINT_COMFORT,
    HEATING_SETPOINT_ECONOMY,
    HEATING_SETPOINT_UNOCCUPIED,
    HEATING_SETPOINT_PROTECTION,
    ROOM_TEMPERATURE_SETPOINT,
    ROOM_TEMPERATURE_SETPOINT_SHIFT,
    ROOM_RELATIVE_HUMIDITY,
    ROOM_TEMPERATURE,
    FLOOR_HEATING_REQUEST,
    FLOOR_HEATING_PUMP_POSITION_VALUE,
    EFFECTIVE_ROOM_TEMPERATURE,
    EFFECTIVE_OUTSIDE_AIR_TEMPERATURE,
    MAX_HEATING_SETPOINT,
    WARM_UP_GRADIENT,
    BUILT_IN_TEMPERATURE_SENSOR_ADJUSTMENT,
    ROOM_AIR_QUALITY,
    ROOM_AIR_QUALITY_RESULT,
    ROOM_RELATIVE_HUMIDITY_RESULT,
    APPLICATION_NUMBER,
    BUILT_IN_TOUCH_DETECTOR,
    TEMPORARY_COMFORT_BUTTON,
    COMFORT_BUTTON,
    RESET_ROOM_ENERGY_EFFICIENCY_INDICATION,
    ROOM_PRESENCE_DETECTION,
    ROOM_PRESENCE_RESULT,
    ENABLE_HEATING_CONTROL,
    WARM_UP_REQUEST,
    ROOM_WINDOW_STATE,
    WINDOW_CONTACT_RESULT,
    FLOOR_HEATING_AVAILABLE,
    ENABLE_KICK,
    GEOFENCING_TRIGGER,
    IO_BUS_MANAGEMENT,
    ONBOARD_MODULE_BUILTIN_5SEN_1,
    ONBOARD_MODULE_2UI_1,
    OFF_PROTECTION_CONFIGURATION,
    CENTRAL_OPERATING_MODE_COMMAND,
    OSSC_STATE,
    ROOM_OPERATING_MODE,
    OCCUPANCY_MODE,
    ROOM_ENERGY_EFFICIENCY_INDICATION,
    HVAC_ENERGY_EFFICIENCY_INDICATION,
    HEATING_COOLING_STATE,
    HVAC_PRESENCE_MODE,
    PLANT_OPERATING_MODE,
    NEXT_ROOM_OPERATING_MODE,
    PRESENT_OPERATING_MODE_REASON,
    FLOOR_HEATING_DEVICE_MODE,
    FLOOR_HEATING_HOT_WATER_DEMAND,
    PRESENT_HEATING_CONTROLLER_SETTING,
    HEATING_DEVICE_TYPE,
    PRESENT_PLANT_OPERATING_MODE,
    HEATING_COOLING_DEMAND,
    HEATING_CONTROL_LOOP,
    OPTIMUM_START_CONTROL_SETTING,
    ROOM_AIR_QUALITY_INDICATION,
)

PRECISION = 3


class SiemensBACnet:
    def __init__(
        self,
        device_address: str,
        device_id: int,
        port: int = DEFAULT_BACNET_PORT,
    ) -> None:
        self.bacnet = BACnetClient(device_address, port)
        self.device_id = device_id
        self._state: Optional[DeviceState] = None

    @property
    def _device_property(self) -> DeviceProperty:
        return DeviceProperty(
            ObjectType.DEVICE,
            self.device_id,
            read_values=[ReadValue.OBJECT_NAME, ReadValue.DESCRIPTION],
        )

    async def update(self) -> None:
        """Refresh local device state."""
        device_properties = DEVICE_PROPERTIES + [self._device_property]
        state: DeviceState = {}
        chunk_size = 20

        for i in range(0, len(device_properties), chunk_size):
            chunk = device_properties[i : i + chunk_size]
            state.update(await self.bacnet.read_multiple(chunk))

        self._state = state

    def _get_value(
        self,
        device_property: DeviceProperty,
        value_name: Optional[ReadValue] = None,
    ) -> Any:
        if self._state is None:
            raise Exception("must run 'update()' method first")

        if value_name is None:
            value_name = ReadValue.PRESENT_VALUE

        return dict(self._state[device_property.object_identifier])[value_name]

    async def _set_value(self, device_property: DeviceProperty, value: Any) -> None:
        await self.bacnet.write(device_property, value)
        await self.update()

    @property
    def device_name(self) -> str:
        """Return device name, e.g.: Flexit Nordic"""
        device_name_from_device = self._get_value(
            self._device_property, ReadValue.OBJECT_NAME
        )
        return device_name_from_device

    @property
    def serial_number(self) -> str:
        """Return device's serial number, e.g.: 800220-000000."""
        serial_number = self._get_value(self._device_property, ReadValue.DESCRIPTION)

        return serial_number

    @property
    def heating_setpoint(self) -> float:
        return float(
            round(
                self._get_value(PRESENT_HEATING_SETPOINT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def heating_setpoint_priorities(self) -> float:
        return self._get_value(PRESENT_HEATING_SETPOINT, ReadValue.PRIORITY_ARRAY)

    async def set_heating_setpoint(self, temp: float | None) -> None:
        """Set heating setpoint temperature in degrees Celsius."""
        await self._set_value(PRESENT_HEATING_SETPOINT, temp)

    @property
    def floor_pump_position(self) -> float:
        """Outside air temperature in degrees Celsius, e.g. 14.3."""
        return float(
            round(self._get_value(PUMP_POSITION, ReadValue.PRESENT_VALUE), PRECISION)
        )

    @property
    def floor_pump_position_priorities(self) -> list[Any]:
        """Outside air temperature in degrees Celsius, e.g. 14.3."""
        return self._get_value(PUMP_POSITION, ReadValue.PRIORITY_ARRAY)

    @property
    def built_in_room_air_temperature_sensor(self) -> float:
        return float(
            round(
                self._get_value(TEMPERATURE_SENSOR, ReadValue.PRESENT_VALUE), PRECISION
            )
        )

    @property
    def built_in_room_air_relative_humidity_sensor(self) -> float:
        return float(
            round(
                self._get_value(
                    BUILT_IN_ROOM_AIR_RELATIVE_HUMIDITY_SENSOR,
                    ReadValue.PRESENT_VALUE,
                ),
                PRECISION,
            )
        )

    @property
    def automation_station_diagnostics(self) -> float:
        return float(
            round(
                self._get_value(
                    AUTOMATION_STATION_DIAGNOSTICS, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def io_bus_diagnostics(self) -> float:
        return float(
            round(
                self._get_value(IO_BUS_DIAGNOSTICS, ReadValue.PRESENT_VALUE), PRECISION
            )
        )

    @property
    def room_temperature_result(self) -> float:
        return float(
            round(
                self._get_value(ROOM_TEMPERATURE_RESULT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def present_heating_setpoint_comfort(self) -> float:
        return float(
            round(
                self._get_value(
                    PRESENT_HEATING_SETPOINT_COMFORT, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def present_heating_setpoint_economy(self) -> float:
        return float(
            round(
                self._get_value(
                    PRESENT_HEATING_SETPOINT_ECONOMY, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def present_heating_setpoint_unoccupied(self) -> float:
        return float(
            round(
                self._get_value(
                    PRESENT_HEATING_SETPOINT_UNOCCUPIED, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def present_heating_setpoint_protection(self) -> float:
        return float(
            round(
                self._get_value(
                    PRESENT_HEATING_SETPOINT_PROTECTION, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def heating_setpoint_comfort(self) -> float:
        return float(
            round(
                self._get_value(HEATING_SETPOINT_COMFORT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def heating_setpoint_comfort_priorities(self) -> list[Any]:
        return self._get_value(HEATING_SETPOINT_COMFORT, ReadValue.PRIORITY_ARRAY)

    async def set_heating_setpoint_comfort(self, value: Any | None) -> None:
        await self._set_value(HEATING_SETPOINT_COMFORT, value)

    @property
    def heating_setpoint_economy(self) -> float:
        return float(
            round(
                self._get_value(HEATING_SETPOINT_ECONOMY, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def heating_setpoint_unoccupied(self) -> float:
        return float(
            round(
                self._get_value(HEATING_SETPOINT_UNOCCUPIED, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def heating_setpoint_protection(self) -> float:
        return float(
            round(
                self._get_value(HEATING_SETPOINT_PROTECTION, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def room_temperature_setpoint(self) -> float:
        return float(
            round(
                self._get_value(ROOM_TEMPERATURE_SETPOINT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def room_temperature_setpoint_priorities(self) -> list[Any]:
        return self._get_value(ROOM_TEMPERATURE_SETPOINT, ReadValue.PRIORITY_ARRAY)

    async def set_room_temperature_setpoint(self, value: Any | None) -> None:
        await self._set_value(ROOM_TEMPERATURE_SETPOINT, value)

    @property
    def room_temperature_setpoint_shift(self) -> float:
        return float(
            round(
                self._get_value(
                    ROOM_TEMPERATURE_SETPOINT_SHIFT, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def room_temperature_setpoint_shift_priorities(self) -> list[Any]:
        return self._get_value(
            ROOM_TEMPERATURE_SETPOINT_SHIFT, ReadValue.PRIORITY_ARRAY
        )

    async def set_room_temperature_setpoint_shift(self, value: Any | None) -> None:
        await self._set_value(ROOM_TEMPERATURE_SETPOINT_SHIFT, value)

    @property
    def room_relative_humidity(self) -> float:
        return float(
            round(
                self._get_value(ROOM_RELATIVE_HUMIDITY, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def room_temperature(self) -> float:
        return float(
            round(self._get_value(ROOM_TEMPERATURE, ReadValue.PRESENT_VALUE), PRECISION)
        )

    @property
    def floor_heating_request(self) -> float:
        return float(
            round(
                self._get_value(FLOOR_HEATING_REQUEST, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def floor_heating_pump_position_value(self) -> float:
        return float(
            round(
                self._get_value(
                    FLOOR_HEATING_PUMP_POSITION_VALUE, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def floor_heating_pump_position_value_priorities(self) -> list[Any]:
        return self._get_value(
            FLOOR_HEATING_PUMP_POSITION_VALUE, ReadValue.PRIORITY_ARRAY
        )

    async def set_floor_heating_pump_position_value(self, value: Any | None) -> None:
        await self._set_value(FLOOR_HEATING_PUMP_POSITION_VALUE, value)

    @property
    def effective_room_temperature(self) -> float:
        return float(
            round(
                self._get_value(EFFECTIVE_ROOM_TEMPERATURE, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def effective_outside_air_temperature(self) -> float:
        return float(
            round(
                self._get_value(
                    EFFECTIVE_OUTSIDE_AIR_TEMPERATURE, ReadValue.PRESENT_VALUE
                ),
                PRECISION,
            )
        )

    @property
    def max_heating_setpoint(self) -> float:
        return float(
            round(
                self._get_value(MAX_HEATING_SETPOINT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def warm_up_gradient(self) -> float:
        return float(
            round(self._get_value(WARM_UP_GRADIENT, ReadValue.PRESENT_VALUE), PRECISION)
        )

    @property
    def built_in_temperature_sensor_adjustment(self) -> float:
        return float(
            round(
                self._get_value(
                    BUILT_IN_TEMPERATURE_SENSOR_ADJUSTMENT,
                    ReadValue.PRESENT_VALUE,
                ),
                PRECISION,
            )
        )

    @property
    def room_air_quality(self) -> float:
        return float(
            round(self._get_value(ROOM_AIR_QUALITY, ReadValue.PRESENT_VALUE), PRECISION)
        )

    @property
    def room_air_quality_result(self) -> float:
        return float(
            round(
                self._get_value(ROOM_AIR_QUALITY_RESULT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def room_relative_humidity_result(self) -> float:
        return float(
            round(
                self._get_value(ROOM_RELATIVE_HUMIDITY_RESULT, ReadValue.PRESENT_VALUE),
                PRECISION,
            )
        )

    @property
    def application_number(self) -> float:
        return float(
            round(
                self._get_value(APPLICATION_NUMBER, ReadValue.PRESENT_VALUE), PRECISION
            )
        )

    @property
    def built_in_touch_detector(self) -> Any:
        return self._get_value(BUILT_IN_TOUCH_DETECTOR, ReadValue.PRESENT_VALUE)

    @property
    def temporary_comfort_button(self) -> Any:
        return self._get_value(TEMPORARY_COMFORT_BUTTON, ReadValue.PRESENT_VALUE)

    @property
    def temporary_comfort_button_priorities(self) -> list[Any]:
        return self._get_value(TEMPORARY_COMFORT_BUTTON, ReadValue.PRIORITY_ARRAY)

    async def set_temporary_comfort_button(self, value: Any | None) -> None:
        await self._set_value(TEMPORARY_COMFORT_BUTTON, value)

    @property
    def comfort_button(self) -> Any:
        return self._get_value(COMFORT_BUTTON, ReadValue.PRESENT_VALUE)

    @property
    def comfort_button_priorities(self) -> list[Any]:
        return self._get_value(COMFORT_BUTTON, ReadValue.PRIORITY_ARRAY)

    async def set_comfort_button(self, value: Any | None) -> None:
        await self._set_value(COMFORT_BUTTON, value)

    @property
    def reset_room_energy_efficiency_indication(self) -> Any:
        return self._get_value(
            RESET_ROOM_ENERGY_EFFICIENCY_INDICATION, ReadValue.PRESENT_VALUE
        )

    @property
    def room_presence_detection(self) -> Any:
        return self._get_value(ROOM_PRESENCE_DETECTION, ReadValue.PRESENT_VALUE)

    @property
    def room_presence_result(self) -> Any:
        return self._get_value(ROOM_PRESENCE_RESULT, ReadValue.PRESENT_VALUE)

    @property
    def enable_heating_control(self) -> Any:
        return self._get_value(ENABLE_HEATING_CONTROL, ReadValue.PRESENT_VALUE)

    @property
    def enable_heating_control_priorities(self) -> list[Any]:
        return self._get_value(ENABLE_HEATING_CONTROL, ReadValue.PRIORITY_ARRAY)

    async def set_enable_heating_control(self, value: Any | None) -> None:
        await self._set_value(ENABLE_HEATING_CONTROL, value)

    @property
    def warm_up_request(self) -> Any:
        return self._get_value(WARM_UP_REQUEST, ReadValue.PRESENT_VALUE)

    @property
    def room_window_state(self) -> Any:
        return self._get_value(ROOM_WINDOW_STATE, ReadValue.PRESENT_VALUE)

    @property
    def window_contact_result(self) -> Any:
        return self._get_value(WINDOW_CONTACT_RESULT, ReadValue.PRESENT_VALUE)

    @property
    def floor_heating_available(self) -> Any:
        return self._get_value(FLOOR_HEATING_AVAILABLE, ReadValue.PRESENT_VALUE)

    @property
    def enable_kick(self) -> Any:
        return self._get_value(ENABLE_KICK, ReadValue.PRESENT_VALUE)

    @property
    def geofencing_trigger(self) -> Any:
        return self._get_value(GEOFENCING_TRIGGER, ReadValue.PRESENT_VALUE)

    @property
    def geofencing_trigger_priorities(self) -> list[Any]:
        return self._get_value(GEOFENCING_TRIGGER, ReadValue.PRIORITY_ARRAY)

    async def set_geofencing_trigger(self, value: Any | None) -> None:
        await self._set_value(GEOFENCING_TRIGGER, value)

    @property
    def io_bus_management(self) -> Any:
        return self._get_value(IO_BUS_MANAGEMENT, ReadValue.PRESENT_VALUE)

    @property
    def onboard_module_builtin_5sen_1(self) -> Any:
        return self._get_value(ONBOARD_MODULE_BUILTIN_5SEN_1, ReadValue.PRESENT_VALUE)

    @property
    def onboard_module_2ui_1(self) -> Any:
        return self._get_value(ONBOARD_MODULE_2UI_1, ReadValue.PRESENT_VALUE)

    @property
    def off_protection_configuration(self) -> Any:
        return self._get_value(OFF_PROTECTION_CONFIGURATION, ReadValue.PRESENT_VALUE)

    @property
    def central_operating_mode_command(self) -> Any:
        return self._get_value(CENTRAL_OPERATING_MODE_COMMAND, ReadValue.PRESENT_VALUE)

    @property
    def central_operating_mode_command_priorities(self) -> list[Any]:
        return self._get_value(CENTRAL_OPERATING_MODE_COMMAND, ReadValue.PRIORITY_ARRAY)

    async def set_central_operating_mode_command(self, value: Any | None) -> None:
        await self._set_value(CENTRAL_OPERATING_MODE_COMMAND, value)

    @property
    def ossc_state(self) -> Any:
        return self._get_value(OSSC_STATE, ReadValue.PRESENT_VALUE)

    @property
    def room_operating_mode(self) -> Any:
        return self._get_value(ROOM_OPERATING_MODE, ReadValue.PRESENT_VALUE)

    @property
    def room_operating_mode_priorities(self) -> list[Any]:
        return self._get_value(ROOM_OPERATING_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_room_operating_mode(self, value: Any | None) -> None:
        await self._set_value(ROOM_OPERATING_MODE, value)

    @property
    def occupancy_mode(self) -> Any:
        return self._get_value(OCCUPANCY_MODE, ReadValue.PRESENT_VALUE)

    @property
    def occupancy_mode_priorities(self) -> list[Any]:
        return self._get_value(OCCUPANCY_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_occupancy_mode(self, value: Any | None) -> None:
        await self._set_value(OCCUPANCY_MODE, value)

    @property
    def room_energy_efficiency_indication(self) -> Any:
        return self._get_value(
            ROOM_ENERGY_EFFICIENCY_INDICATION, ReadValue.PRESENT_VALUE
        )

    @property
    def room_energy_efficiency_indication_priorities(self) -> list[Any]:
        return self._get_value(
            ROOM_ENERGY_EFFICIENCY_INDICATION, ReadValue.PRIORITY_ARRAY
        )

    async def set_room_energy_efficiency_indication(self, value: Any | None) -> None:
        await self._set_value(ROOM_ENERGY_EFFICIENCY_INDICATION, value)

    @property
    def hvac_energy_efficiency_indication(self) -> Any:
        return self._get_value(
            HVAC_ENERGY_EFFICIENCY_INDICATION, ReadValue.PRESENT_VALUE
        )

    @property
    def heating_cooling_state(self) -> Any:
        return self._get_value(HEATING_COOLING_STATE, ReadValue.PRESENT_VALUE)

    @property
    def hvac_presence_mode(self) -> Any:
        return self._get_value(HVAC_PRESENCE_MODE, ReadValue.PRESENT_VALUE)

    @property
    def hvac_presence_mode_priorities(self) -> list[Any]:
        return self._get_value(HVAC_PRESENCE_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_hvac_presence_mode(self, value: Any | None) -> None:
        await self._set_value(HVAC_PRESENCE_MODE, value)

    @property
    def plant_operating_mode(self) -> Any:
        return self._get_value(PLANT_OPERATING_MODE, ReadValue.PRESENT_VALUE)

    @property
    def plant_operating_mode_priorities(self) -> list[Any]:
        return self._get_value(PLANT_OPERATING_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_plant_operating_mode(self, value: Any | None) -> None:
        await self._set_value(PLANT_OPERATING_MODE, value)

    @property
    def next_room_operating_mode(self) -> Any:
        return self._get_value(NEXT_ROOM_OPERATING_MODE, ReadValue.PRESENT_VALUE)

    @property
    def next_room_operating_mode_priorities(self) -> list[Any]:
        return self._get_value(NEXT_ROOM_OPERATING_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_next_room_operating_mode(self, value: Any | None) -> None:
        await self._set_value(NEXT_ROOM_OPERATING_MODE, value)

    @property
    def present_operating_mode_reason(self) -> Any:
        return self._get_value(PRESENT_OPERATING_MODE_REASON, ReadValue.PRESENT_VALUE)

    @property
    def present_operating_mode_reason_priorities(self) -> list[Any]:
        return self._get_value(PRESENT_OPERATING_MODE_REASON, ReadValue.PRIORITY_ARRAY)

    async def set_present_operating_mode_reason(self, value: Any | None) -> None:
        await self._set_value(PRESENT_OPERATING_MODE_REASON, value)

    @property
    def floor_heating_device_mode(self) -> Any:
        return self._get_value(FLOOR_HEATING_DEVICE_MODE, ReadValue.PRESENT_VALUE)

    @property
    def floor_heating_device_mode_priorities(self) -> list[Any]:
        return self._get_value(FLOOR_HEATING_DEVICE_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_floor_heating_device_mode(self, value: Any | None) -> None:
        await self._set_value(FLOOR_HEATING_DEVICE_MODE, value)

    @property
    def floor_heating_hot_water_demand(self) -> Any:
        return self._get_value(FLOOR_HEATING_HOT_WATER_DEMAND, ReadValue.PRESENT_VALUE)

    @property
    def present_heating_controller_setting(self) -> Any:
        return self._get_value(
            PRESENT_HEATING_CONTROLLER_SETTING, ReadValue.PRESENT_VALUE
        )

    @property
    def heating_device_type(self) -> Any:
        return self._get_value(HEATING_DEVICE_TYPE, ReadValue.PRESENT_VALUE)

    @property
    def present_plant_operating_mode(self) -> Any:
        return self._get_value(PRESENT_PLANT_OPERATING_MODE, ReadValue.PRESENT_VALUE)

    @property
    def present_plant_operating_mode_priorities(self) -> list[Any]:
        return self._get_value(PRESENT_PLANT_OPERATING_MODE, ReadValue.PRIORITY_ARRAY)

    async def set_present_plant_operating_mode(self, value: Any | None) -> None:
        await self._set_value(PRESENT_PLANT_OPERATING_MODE, value)

    @property
    def heating_cooling_demand(self) -> Any:
        return self._get_value(HEATING_COOLING_DEMAND, ReadValue.PRESENT_VALUE)

    @property
    def heating_control_loop(self) -> Any:
        return self._get_value(HEATING_CONTROL_LOOP, ReadValue.PRESENT_VALUE)

    @property
    def optimum_start_control_setting(self) -> Any:
        return self._get_value(OPTIMUM_START_CONTROL_SETTING, ReadValue.PRESENT_VALUE)

    @property
    def room_air_quality_indication(self) -> Any:
        return self._get_value(ROOM_AIR_QUALITY_INDICATION, ReadValue.PRESENT_VALUE)

    async def set_floor_pump_position(self, value: Any | None) -> None:
        await self._set_value(PUMP_POSITION, value)
