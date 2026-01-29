"""Siemens Thermostat RDS110.R config."""

from .bacnet import DeviceProperty, ObjectType, ReadValue

TEMPERATURE_SENSOR = DeviceProperty(ObjectType.ANALOG_INPUT, 0)
PUMP_POSITION = DeviceProperty(
    ObjectType.ANALOG_OUTPUT,
    4,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
PRESENT_HEATING_SETPOINT = DeviceProperty(
    ObjectType.ANALOG_VALUE,
    122,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
BUILT_IN_ROOM_AIR_RELATIVE_HUMIDITY_SENSOR = DeviceProperty(ObjectType.ANALOG_INPUT, 1)
AUTOMATION_STATION_DIAGNOSTICS = DeviceProperty(ObjectType.ANALOG_VALUE, 0)
IO_BUS_DIAGNOSTICS = DeviceProperty(ObjectType.ANALOG_VALUE, 1)
ROOM_TEMPERATURE_RESULT = DeviceProperty(ObjectType.ANALOG_VALUE, 111)
PRESENT_HEATING_SETPOINT_COMFORT = DeviceProperty(ObjectType.ANALOG_VALUE, 123)
PRESENT_HEATING_SETPOINT_ECONOMY = DeviceProperty(ObjectType.ANALOG_VALUE, 124)
PRESENT_HEATING_SETPOINT_UNOCCUPIED = DeviceProperty(ObjectType.ANALOG_VALUE, 125)
PRESENT_HEATING_SETPOINT_PROTECTION = DeviceProperty(ObjectType.ANALOG_VALUE, 126)
HEATING_SETPOINT_COMFORT = DeviceProperty(
    ObjectType.ANALOG_VALUE,
    127,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
HEATING_SETPOINT_ECONOMY = DeviceProperty(ObjectType.ANALOG_VALUE, 128)
HEATING_SETPOINT_UNOCCUPIED = DeviceProperty(ObjectType.ANALOG_VALUE, 129)
HEATING_SETPOINT_PROTECTION = DeviceProperty(ObjectType.ANALOG_VALUE, 130)
ROOM_TEMPERATURE_SETPOINT = DeviceProperty(
    ObjectType.ANALOG_VALUE,
    131,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
ROOM_TEMPERATURE_SETPOINT_SHIFT = DeviceProperty(
    ObjectType.ANALOG_VALUE,
    132,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
ROOM_RELATIVE_HUMIDITY = DeviceProperty(ObjectType.ANALOG_VALUE, 133)
ROOM_TEMPERATURE = DeviceProperty(ObjectType.ANALOG_VALUE, 134)
FLOOR_HEATING_REQUEST = DeviceProperty(ObjectType.ANALOG_VALUE, 150)
FLOOR_HEATING_PUMP_POSITION_VALUE = DeviceProperty(
    ObjectType.ANALOG_VALUE,
    151,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
EFFECTIVE_ROOM_TEMPERATURE = DeviceProperty(ObjectType.ANALOG_VALUE, 162)
EFFECTIVE_OUTSIDE_AIR_TEMPERATURE = DeviceProperty(ObjectType.ANALOG_VALUE, 163)
MAX_HEATING_SETPOINT = DeviceProperty(ObjectType.ANALOG_VALUE, 178)
WARM_UP_GRADIENT = DeviceProperty(ObjectType.ANALOG_VALUE, 180)
BUILT_IN_TEMPERATURE_SENSOR_ADJUSTMENT = DeviceProperty(ObjectType.ANALOG_VALUE, 181)
ROOM_AIR_QUALITY = DeviceProperty(ObjectType.ANALOG_VALUE, 205)
ROOM_AIR_QUALITY_RESULT = DeviceProperty(ObjectType.ANALOG_VALUE, 206)
ROOM_RELATIVE_HUMIDITY_RESULT = DeviceProperty(ObjectType.ANALOG_VALUE, 207)
APPLICATION_NUMBER = DeviceProperty(ObjectType.ANALOG_VALUE, 208)
BUILT_IN_TOUCH_DETECTOR = DeviceProperty(ObjectType.BINARY_INPUT, 2)
TEMPORARY_COMFORT_BUTTON = DeviceProperty(
    ObjectType.BINARY_VALUE,
    56,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
COMFORT_BUTTON = DeviceProperty(
    ObjectType.BINARY_VALUE,
    57,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
RESET_ROOM_ENERGY_EFFICIENCY_INDICATION = DeviceProperty(ObjectType.BINARY_VALUE, 58)
ROOM_PRESENCE_DETECTION = DeviceProperty(ObjectType.BINARY_VALUE, 59)
ROOM_PRESENCE_RESULT = DeviceProperty(ObjectType.BINARY_VALUE, 60)
ENABLE_HEATING_CONTROL = DeviceProperty(
    ObjectType.BINARY_VALUE,
    63,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
WARM_UP_REQUEST = DeviceProperty(ObjectType.BINARY_VALUE, 64)
ROOM_WINDOW_STATE = DeviceProperty(ObjectType.BINARY_VALUE, 65)
WINDOW_CONTACT_RESULT = DeviceProperty(ObjectType.BINARY_VALUE, 66)
FLOOR_HEATING_AVAILABLE = DeviceProperty(ObjectType.BINARY_VALUE, 73)
ENABLE_KICK = DeviceProperty(ObjectType.BINARY_VALUE, 85)
GEOFENCING_TRIGGER = DeviceProperty(
    ObjectType.BINARY_VALUE,
    90,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
IO_BUS_MANAGEMENT = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 0)
ONBOARD_MODULE_BUILTIN_5SEN_1 = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 1)
ONBOARD_MODULE_2UI_1 = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 2)
OFF_PROTECTION_CONFIGURATION = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 76)
CENTRAL_OPERATING_MODE_COMMAND = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    77,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
OSSC_STATE = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 78)
ROOM_OPERATING_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    80,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
OCCUPANCY_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    81,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
ROOM_ENERGY_EFFICIENCY_INDICATION = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    82,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
HVAC_ENERGY_EFFICIENCY_INDICATION = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 84)
HEATING_COOLING_STATE = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 86)
HVAC_PRESENCE_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    87,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
PLANT_OPERATING_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    88,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
NEXT_ROOM_OPERATING_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    89,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
PRESENT_OPERATING_MODE_REASON = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    90,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
FLOOR_HEATING_DEVICE_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    98,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
FLOOR_HEATING_HOT_WATER_DEMAND = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 99)
PRESENT_HEATING_CONTROLLER_SETTING = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 109)
HEATING_DEVICE_TYPE = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 110)
PRESENT_PLANT_OPERATING_MODE = DeviceProperty(
    ObjectType.MULTI_STATE_VALUE,
    111,
    read_values=[ReadValue.PRESENT_VALUE, ReadValue.PRIORITY_ARRAY],
)
HEATING_COOLING_DEMAND = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 112)
HEATING_CONTROL_LOOP = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 113)
OPTIMUM_START_CONTROL_SETTING = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 114)
ROOM_AIR_QUALITY_INDICATION = DeviceProperty(ObjectType.MULTI_STATE_VALUE, 116)

# List of all DeviceProperties defined in this file
DEVICE_PROPERTIES = [
    item for _, item in globals().items() if isinstance(item, DeviceProperty)
]
