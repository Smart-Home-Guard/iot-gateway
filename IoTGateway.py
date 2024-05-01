import json
import queue
import sys
import threading

import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports
from Adafruit_IO import MQTTClient
from Constants import *
from SensorComponent import *
from ButtonComponent import *
from OutputComponent import *
from Miscellaneous import *


class Gateway:
    def __init__(self, aio_username, aio_key):
        # MQTT Server
        self.client_id = ''
        self.client_token = ''
        # Adafruit Server
        self.aio_username = aio_username
        self.aio_key = aio_key
        # Device list
        self.device_list = {'fire-alert-devices': [], 'alert-devices': []}
        # Serial message buffer
        self.serial_message_buffer = queue.Queue()

    # Set up connection #################################################################
    def load_client_info(self, client_info_path):
        with open(client_info_path, "r") as file:
            client_info_dict = json.load(file)
        self.client_id = client_info_dict["client_id"]
        self.client_token = client_info_dict["client_token"]

    def load_device_info(self, device_info_path):
        with open(device_info_path, "r") as file:
            device_info_dict = json.load(file)

        if 'fire-alert-devices' in device_info_dict:
            fire_alert_device_list = device_info_dict['fire-alert-devices']
            for idx in range(0, len(fire_alert_device_list)):
                fire_alert_device = fire_alert_device_list[idx]
                # Get information
                co_sensor = None
                if len(fire_alert_device['co']) > 0:
                    co_sensor_info = fire_alert_device['co'][0]
                    co_sensor = SensorComponent(feed_id=co_sensor_info['feed_id'],
                                                sensor_id=co_sensor_info['sensor_id'],
                                                component_id=co_sensor_info['component_id'],
                                                processed_data_threshold=co_sensor_info['processed_data_threshold'])
                fire_sensor = None
                if len(fire_alert_device['fire']) > 0:
                    fire_sensor_info = fire_alert_device['fire'][0]
                    fire_sensor = SensorComponent(feed_id=fire_sensor_info['feed_id'],
                                                  sensor_id=fire_sensor_info['sensor_id'],
                                                  component_id=fire_sensor_info['component_id'],
                                                  processed_data_threshold=fire_sensor_info['processed_data_threshold'])
                heat_sensor = None
                if len(fire_alert_device['heat']) > 0:
                    heat_sensor_info = fire_alert_device['heat'][0]
                    heat_sensor = SensorComponent(feed_id=heat_sensor_info['feed_id'],
                                                  sensor_id=heat_sensor_info['sensor_id'],
                                                  component_id=heat_sensor_info['component_id'],
                                                  processed_data_threshold=heat_sensor_info['processed_data_threshold'])
                smoke_sensor = None
                if len(fire_alert_device['smoke']) > 0:
                    smoke_sensor_info = fire_alert_device['smoke'][0]
                    smoke_sensor = SensorComponent(feed_id=smoke_sensor_info['feed_id'],
                                                   sensor_id=smoke_sensor_info['sensor_id'],
                                                   component_id=smoke_sensor_info['component_id'],
                                                   processed_data_threshold=smoke_sensor_info['processed_data_threshold'])
                lpg_sensor = None
                if len(fire_alert_device['lpg']) > 0:
                    lpg_sensor_info = fire_alert_device['lpg'][0]
                    lpg_sensor = SensorComponent(feed_id=lpg_sensor_info['feed_id'],
                                                 sensor_id=lpg_sensor_info['sensor_id'],
                                                 component_id=lpg_sensor_info['component_id'],
                                                 processed_data_threshold=lpg_sensor_info['processed_data_threshold'])
                button_component = None
                if len(fire_alert_device['button']) > 0:
                    button_component_info = fire_alert_device['button'][0]
                    button_component = ButtonComponent(feed_id=button_component_info['feed_id'],
                                                       device_id=button_component_info['device_id'],
                                                       component_id=button_component_info['component_id'])
                light_component = None
                if len(fire_alert_device['light']) > 0:
                    light_component_info = fire_alert_device['light'][0]
                    light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'])
                buzzer_component = None
                if len(fire_alert_device['buzzer']) > 0:
                    buzzer_component_info = fire_alert_device['buzzer'][0]
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'])
                fire_alert_device_dict = {
                    'co': co_sensor,
                    'fire': fire_sensor,
                    'heat': heat_sensor,
                    'smoke': smoke_sensor,
                    'lpg': lpg_sensor,
                    'button': button_component,
                    'light': light_component,
                    'buzzer': buzzer_component
                }
                self.device_list['fire-alert-devices'].append(fire_alert_device_dict)
        else:
            print(f'Warning: Missing Fire Alert device information')

        if 'alert-devices' in device_info_dict:
            alert_devices_list = device_info_dict['alert-devices']
            for idx in range(0, len(alert_devices_list)):
                alert_device = alert_devices_list[idx]
                button_component = None
                if len(alert_device['button']) > 0:
                    button_component_info = alert_device['button'][0]
                    button_component = ButtonComponent(feed_id=button_component_info['feed_id'],
                                                       device_id=button_component_info['device_id'],
                                                       component_id=button_component_info['component_id'])
                light_component = None
                if len(alert_device['light']) > 0:
                    light_component_info = alert_device['light'][0]
                    light_component = ButtonComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'])
                buzzer_component = None
                if len(alert_device['buzzer']) > 0:
                    buzzer_component_info = alert_device['buzzer'][0]
                    buzzer_component = ButtonComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'])
                alert_device_dict = {
                    'button': button_component,
                    'light': light_component,
                    'buzzer': buzzer_component
                }
                self.device_list['alert-devices'].append(alert_device_dict)

        else:
            print(f'Warning: Missing Alert device information')

    def init_serial(self):
        # Serial connection
        ser = serial.Serial(port="COM17", baudrate=115200)  # COM17 - COM15
        return ser
    ######################################################################################

    # Serial thread #############################################################################
    def read_serial(self, ser):
        bytes_to_read = ser.in_waiting
        if bytes_to_read > 0:
            global mess
            mess = mess + ser.read(bytes_to_read).decode("UTF-8")
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
        node_value = {}
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
    def mqtt_server_connection(self):
        mqtt_client = mqtt.Client(self.client_id)
        mqtt_client.connect('test.mosquitto.org')
        mqtt_client.loop_start()

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

        client = MQTTClient(self.aio_username, self.aio_key)
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
        self.load_client_info('ClientInfo.json')

        # Load Sensor information
        self.load_device_info('DeviceInfo.json')

        # # Set up serial connection
        # ser = self.init_serial()
        #
        # # Connect to Adafruit server
        # adafruit_server_connection_thread = threading.Thread(target=self.adafruit_server_connection)
        # adafruit_server_connection_thread.start()
        #
        # # Connect to MQTT server (create a MQTT connection thread)
        # mqtt_server_connection_thread = threading.Thread(target=self.mqtt_server_connection)
        # mqtt_server_connection_thread.start()
        #
        # # Serial Reader thread
        # serial_reader_thread = threading.Thread(target=self.read_serial)
        # serial_reader_thread.start()
        #
        # # Serial handle
        # self.handle_serial()
    ######################################################################################


mess = ''

temp_gateway = Gateway('a', 'b')
temp_gateway.start()
print(temp_gateway.device_list)