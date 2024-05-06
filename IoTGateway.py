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

    def __init__(self):
        # MQTT Server
        self.mqtt_client_socket = None
        self.mqtt_client_id = ''
        self.mqtt_client_token = ''
        # Adafruit Server
        self.aio_client_socket = None
        self.aio_username = ''
        self.aio_key = ''
        self.aio_feed_id = AIO_FEED_ID
        # Device list
        self.device_list = {'fire-alert-devices': [FireAlertDevice()], 'alert-devices': [AlertDevice()]}
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
        # Clear buffer
        self.device_list['fire-alert-device'] = []
        self.device_list['alert-device'] = []

        # Load from the device file
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
                                                sensor_enable=True)
                fire_sensor = None
                if len(fire_alert_device['fire']) > 0:
                    fire_sensor_info = fire_alert_device['fire'][0]
                    device_id = fire_sensor_info['sensor_id']
                    fire_sensor = SensorComponent(feed_id=fire_sensor_info['feed_id'],
                                                  sensor_id=fire_sensor_info['sensor_id'],
                                                  component_id=fire_sensor_info['component_id'],
                                                  processed_data_threshold=fire_sensor_info['processed_data_threshold'],
                                                  sensor_enable=True)
                heat_sensor = None
                if len(fire_alert_device['heat']) > 0:
                    heat_sensor_info = fire_alert_device['heat'][0]
                    device_id = heat_sensor_info['sensor_id']
                    heat_sensor = SensorComponent(feed_id=heat_sensor_info['feed_id'],
                                                  sensor_id=heat_sensor_info['sensor_id'],
                                                  component_id=heat_sensor_info['component_id'],
                                                  processed_data_threshold=heat_sensor_info['processed_data_threshold'],
                                                  sensor_enable=True)
                smoke_sensor = None
                if len(fire_alert_device['smoke']) > 0:
                    smoke_sensor_info = fire_alert_device['smoke'][0]
                    device_id = smoke_sensor_info['sensor_id']
                    smoke_sensor = SensorComponent(feed_id=smoke_sensor_info['feed_id'],
                                                   sensor_id=smoke_sensor_info['sensor_id'],
                                                   component_id=smoke_sensor_info['component_id'],
                                                   processed_data_threshold=smoke_sensor_info['processed_data_threshold'],
                                                   sensor_enable=True)
                lpg_sensor = None
                if len(fire_alert_device['lpg']) > 0:
                    lpg_sensor_info = fire_alert_device['lpg'][0]
                    device_id = lpg_sensor_info['sensor_id']
                    lpg_sensor = SensorComponent(feed_id=lpg_sensor_info['feed_id'],
                                                 sensor_id=lpg_sensor_info['sensor_id'],
                                                 component_id=lpg_sensor_info['component_id'],
                                                 processed_data_threshold=lpg_sensor_info['processed_data_threshold'],
                                                 sensor_enable=True)
                button_component = None
                if len(fire_alert_device['button']) > 0:
                    button_component_info = fire_alert_device['button'][0]
                    device_id = button_component_info['device_id']
                    button_component = ButtonComponent(feed_id=button_component_info['feed_id'],
                                                       device_id=button_component_info['device_id'],
                                                       component_id=button_component_info['component_id'],
                                                       component_enable=True)
                light_component = None
                if len(fire_alert_device['light']) > 0:
                    light_component_info = fire_alert_device['light'][0]
                    device_id = light_component_info['device_id']
                    light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'],
                                                      component_enable=True)
                buzzer_component = None
                if len(fire_alert_device['buzzer']) > 0:
                    buzzer_component_info = fire_alert_device['buzzer'][0]
                    device_id = buzzer_component_info['device_id']
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'],
                                                       component_enable=True)

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
                                                       component_enable=True)
                light_component = None
                if len(alert_device['light']) > 0:
                    light_component_info = alert_device['light'][0]
                    device_id = light_component_info['device_id']
                    light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                      device_id=light_component_info['device_id'],
                                                      component_id=light_component_info['component_id'],
                                                      component_enable=True)
                buzzer_component = None
                if len(alert_device['buzzer']) > 0:
                    buzzer_component_info = alert_device['buzzer'][0]
                    device_id = buzzer_component_info['device_id']
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'],
                                                       component_enable=True)

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

    # Miscellaneous #############################################################################
    def get_device_type(self, device_id):
        for device in self.device_list['fire-alert-devices']:
            if device.get_device_id() == device_id:
                return 'fire-alert-device'
        for device in self.device_list['alert-devices']:
            if device.get_device_id() == device_id:
                return 'alert-device'
        return ''

    #############################################################################################

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
            self.mqtt_client_socket.publish(topic=message_topic, payload=json.dump(message))
        except:
            print('ERROR: Can not publish the message to the MQTT Server')
    #############################################################################################

    # Processing ################################################################################
    def dangerous_detector(self):
        # Todo: 1 thread Kiểm tra (inspect) các giá trị status của các device trong list, với tần số cao hơn tần số gửi
        #       mẫu. ifo device.status != 'safe' -> publish to MQTT server (just 1 time)
        pass
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
        # Todo: Put data to buffer
        # Parser
        data = serial_message.replace("!", "")
        data = data.replace("#", "")
        split_data = data.split(":")
        node_funct_id = split_data[NODE_FUNCT_ID_IDX]
        node_device_id = split_data[NODE_DEVICE_ID_IDX]
        node_value = [0] * NODE_VALUE_6_IDX
        for idx in range(len(split_data) - NODE_VALUE_1_IDX):  #
            node_value[idx] = split_data[NODE_VALUE_1_IDX + idx]

        # Handling
        if node_funct_id == FUNCT_READ_INPUT_UART:
            device_type = self.get_device_type(node_device_id)
            if device_type == 'fire-alert-device':
                if len(split_data) == 7:        # Fire-alert device
                    co_str = node_value[0]
                    smoke_str = node_value[1]
                    fire_str = node_value[2]
                    co_value = decode_node_value(int(co_str), 'co')
                    smoke_value = decode_node_value(int(smoke_str), 'smoke')
                    fire_value = decode_node_value(int(fire_str), 'fire')
                    for device in self.device_list['fire-alert-devices']:
                        if device.get_device_id() == node_device_id:
                            device.put_data_co_sensor(component_id=COMP_ID_CO, value=co_value)
                            device.put_data_smoke_sensor(component_id=COMP_ID_SMOKE, value=smoke_value)
                            device.put_data_fire_sensor(component_id=COMP_ID_FIRE, value=fire_value)
                            return
                    print(f'ERROR: Can not find the device with ID {node_device_id} (1)')
                    return
                elif len(split_data) == 3:      # LPG sensor
                    lpg_str = node_value[0]
                    lpg_value = decode_node_value(int(lpg_str), 'lpg')
                    for device in self.device_list['fire-alert-devices']:
                        if device.get_device_id() == node_device_id:
                            device.put_data_lpg_sensor(component_id=COMP_ID_LPG, value=lpg_value)
                            return
                    print(f'ERROR: Can not find the device with ID {node_device_id} (2)')
                    return
                else:
                    print('ERROR: Wrong UART format')
                    return
            elif device_type == 'alert-device':
                # Todo: Put ON-OFF request to queue (button-process-queue)
                #       Queue này sẽ có 3 nguồn put vào là PhysicalButton + CS Application
                #       sẽ có 1 thread lấy từng ON-OFF Request để xử lý (gửi xuống phần cứng, cập nhật lên phần mềm)
                pass
            else:
                pass
        # if node_device_id == CO_DETECTION_ENUM:
        #     co_str = node_value[0]
        #     component_id = 4            # Todo: Fixed
        #     alert_light_value = int(node_value[1])
        #     # Decode
        #     co_value = decode_node_value(int(co_str), 'co')

        return

    def handle_serial(self):
        while True:
            if self.serial_message_buffer.qsize() > 0:
                self.handle_serial_message(self.serial_message_buffer.get())
    ################################################################################################

    # Server connection Thread #############################################################################
    def connect_to_mqtt_server(self):
        self.mqtt_client_socket = mqtt.Client(self.mqtt_client_id)
        try:
            self.mqtt_client_socket.connect('test.mosquitto.org')
            print('INFO: Connect to the MQTT server successfully')
        except:
            print('ERROR: Can not connect to the MQTT server')

    def mqtt_server_connection(self):
        self.mqtt_client_socket.loop_start()

    def adafruit_server_connection(self):
        def connected(client_in):
            print("INFO: The Adafruit server is connected")
            client_in.subscribe(self.aio_feed_id, self.aio_username)

        def disconnected(client_in):
            print("INFO: The Adafruit server has disconnected")
            sys.exit(1)

        def message(client_in, feed_id, payload):
            print(f'Feed ID: {feed_id} Data: {payload}')

        def subscribe(client_in, userdata, mid, granted_qos):
            print("INFO: Subscribe to the Adafruit server successfully")

        self.aio_client_socket = AdafruitClient(self.aio_username, self.aio_key)
        self.aio_client_socket.on_connect = connected
        self.aio_client_socket.on_disconnect = disconnected
        self.aio_client_socket.on_message = message
        self.aio_client_socket.on_subscribe = subscribe
        self.aio_client_socket.connect()
        self.aio_client_socket.loop_background()
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

        # Publish all components to the MQTT server
        self.publish_components_connection()

        # Connect to Adafruit server for Dashboard
        adafruit_server_connection_thread = threading.Thread(target=self.adafruit_server_connection)
        adafruit_server_connection_thread.start()

        # Connect to MQTT server (create a MQTT connection thread)
        mqtt_server_connection_thread = threading.Thread(target=self.mqtt_server_connection)
        mqtt_server_connection_thread.start()

        # Serial Reader thread
        serial_reader_thread = threading.Thread(target=self.read_serial)
        serial_reader_thread.start()

        # Serial Reader thread
        dangerous_detector_thread = threading.Thread(target=self.dangerous_detector)
        dangerous_detector_thread.start()

        # Serial handle
        self.handle_serial()
    ######################################################################################


mess = ''

if __name__ == '__main__':
    temp_gateway = Gateway()
    temp_gateway.start()

    # End #

