from BatteryComponent import *
import numpy as np


class SensorComponent:
    def __init__(self, feed_id='None', sensor_id=0, component_id=0, processed_data_threshold=0x7fffffff):
        self.feed_id = feed_id
        self.sensor_id = sensor_id
        self.component_id = component_id
        self.raw_data_buffer = []
        self.raw_data_updated = 0      # new data in the buffer
        self.processed_data = 0
        self.processed_data_threshold = processed_data_threshold
        self.battery = BatteryComponent()
        self.sensor_status = True       # En

    def set_threshold(self, new_threshold_value):
        self.processed_data_threshold = new_threshold_value

    def is_buffer_updated(self):
        return self.raw_data_updated > 0

    def is_safe(self):
        return self.processed_data < self.processed_data_threshold

    def put_raw_data(self, value):
        self.raw_data_buffer.append(value)
        self.raw_data_updated += 1

    def get_processed_data(self):
        return self.processed_data
    
    def update_new_data(self):
        if self.raw_data_updated == 0:
            # Return old data
            return self.processed_data
        # Get sub buffer of data buffer
        sub_buffer = self.raw_data_buffer[len(self.raw_data_buffer) - self.raw_data_updated:len(self.raw_data_buffer)]
        # Data processing (mean value)
        new_processed_data = np.mean(sub_buffer)
        # Clear buffer
        self.raw_data_buffer.clear()
        self.raw_data_updated = 0
        # Update buffer
        self.processed_data = new_processed_data

    def get_metrics(self):
        metrics_dict = {
            'id': self.sensor_id,
            'component': self.component_id,
            'value': self.get_processed_data(),
            'alert': self.is_safe()
        }
        return metrics_dict


# Testing segment
if __name__ == '__main__':
    co_sensor = SensorComponent(feed_id='co_feed', sensor_id=2, component_id=3)
    for i in range(0, 30):
        co_sensor.put_raw_data(i)
    print('--------------- Before updating--------------------')
    print(f'Raw data has just updated: {co_sensor.raw_data_updated}')
    print(f'Raw data buffer: {co_sensor.raw_data_buffer}')
    print(f'Processed data buffer: {co_sensor.get_processed_data()}')
    print('--------------- After updating--------------------')
    co_sensor.update_new_data()
    print(f'Raw data has just updated: {co_sensor.raw_data_updated}')
    print(f'Raw data buffer: {co_sensor.raw_data_buffer}')
    print(f'Processed data buffer: {co_sensor.get_processed_data()}')
    print(f'Is safe: {co_sensor.is_safe()}')
    print(f'Value threshold: {co_sensor.processed_data_threshold}')
    print(f'Metrics: {co_sensor.get_metrics()}')
    print('---------------------------------------------------')

    co_sensor.set_threshold(3)
    for i in range(3, 13):
        co_sensor.put_raw_data(i)

    print('--------------- Before updating--------------------')
    print(f'Raw data has just updated: {co_sensor.raw_data_updated}')
    print(f'Raw data buffer: {co_sensor.raw_data_buffer}')
    print(f'Processed data buffer: {co_sensor.get_processed_data()}')
    co_sensor.update_new_data()
    print('--------------- After updating--------------------')
    print(f'Raw data has just updated: {co_sensor.raw_data_updated}')
    print(f'Raw data buffer: {co_sensor.raw_data_buffer}')
    print(f'Processed data buffer: {co_sensor.get_processed_data()}')
    print(f'Is safe: {co_sensor.is_safe()}')
    print(f'Value threshold: {co_sensor.processed_data_threshold}')
    print(f'Metrics: {co_sensor.get_metrics()}')

    print('-------------------')
