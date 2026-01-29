import asyncio
import sys

from siemens_bacnet_connector import SiemensBACnet


async def main():
    if len(sys.argv) < 2:
        print(f"usage ./{sys.argv[0]} <siemens-thermostat-ip-address>")
        exit()

    device_address = sys.argv[1]

    # create a SiemensBACnet device instance with the IP address and Device ID
    device = SiemensBACnet(device_address, 4194303)

    await device.update()

    # check device name and s/n
    print(f"Device Name: {device.device_name}")
    print(f"Serial Number: {device.serial_number}")
    print(
        f"Built-in room air temperature sensor: {device.built_in_room_air_temperature_sensor}"
    )
    print(
        f"Built-in room air relative humidity sensor: {device.built_in_room_air_relative_humidity_sensor}"
    )
    print(f"Automation station diagnostics: {device.automation_station_diagnostics}")
    print(f"I/O bus diagnostics: {device.io_bus_diagnostics}")
    print(f"Room temperature result: {device.room_temperature_result}")
    print(f"Present heating setpoint: {device.heating_setpoint}")
    print(device.heating_setpoint_priorities)
    print(
        f"Present heating setpoint for comfort: {device.present_heating_setpoint_comfort}"
    )
    print(
        f"Present heating setpoint for economy: {device.present_heating_setpoint_economy}"
    )
    print(
        f"Present heating setpoint for unoccupied: {device.present_heating_setpoint_unoccupied}"
    )
    print(
        f"Present heating setpoint for protection: {device.present_heating_setpoint_protection}"
    )
    print(f"Heating setpoint for comfort: {device.heating_setpoint_comfort}")
    print(device.heating_setpoint_comfort_priorities)
    print(f"Heating setpoint for economy: {device.heating_setpoint_economy}")
    print(f"Heating setpoint for unoccupied: {device.heating_setpoint_unoccupied}")
    print(f"Heating setpoint for protection: {device.heating_setpoint_protection}")
    print(f"Room temperature setpoint: {device.room_temperature_setpoint}")
    print(device.room_temperature_setpoint_priorities)
    print(f"Room temperature setpoint shift: {device.room_temperature_setpoint_shift}")
    print(device.room_temperature_setpoint_shift_priorities)
    print(f"Relative humidity for room: {device.room_relative_humidity}")
    print(f"Room temperature: {device.room_temperature}")
    print(f"Floor heating, heating request: {device.floor_heating_request}")
    print(
        f"Floor heating pump position value: {device.floor_heating_pump_position_value}"
    )
    print(device.floor_heating_pump_position_value_priorities)
    print(f"Effective room temperature: {device.effective_room_temperature}")
    print(
        f"Effective outside air temperature: {device.effective_outside_air_temperature}"
    )
    print(f"Max. heating setpoint: {device.max_heating_setpoint}")
    print(f"Warm-up gradient: {device.warm_up_gradient}")
    print(
        f"Built-in temp. sensor adj.: {device.built_in_temperature_sensor_adjustment}"
    )
    print(f"Room air quality: {device.room_air_quality}")
    print(f"Result of room air quality: {device.room_air_quality_result}")
    print(
        "Result of relative air humidity for room: "
        f"{device.room_relative_humidity_result}"
    )
    print(f"Application number: {device.application_number}")
    print(f"Built-in touch detector: {device.built_in_touch_detector}")
    print(f"Temporary comfort button: {device.temporary_comfort_button}")
    print(device.temporary_comfort_button_priorities)
    print(f"Comfort button: {device.comfort_button}")
    print(device.comfort_button_priorities)
    print(
        "Reset of room energy efficiency indic.: "
        f"{device.reset_room_energy_efficiency_indication}"
    )
    print(f"Room presence detection: {device.room_presence_detection}")
    print(f"Result of presence detector: {device.room_presence_result}")
    print(f"Enable heating control: {device.enable_heating_control}")
    print(device.enable_heating_control_priorities)
    print(f"Warm-up request: {device.warm_up_request}")
    print(f"Room window state: {device.room_window_state}")
    print(f"Result of window contact: {device.window_contact_result}")
    print(f"Floor heating available for heating: {device.floor_heating_available}")
    print(f"Enable kick: {device.enable_kick}")
    print(f"Geofencing trigger: {device.geofencing_trigger}")
    print(device.geofencing_trigger_priorities)
    print(f"I/O bus management: {device.io_bus_management}")
    print(f"On-board module BltIn5Sen module_1: {device.onboard_module_builtin_5sen_1}")
    print(f"On-board 2UI module_1: {device.onboard_module_2ui_1}")
    print(f"Off/protection configuration: {device.off_protection_configuration}")
    print(
        f"Central operating mode command value: {device.central_operating_mode_command}"
    )
    print(device.central_operating_mode_command_priorities)
    print(f"OSSC state (optimum start stop control): {device.ossc_state}")
    print(f"Room operating mode: {device.room_operating_mode}")
    print(device.room_operating_mode_priorities)
    print(f"Occupancy mode: {device.occupancy_mode}")
    print(device.occupancy_mode_priorities)
    print(
        f"Energy efficiency indication room: {device.room_energy_efficiency_indication}"
    )
    print(device.room_energy_efficiency_indication_priorities)
    print(
        "Room energy efficiency indication HVAC: "
        f"{device.hvac_energy_efficiency_indication}"
    )
    print(f"Heating/cooling state: {device.heating_cooling_state}")
    print(f"HVAC presence mode: {device.hvac_presence_mode}")
    print(device.hvac_presence_mode_priorities)
    print(f"Plant operating mode: {device.plant_operating_mode}")
    print(device.plant_operating_mode_priorities)
    print(f"Next room operating mode: {device.next_room_operating_mode}")
    print(device.next_room_operating_mode_priorities)
    print(f"Present operating mode and reason: {device.present_operating_mode_reason}")
    print(device.present_operating_mode_reason_priorities)
    print(f"Floor heating device mode: {device.floor_heating_device_mode}")
    print(device.floor_heating_device_mode_priorities)
    print(f"Floor heating hot water demand: {device.floor_heating_hot_water_demand}")
    print(
        "Present heating controller setting: "
        f"{device.present_heating_controller_setting}"
    )
    print(f"Heating device type: {device.heating_device_type}")
    print(f"Present plant operating mode: {device.present_plant_operating_mode}")
    print(device.present_plant_operating_mode_priorities)
    print(f"Heating/cooling demand: {device.heating_cooling_demand}")
    print(f"Heating control loop: {device.heating_control_loop}")
    print(f"Optimum start control setting: {device.optimum_start_control_setting}")
    print(f"Room air quality indication: {device.room_air_quality_indication}")
    print(f"Floor heating pump position: {device.floor_pump_position}")
    print(device.floor_pump_position_priorities)


if __name__ == "__main__":
    asyncio.run(main())
