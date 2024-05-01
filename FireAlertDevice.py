from SensorComponent import *


class FireAlertDevice:
    def __init__(self, device_id=None,
                 co_sensor=None,
                 fire_sensor=None,
                 heat_sensor=None,
                 smoke_sensor=None,
                 button_component=None,
                 light_component=None):
        self.device_id = device_id
        self.co_sensor = co_sensor        # 1 component
        self.fire_sensor = fire_sensor    # 1 component
        self.heat_sensor = heat_sensor    # 1 component
        self.smoke_sensor = smoke_sensor        # 1 component
        self.button_component = button_component              # 1 component
        self.light_component = light_component                # 1 component
        self.status = 'safe'    # Todo: 'safe'/'dangerous-0'/'dangerous-2'/'dangerous-3'

    # Get attr ###############################################
    def get_co_sensor_list(self):
        return self.co_sensor

    def get_fire_sensor_list(self):
        return self.fire_sensor

    def get_heat_sensor_list(self):
        return self.heat_sensor

    def get_smoke_sensor_list(self):
        return self.smoke_sensor

    def get_button_list(self):
        return self.button_component

    def get_light_list(self):
        return self.light_component

    def get_prev_status(self):
        return self.status

    def get_cur_status(self):
        self.update_status()
        return self.status
    ##########################################################

    # Update data ############################################
    def update_status(self):
        co_sensor_value = self.co_sensor.get_new_processed_data()
        fire_sensor_value = self.fire_sensor.get_new_processed_data()
        heat_sensor_value = self.heat_sensor.get_new_processed_data()
        smoke_sensor_value = self.smoke_sensor.get_new_processed_data()
        ######################################################
        # Todo: processing data
        #       danger detection
        processed_data = co_sensor_value + fire_sensor_value + heat_sensor_value + smoke_sensor_value
        if processed_data > 128:
            self.status = 'dangerous-2'
        elif processed_data > 64:
            self.status = 'dangerous-1'
        elif processed_data > 32:
            self.status = 'dangerous-0'
        else:
            self.status = 'safe'
        ####################################################
        return self.status
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
    ##########################################################


# Testing segment
if __name__ == '__main__':
    co_sensor_list = [None, None]
    co_sensor_0 = SensorComponent(feed_id='3', sensor_id=0, component_id=0, processed_data_threshold=-1)
    co_sensor_1 = SensorComponent(feed_id='2', sensor_id=0, component_id=1, processed_data_threshold=-1)
    co_sensor_list[0] = co_sensor_0
    co_sensor_list[1] = co_sensor_1

    temp_device = FireAlertDevice(device_id=0, co_sensor=co_sensor_list[0])
    temp_device.put_data_co_sensor(2, 30)
    temp_device.put_data_co_sensor(1, 10)
    temp_device.put_data_co_sensor(0, 10)

    print(temp_device.co_sensor.get_new_processed_data())