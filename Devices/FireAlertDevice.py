from Components.SensorComponent import *
from Components.ButtonComponent import *
from Components.OutputComponent import *


class FireAlertDevice:
    def __init__(self, device_id=None,
                 co_sensor=SensorComponent(),
                 fire_sensor=SensorComponent(),
                 heat_sensor=SensorComponent(),
                 smoke_sensor=SensorComponent(),
                 lpg_sensor=SensorComponent(),
                 button_component=ButtonComponent(),
                 light_component=OutputComponent(),
                 buzzer_component=OutputComponent()):
        self.device_id = device_id
        self.co_sensor = co_sensor                  # 1 component
        self.fire_sensor = fire_sensor              # 1 component
        self.heat_sensor = heat_sensor              # 1 component
        self.smoke_sensor = smoke_sensor            # 1 component
        self.lpg_sensor = lpg_sensor                # 1 component
        self.button_component = button_component    # 1 component
        self.light_component = light_component      # 1 component
        self.buzzer_component = buzzer_component    # 1 component
        self.status = 'safe'    # Todo: 'safe'/'dangerous-0'/'dangerous-2'/'dangerous-3'

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

    def get_button_list(self):
        return self.button_component

    def get_light_list(self):
        return self.light_component

    def get_status(self):
        return self.status

    def get_metrics(self):
        co_sensor_dict = self.co_sensor.get_metrics()
        fire_sensor_dict = self.fire_sensor.get_metrics()
        heat_sensor_dict = self.heat_sensor.get_metrics()
        smoke_sensor_dict = self.smoke_sensor.get_metrics()
        lpg_sensor_dict = self.lpg_sensor.get_metrics()
        button_component_dict = self.button_component.get_metrics()
        light_component_dict = self.light_component.get_metrics()
        buzzer_component_dict = self.buzzer_component.get_metrics()
        fire_alert_device_dict = {
            'co': [co_sensor_dict],
            'fire': [fire_sensor_dict],
            'heat': [heat_sensor_dict],
            'smoke': [smoke_sensor_dict],
            'lpg': [lpg_sensor_dict],
            'fire-button': [button_component_dict],
            'fire-light': [light_component_dict],
            'fire-buzzer': [buzzer_component_dict]
        }
        return fire_alert_device_dict

    def get_info(self):
        co_sensor_dict = self.co_sensor.get_info()
        fire_sensor_dict = self.fire_sensor.get_info()
        heat_sensor_dict = self.heat_sensor.get_info()
        smoke_sensor_dict = self.smoke_sensor.get_info()
        lpg_sensor_dict = self.lpg_sensor.get_info()
        button_component_dict = self.button_component.get_info()
        light_component_dict = self.light_component.get_info()
        buzzer_component_dict = self.buzzer_component.get_info()
        fire_alert_device_info_array = [co_sensor_dict, fire_sensor_dict, heat_sensor_dict, smoke_sensor_dict,
                                        lpg_sensor_dict, button_component_dict, light_component_dict,
                                        buzzer_component_dict]
        return fire_alert_device_info_array
    ##########################################################

    # Update data ############################################
    def inspect_new_status(self):
        new_co_sensor_value = self.co_sensor.inspect_new_data()
        new_fire_sensor_value = self.fire_sensor.inspect_new_data()
        new_heat_sensor_value = self.heat_sensor.inspect_new_data()
        new_smoke_sensor_value = self.smoke_sensor.inspect_new_data()
        new_lpg_sensor_value = self.lpg_sensor.inspect_new_data()
        ######################################################
        # Todo: processing data
        #       danger detection
        try:
            processed_data = (new_co_sensor_value + new_fire_sensor_value + new_heat_sensor_value +
                              new_smoke_sensor_value + new_lpg_sensor_value)
        except TypeError:           # None value (One or more sensors do not have new data )
            return self.status      # Return old status
        if processed_data > 128:
            return 'dangerous-2'
        elif processed_data > 64:
            return 'dangerous-1'
        elif processed_data > 32:
            return 'dangerous-0'
        else:
            return 'safe'

    def update_new_data(self):
        self.co_sensor.update_new_data()
        self.fire_sensor.update_new_data()
        self.heat_sensor.update_new_data()
        self.smoke_sensor.update_new_data()
        self.lpg_sensor.update_new_data()
        co_sensor_value = self.co_sensor.get_processed_data()
        fire_sensor_value = self.fire_sensor.get_processed_data()
        heat_sensor_value = self.heat_sensor.get_processed_data()
        smoke_sensor_value = self.smoke_sensor.get_processed_data()
        lpg_sensor_value = self.lpg_sensor.get_processed_data()
        ######################################################
        # Todo: processing data
        #       danger detection
        processed_data = co_sensor_value + fire_sensor_value + heat_sensor_value + smoke_sensor_value + lpg_sensor_value
        if processed_data > 128:
            self.status = 'dangerous-2'
        elif processed_data > 64:
            self.status = 'dangerous-1'
        elif processed_data > 32:
            self.status = 'dangerous-0'
        else:
            self.status = 'safe'
        ####################################################
    ##########################################################

    # Put data ###############################################
    def put_data_co_sensor(self, component_id, value):
        if self.co_sensor.component_id == component_id:
            self.co_sensor.put_raw_data(value)
        else:
            print(f'Warning: The component does not exist (CO: {component_id})')

    def put_data_fire_sensor(self, component_id, value):
        if self.fire_sensor.component_id == component_id:
            self.fire_sensor.put_raw_data(value)
        else:
            print(f'Warning: The component does not exist (Fire: {component_id})')

    def put_data_heat_sensor(self, component_id, value):
        if self.heat_sensor.component_id == component_id:
            self.heat_sensor.put_raw_data(value)
        else:
            print(f'Warning: The component does not exist (Heat: {component_id})')

    def put_data_smoke_sensor(self, component_id, value):
        if self.smoke_sensor.component_id == component_id:
            self.smoke_sensor.put_raw_data(value)
        else:
            print(f'Warning: The component does not exist (Smoke: {component_id})')

    def put_data_lpg_sensor(self, component_id, value):
        if self.lpg_sensor.component_id == component_id:
            self.lpg_sensor.put_raw_data(value)
        else:
            print(f'Warning: The component does not exist (LPG: {component_id})')
    ##########################################################


# Testing segment
if __name__ == '__main__':
    co_sensor_list = [None, None]
    co_sensor_0 = SensorComponent(feed_id='3', sensor_id=0, component_id=0, processed_data_threshold=-1, sensor_status=True)
    fire_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=-1, sensor_status=True)
    smoke_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=-1, sensor_status=True)
    heat_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=-1, sensor_status=True)
    lpg_sensor_0 = SensorComponent(feed_id='2', sensor_id=0, component_id=0, processed_data_threshold=-1, sensor_status=True)
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