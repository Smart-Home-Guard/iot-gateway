from Components.SensorComponent import *
from Components.ButtonComponent import *
from Components.OutputComponent import *
from Components.BatteryComponent import *


class FireAlertDevice:
    def __init__(self, device_id=None,
                 co_sensor=SensorComponent(),
                 fire_sensor=SensorComponent(),
                 heat_sensor=SensorComponent(),
                 smoke_sensor=SensorComponent(),
                 lpg_sensor=SensorComponent(),
                 light_component=OutputComponent(),
                 buzzer_component=OutputComponent(),
                 battery_component=BatteryComponent()):
        self.device_id = device_id
        self.co_sensor = co_sensor                  # 1 component
        self.fire_sensor = fire_sensor              # 1 component
        self.heat_sensor = heat_sensor              # 1 component
        self.smoke_sensor = smoke_sensor            # 1 component
        self.lpg_sensor = lpg_sensor                # 1 component
        self.light_component = light_component      # 1 component
        self.buzzer_component = buzzer_component    # 1 component
        self.battery_component = battery_component
        self.mute_alert_light = 0
        self.mute_alert_buzzer = 0
        self.status = 'safe'        # 'safe' / 'dangerous'

    # Get attr ###############################################
    def get_device_id(self):
        return self.device_id

    def get_co_sensor_list(self):
        return self.co_sensor

    def get_fire_sensor_list(self):
        return self.fire_sensor

    def get_heat_sensor_list(self):
        return self.heat_sensor

    def get_smoke_sensor_list(self):
        return self.smoke_sensor

    def get_lpg_sensor_list(self):
        return self.smoke_sensor

    def get_light_list(self):
        return self.light_component

    def get_buzzer_list(self):
        return self.buzzer_component
    def get_status(self):
        return self.status

    def get_mute_alert_light_state(self):
        return self.mute_alert_light

    def get_mute_alert_buzzer_state(self):
        return self.mute_alert_buzzer

    def get_component_status(self):
        component_status_dict = {
            'fire': self.fire_sensor.sensor_status,
            'co': self.co_sensor.sensor_status,
            'smoke': self.smoke_sensor.sensor_status,
            'lpg': self.lpg_sensor.sensor_status,
            'light': self.light_component.get_state(),
            'buzzer': self.buzzer_component.get_state()
        }
        return component_status_dict

    def get_metrics(self):
        if not self.co_sensor == None:
            co_sensor_dict = self.co_sensor.get_metrics()
        else:
            co_sensor_dict = None
        if not self.fire_sensor == None:
            fire_sensor_dict = self.fire_sensor.get_metrics()
        else:
            fire_sensor_dict = None
        if not self.heat_sensor == None:
            heat_sensor_dict = self.heat_sensor.get_metrics()
        else:
            heat_sensor_dict = None
        if not self.smoke_sensor == None:
            smoke_sensor_dict = self.smoke_sensor.get_metrics()
        else:
            smoke_sensor_dict = None

        if not self.lpg_sensor == None:
            lpg_sensor_dict = self.lpg_sensor.get_metrics()
        else:
            lpg_sensor_dict = None
        # fire_sensor_dict = self.fire_sensor.get_metrics()
        # heat_sensor_dict = self.heat_sensor.get_metrics()
        # smoke_sensor_dict = self.smoke_sensor.get_metrics()
        # lpg_sensor_dict = self.lpg_sensor.get_metrics()
        light_component_dict = self.light_component.get_metrics()
        buzzer_component_dict = self.buzzer_component.get_metrics()
        fire_alert_device_dict = {
            'co': [co_sensor_dict],
            'fire': [fire_sensor_dict],
            'heat': [heat_sensor_dict],
            'smoke': [smoke_sensor_dict],
            'lpg': [lpg_sensor_dict],
            'fire-light': [light_component_dict],
            'fire-buzzer': [buzzer_component_dict]
        }
        return fire_alert_device_dict

    def get_info(self):
        if not self.co_sensor == None:
            co_sensor_dict = self.co_sensor.get_info()
        else:
            co_sensor_dict = None
        if not self.fire_sensor == None:
            fire_sensor_dict = self.fire_sensor.get_info()
        else:
            fire_sensor_dict = None
        if not self.heat_sensor == None:
            heat_sensor_dict = self.heat_sensor.get_info()
        else:
            heat_sensor_dict = None
        if not self.smoke_sensor == None:
            smoke_sensor_dict = self.smoke_sensor.get_info()
        else:
            smoke_sensor_dict = None

        if not self.lpg_sensor == None:
            lpg_sensor_dict = self.lpg_sensor.get_info()
        else:
            lpg_sensor_dict = None
        light_component_dict = self.light_component.get_info()
        buzzer_component_dict = self.buzzer_component.get_info()
        fire_alert_device_info_array = [co_sensor_dict, fire_sensor_dict, heat_sensor_dict, smoke_sensor_dict,
                                        lpg_sensor_dict, light_component_dict,
                                        buzzer_component_dict]
        device_info_list = []
        for device_info in fire_alert_device_info_array:
            if not device_info == {}:
                device_info_list.append(device_info)
        return device_info_list

    def get_battery_status(self):
        return self.battery_component.get_metrics()
    ##########################################################

    # Update data ############################################
    def inspect_new_status(self):
        new_co_sensor_status = self.co_sensor.inspect_new_status()
        new_fire_sensor_status = self.fire_sensor.inspect_new_status()
        new_heat_sensor_status = self.heat_sensor.inspect_new_status()
        new_smoke_sensor_status = self.smoke_sensor.inspect_new_status()
        new_lpg_sensor_status = self.lpg_sensor.inspect_new_status()
        ######################################################
        if (new_co_sensor_status == 'safe' and
            new_fire_sensor_status == 'safe' and
            new_heat_sensor_status == 'safe' and
            new_smoke_sensor_status == 'safe' and
            new_lpg_sensor_status == 'safe'):
            return 'safe'
        else:
            return 'dangerous'

    def update_new_data(self):
        self.co_sensor.update_new_data()
        self.fire_sensor.update_new_data()
        self.heat_sensor.update_new_data()
        self.smoke_sensor.update_new_data()
        self.lpg_sensor.update_new_data()
        ######################################################
        if self.is_all_sensors_safe():
            self.status = 'safe'
        else:
            self.status = 'dangerous'
        ####################################################
    ##########################################################

    # Put data ###############################################
    def put_data_co_sensor(self, component_id, value):
        self.co_sensor.put_raw_data(value)

    def put_data_fire_sensor(self, component_id, value):
        self.fire_sensor.put_raw_data(value)

    def put_data_heat_sensor(self, component_id, value):
        self.heat_sensor.put_raw_data(value)

    def put_data_smoke_sensor(self, component_id, value):
        self.smoke_sensor.put_raw_data(value)

    def put_data_lpg_sensor(self, component_id, value):
        self.lpg_sensor.put_raw_data(value)
    ##########################################################

    # Set Output component ###################################
    def set_state_light_component(self, state_in):
        self.light_component.set_state(state_in)

    def set_state_buzzer_component(self, state_in):
        self.buzzer_component.set_state(state_in)

    def toggle_state_light_component(self):
        self.light_component.toggle_state()

    def toggle_state_buzzer_component(self):
        self.buzzer_component.toggle_state()

    def set_mute_alert_light(self, option):
        self.mute_alert_light = option
        self.light_component.set_mute_alert(option=option)

    def set_mute_alert_buzzer(self, option):
        self.mute_alert_buzzer = option
        self.buzzer_component.set_mute_alert(option=option)
    ##########################################################

    # Misc ###############################################
    def is_all_sensors_safe(self):
        return (self.co_sensor.is_safe() == 'safe' and
                self.fire_sensor.is_safe() == 'safe' and
                self.heat_sensor.is_safe() == 'safe' and
                self.smoke_sensor.is_safe() == 'safe' and
                self.lpg_sensor.is_safe() == 'safe')
    ##########################################################


# Testing segment
if __name__ == '__main__':
    co_sensor_list = [None, None]
    co_sensor_0 = SensorComponent(feed_id='3', sensor_id=0, component_id=0, processed_data_threshold=60, sensor_enable=True)
    fire_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=60, sensor_enable=True)
    smoke_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=60, sensor_enable=True)
    heat_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=60, sensor_enable=True)
    lpg_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=49, sensor_enable=True)
    co_sensor_list[0] = co_sensor_0

    temp_device = FireAlertDevice(device_id=0, co_sensor=co_sensor_list[0], fire_sensor=fire_sensor_0,
                                  smoke_sensor=smoke_sensor_0, heat_sensor=heat_sensor_0, lpg_sensor=lpg_sensor_0)
    temp_device.put_data_co_sensor(2, 30)
    temp_device.put_data_co_sensor(1, 10)
    temp_device.put_data_co_sensor(0, 40)
    temp_device.put_data_co_sensor(0, 50)
    temp_device.put_data_fire_sensor(0, 50)
    temp_device.put_data_smoke_sensor(0, 50)
    temp_device.put_data_heat_sensor(0, 50)
    temp_device.put_data_lpg_sensor(0, 50)

    print(f'Inspect status before updating: {temp_device.inspect_new_status()}')
    print(f'Get status before updating: {temp_device.get_status()}')
    temp_device.update_new_data()
    print(f'------------------Updating------------------')

    print(f'Get processed data of the CO sensor: {temp_device.co_sensor.get_processed_data()}')
    print(f'Get device metrics: {temp_device.get_metrics()}')