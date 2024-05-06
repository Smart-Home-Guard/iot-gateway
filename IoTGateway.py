import json
import queue
import sys
import threading

import serial
import serial.tools.list_ports
from Adafruit_IO import MQTTClient as AdafruitClient
import paho.mqtt.client as mqtt
from Mics.Constants import *
from Devices.FireAlertDevice import *
from Devices.AlertDevice import *
from Components.SensorComponent import *
from Components.ButtonComponent import *
from Components.OutputComponent import *
from Mics.Miscellaneous import *


class Gateway:
    # Mode configuration
    WITHOUT_SERIAL_CONNECTION = True

    def __init__(self, aio_username, aio_key):
        # MQTT Server
        self.mqtt_client_id = ''
        self.mqtt_client_token = ''
        self.mqtt_client = None
        # Adafruit Server
        self.aio_username = aio_username
        self.aio_key = aio_key
        # Device list
        self.device_list = {'fire-alert-devices': [], 'alert-devices': []}
        # Serial
        self.serial_obj = None
        self.serial_message_buffer = queue.Queue()

    # Set up connection #################################################################
    def load_client_info(self, mqtt_client_info_path, aio_user_info_path):
        with open(mqtt_client_info_path, "r") as file:
            mqtt_client_info_dict = json.load(file)
        self.mqtt_client_id = mqtt_client_info_dict["client_id"]
        self.mqtt_client_token = mqtt_client_info_dict["client_token"]
        with open(aio_user_info_path, "r") as file:
            aio_user_info_dict = json.load(file)
        self.aio_username = aio_user_info_dict["aio_username"]
        self.aio_key = aio_user_info_dict["aio_key"]

    def load_device_info(self, device_info_path):
        with open(device_info_path, "r") as file:
            device_info_dict = json.load(file)

        if 'fire-alert-devices' in device_info_dict:
            fire_alert_device_list = device_info_dict['fire-alert-devices']
            for idx in range(0, len(fire_alert_device_list)):
                device_id = None
                fire_alert_device = fire_alert_device_list[idx]
                # Get information
                co_sensor = None
                if len(fire_alert_device['co']) > 0:
                    co_sensor_info = fire_alert_device['co'][0]
                    device_id = co_sensor_info['sensor_id']
                    co_sensor = SensorComponent(feed_id=co_sensor_info['feed_id'],
                                                sensor_id=co_sensor_info['sensor_id'],
                                                component_id=co_sensor_info['component_id'],
                                                processed_data_threshold=co_sensor_info['processed_data_threshold'],
                                                sensor_status=True)
                fire_sensor = None
                if len(fire_alert_device['fire']) > 0:
                    fire_sensor_info = fire_alert_device['fire'][0]
                    device_id = fire_sensor_info['sensor_id']
                    fire_sensor = SensorComponent(feed_id=fire_sensor_info['feed_id'],
                                                  sensor_id=fire_sensor_info['sensor_id'],
                                                  component_id=fire_sensor_info['component_id'],
                                                  processed_data_threshold=fire_sensor_info['processed_data_threshold'],
                                                  sensor_status=True)
                heat_sensor = None
                if len(fire_alert_device['heat']) > 0:
                    heat_sensor_info = fire_alert_device['heat'][0]
                    device_id = heat_sensor_info['sensor_id']
                    heat_sensor = SensorComponent(feed_id=heat_sensor_info['feed_id'],
                                                  sensor_id=heat_sensor_info['sensor_id'],
                                                  component_id=heat_sensor_info['component_id'],
                                                  processed_data_threshold=heat_sensor_info['processed_data_threshold'],
                                                  sensor_status=True)
                smoke_sensor = None
                if len(fire_alert_device['smoke']) > 0:
                    smoke_sensor_info = fire_alert_device['smoke'][0]
                    device_id = smoke_sensor_info['sensor_id']
                    smoke_sensor = SensorComponent(feed_id=smoke_sensor_info['feed_id'],
                                                   sensor_id=smoke_sensor_info['sensor_id'],
                                                   component_id=smoke_sensor_info['component_id'],
                                                   processed_data_threshold=smoke_sensor_info['processed_data_threshold'],
                                                   sensor_status=True)
                lpg_sensor = None
                if len(fire_alert_device['lpg']) > 0:
                    lpg_sensor_info = fire_alert_device['lpg'][0]
                    device_id = lpg_sensor_info['sensor_id']
                    lpg_sensor = SensorComponent(feed_id=lpg_sensor_info['feed_id'],
                                                 sensor_id=lpg_sensor_info['sensor_id'],
                                                 component_id=lpg_sensor_info['component_id'],
                                                 processed_data_threshold=lpg_sensor_info['processed_data_threshold'],
                                                 sensor_status=True)
                button_component = None
                if len(fire_alert_device['button']) > 0:
                    button_component_info = fire_alert_device['button'][0]
                    device_id = button_component_info['device_id']
                    button_component = ButtonComponent(feed_id=button_component_info['feed_id'],
                                                       device_id=button_component_info['device_id'],
                                                       component_id=button_component_info['component_id'],
                                                       component_status=True)
                light_component = None
                if len(fire_alert_device['light']) > 0:
                    light_component_info = fire_alert_device['light'][0]
                    device_id = light_component_info['device_id']
                    light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'],
                                                      component_status=True)
                buzzer_component = None
                if len(fire_alert_device['buzzer']) > 0:
                    buzzer_component_info = fire_alert_device['buzzer'][0]
                    device_id = buzzer_component_info['device_id']
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'],
                                                       component_status=True)

                fire_alert_device = FireAlertDevice(device_id=device_id, co_sensor=co_sensor, fire_sensor=fire_sensor,
                                                    heat_sensor=heat_sensor, smoke_sensor=smoke_sensor,
                                                    lpg_sensor=lpg_sensor, button_component=button_component,
                                                    light_component=light_component, buzzer_component=buzzer_component)

                self.device_list['fire-alert-devices'].append(fire_alert_device)
        else:
            print(f'Warning: Missing Fire Alert device information')

        if 'alert-devices' in device_info_dict:
            alert_devices_list = device_info_dict['alert-devices']
            for idx in range(0, len(alert_devices_list)):
                alert_device = alert_devices_list[idx]
                device_id = None
                button_component = None
                if len(alert_device['button']) > 0:
                    button_component_info = alert_device['button'][0]
                    device_id = button_component_info['device_id']
                    button_component = ButtonComponent(feed_id=button_component_info['feed_id'],
                                                       device_id=button_component_info['device_id'],
                                                       component_id=button_component_info['component_id'],
                                                       component_status=True)
                light_component = None
                if len(alert_device['light']) > 0:
                    light_component_info = alert_device['light'][0]
                    device_id = light_component_info['device_id']
                    light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'],
                                                      component_status=True)
                buzzer_component = None
                if len(alert_device['buzzer']) > 0:
                    buzzer_component_info = alert_device['buzzer'][0]
                    device_id = buzzer_component_info['device_id']
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'],
                                                       component_status=True)

                alert_device = AlertDevice(device_id=device_id, button_component=button_component,
                                           light_component=light_component, buzzer_component=buzzer_component)

                self.device_list['alert-devices'].append(alert_device)

        else:
            print(f'Warning: Missing Alert device information')

    def init_serial(self):
        if not self.WITHOUT_SERIAL_CONNECTION:
            # Serial connection
            self.serial_obj = serial.Serial(port="COM17", baudrate=115200)  # COM17 - COM15
        return 'None'
    ######################################################################################

    # Get attr of the object ####################################################################
    def get_components_list(self):
        components_list = []
        for device in self.device_list['fire-alert-devices']:
            components_list = components_list + device.get_info()
        for device in self.device_list['alert-devices']:
            components_list = components_list + device.get_info()
        print(components_list)
        return components_list

    #############################################################################################

    # MQTT Server method ########################################################################
    def get_topic(self, channel_type):
        if channel_type == 'fire-alert':
            return self.mqtt_client_id + '/fire-alert-metrics'
        elif channel_type == 'devices-status':
            return self.mqtt_client_id + 'devices-status-metrics'
        return ''

    def publish_components_connection(self):
        components_list = self.get_components_list()
        # Publish to MQTT server
        message_topic = self.get_topic(channel_type='devices-status')
        message = {
            'kind': KENUM_CONNECT_DEVICE,
            'payload': {
                'token': self.mqtt_client_token,
                'data': components_list
            }
        }
        print(f'INFO: Publish all components to the MQTT server (message: {message})')
        try:
            self.mqtt_client.publish(topic=message_topic, payload=json.dump(message))
        except:
            print('ERROR: Can not publish the message to the MQTT Server')
    #############################################################################################

    # Serial thread #############################################################################
    def read_serial(self):
        if not self.WITHOUT_SERIAL_CONNECTION:
            bytes_to_read = self.serial_obj.in_waiting
        else:
            bytes_to_read = input('Your commands: ')

        if bytes_to_read > 0:
            global mess
            if not self.WITHOUT_SERIAL_CONNECTION:
                mess = mess + self.serial_obj.read(bytes_to_read).decode("UTF-8")
            else:
                mess = mess + bytes_to_read
            # print(mess + "\n")
            while ("#" in mess) and ("!" in mess):
                start = mess.find("!")
                end = mess.find("#")
                self.serial_message_buffer.put(mess[start:end + 1])
                # self.processing_data(mess[start:end + 1])
                if end == len(mess):
                    mess = ""
                else:
                    mess = mess[end + 1:]

    def handle_serial_message(self, serial_message):
        # Todo: processing data
        # Parser
        data = serial_message.replace("!", "")
        data = data.replace("#", "")
        split_data = data.split(":")
        node_funct_id = split_data[NODE_FUNCT_ID_IDX]
        node_device_id = split_data[NODE_DEVICE_ID_IDX]
        node_value = [None] * NODE_VALUE_6_IDX
        for i in range(len(split_data) - NODE_VALUE_1_IDX):  #
            node_value[i] = split_data[NODE_VALUE_1_IDX + i]

        # Handling
        if node_device_id == CO_DETECTION_ENUM:
            co_str = node_value[0]
            component_id = 4            # Todo: Fixed
            alert_light_value = int(node_value[1])
            # Decode
            co_value = decode_node_value(int(co_str), 'co')

        return

    def handle_serial(self):
        while True:
            if self.serial_message_buffer.qsize() > 0:
                self.handle_serial_message(self.serial_message_buffer.get())
    ################################################################################################

    # Server connection Thread #############################################################################
    def connect_to_mqtt_server(self):
        self.mqtt_client = mqtt.Client(self.mqtt_client_id)
        try:
            self.mqtt_client.connect('test.mosquitto.org')
            print('INFO: Connect to the MQTT server successfully')
        except:
            print('ERROR: Can not connect to the MQTT server')

    def mqtt_server_connection(self):
        self.mqtt_client.loop_start()

    def adafruit_server_connection(self):
        def connected(client_in, aio_feed_id_in, aio_username_in):
            print("Adafruit server is connected")
            client_in.subscribe(aio_feed_id_in, aio_username_in)

        def disconnected(client_in):
            print("Disconnected")
            sys.exit(1)

        def message(client_in, feed_id, payload):
            print(f'Feed ID: {feed_id} Data: {payload}')

        def subscribe(client_in, userdata, mid, granted_qos):
            print("Subscribe thanh cong...")

        client = AdafruitClient(self.aio_username, self.aio_key)
        client.on_connect = connected
        client.on_disconnect = disconnected
        client.on_message = message
        client.on_subscribe = subscribe
        client.connect()
        client.loop_background()
    ######################################################################################

    # Main ###############################################################################
    def start(self):
        # Load Client information
        self.load_client_info('PrivateInfo/MqttClientInfo.json',
                              'PrivateInfo/AdafruitUserInfo.json')

        # Load Sensor information
        self.load_device_info('DeviceInfo.json')

        # Set up serial connection
        ser = self.init_serial()

        # Establish connection with the MQTT server
        self.connect_to_mqtt_server()

        # Connect to Adafruit server
        # adafruit_server_connection_thread = threading.Thread(target=self.adafruit_server_connection)
        # adafruit_server_connection_thread.start()

        # Publish all components
        self.publish_components_connection()

        # Connect to MQTT server (create a MQTT connection thread)
        mqtt_server_connection_thread = threading.Thread(target=self.mqtt_server_connection)
        mqtt_server_connection_thread.start()

        # Serial Reader thread
        serial_reader_thread = threading.Thread(target=self.read_serial)
        serial_reader_thread.start()

        # Serial handle
        self.handle_serial()
    ######################################################################################

mess = ''

if __name__ == '__main__':
    temp_gateway = Gateway('a', 'b')
    temp_gateway.start()
    # End #

    print(temp_gateway.device_list['alert-devices'][0].get_metrics())
