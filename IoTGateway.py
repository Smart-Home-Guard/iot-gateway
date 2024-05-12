import json
import queue
import sys
import threading
import time

import serial
import serial.tools.list_ports
from Adafruit_IO import MQTTClient as AdafruitClient
import paho.mqtt.client as mqtt
from Misc.Constants import *
from Devices.FireAlertDevice import *
from Devices.AlertDevice import *
from Components.SensorComponent import *
from Components.ButtonComponent import *
from Components.OutputComponent import *
from Misc.Miscellaneous import *


class Gateway:
    # Mode configuration
    WITHOUT_SERIAL_CONNECTION = True

    def __init__(self):
        # MQTT Server
        self.mqtt_client_socket = None
        self.mqtt_client_id = ''
        self.mqtt_client_token = ''
        self.mqtt_message_buffer = queue.Queue()
        # Adafruit Server
        self.aio_client_socket = None
        self.aio_username = ''
        self.aio_key = ''
        self.aio_feed_id = AIO_FEED_ID
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
                co_sensor = SensorComponent()
                if 'co' in fire_alert_device:
                    if len(fire_alert_device['co']) > 0:
                        co_sensor_info = fire_alert_device['co'][0]
                        device_id = co_sensor_info['sensor_id']
                        co_sensor = SensorComponent(feed_id=co_sensor_info['feed_id'],
                                                    sensor_id=co_sensor_info['sensor_id'],
                                                    component_id=co_sensor_info['component_id'],
                                                    processed_data_threshold=co_sensor_info['processed_data_threshold'],
                                                    sensor_enable=True)
                        print(f'INFO: Create CO sensor with device ID {co_sensor_info['sensor_id']} '
                              f'and component ID {co_sensor_info['component_id']}')
                fire_sensor = SensorComponent()
                if 'fire' in fire_alert_device:
                    if len(fire_alert_device['fire']) > 0:
                        fire_sensor_info = fire_alert_device['fire'][0]
                        device_id = fire_sensor_info['sensor_id']
                        fire_sensor = SensorComponent(feed_id=fire_sensor_info['feed_id'],
                                                      sensor_id=fire_sensor_info['sensor_id'],
                                                      component_id=fire_sensor_info['component_id'],
                                                      processed_data_threshold=fire_sensor_info['processed_data_threshold'],
                                                      sensor_enable=True)
                        print(f'INFO: Create FIRE sensor with device ID {fire_sensor_info['sensor_id']} '
                              f'and component ID {fire_sensor_info['component_id']}')
                heat_sensor = SensorComponent()
                if 'heat' in fire_alert_device:
                    if len(fire_alert_device['heat']) > 0:
                        heat_sensor_info = fire_alert_device['heat'][0]
                        device_id = heat_sensor_info['sensor_id']
                        heat_sensor = SensorComponent(feed_id=heat_sensor_info['feed_id'],
                                                      sensor_id=heat_sensor_info['sensor_id'],
                                                      component_id=heat_sensor_info['component_id'],
                                                      processed_data_threshold=heat_sensor_info['processed_data_threshold'],
                                                      sensor_enable=True)
                        print(f'INFO: Create HEAT sensor with device ID {heat_sensor_info['sensor_id']} '
                              f'and component ID {heat_sensor_info['component_id']}')
                smoke_sensor = SensorComponent()
                if 'smoke' in fire_alert_device:
                    if len(fire_alert_device['smoke']) > 0:
                        smoke_sensor_info = fire_alert_device['smoke'][0]
                        device_id = smoke_sensor_info['sensor_id']
                        smoke_sensor = SensorComponent(feed_id=smoke_sensor_info['feed_id'],
                                                       sensor_id=smoke_sensor_info['sensor_id'],
                                                       component_id=smoke_sensor_info['component_id'],
                                                       processed_data_threshold=smoke_sensor_info['processed_data_threshold'],
                                                       sensor_enable=True)
                        print(f'INFO: Create SMOKE sensor with device ID {smoke_sensor_info['sensor_id']} '
                              f'and component ID {smoke_sensor_info['component_id']}')
                lpg_sensor = SensorComponent()
                if 'lpg' in fire_alert_device:
                    if len(fire_alert_device['lpg']) > 0:
                        lpg_sensor_info = fire_alert_device['lpg'][0]
                        device_id = lpg_sensor_info['sensor_id']
                        lpg_sensor = SensorComponent(feed_id=lpg_sensor_info['feed_id'],
                                                     sensor_id=lpg_sensor_info['sensor_id'],
                                                     component_id=lpg_sensor_info['component_id'],
                                                     processed_data_threshold=lpg_sensor_info['processed_data_threshold'],
                                                     sensor_enable=True)
                        print(f'INFO: Create LPG sensor with device ID {lpg_sensor_info['sensor_id']} '
                              f'and component ID {lpg_sensor_info['component_id']}')
                light_component = None
                if 'light' in fire_alert_device:
                    if len(fire_alert_device['light']) > 0:
                        light_component_info = fire_alert_device['light'][0]
                        device_id = light_component_info['device_id']
                        light_component = OutputComponent(feed_id=light_component_info['feed_id'],
                                                          device_id=light_component_info['device_id'],
                                                          component_id=light_component_info['component_id'],
                                                          component_enable=True)
                        print(f'INFO: Create LIGHT component with device ID {light_component_info['device_id']} '
                              f'and component ID {light_component_info['component_id']}')
                buzzer_component = None
                if 'buzzer' in fire_alert_device:
                    if len(fire_alert_device['buzzer']) > 0:
                        buzzer_component_info = fire_alert_device['buzzer'][0]
                        device_id = buzzer_component_info['device_id']
                        buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                           device_id=buzzer_component_info['device_id'],
                                                           component_id=buzzer_component_info['component_id'],
                                                           component_enable=True)
                        print(f'INFO: Create BUZZER component with device ID {buzzer_component_info['device_id']} '
                              f'and component ID {buzzer_component_info['component_id']}')

                battery_component = None
                if 'battery' in fire_alert_device:
                    if len(fire_alert_device['battery']) > 0:
                        battery_component_info = fire_alert_device['battery'][0]
                        device_id = battery_component_info['device_id']
                        battery_component = BatteryComponent(device_id=battery_component_info['device_id'],
                                                             component_id=battery_component_info['component_id'],
                                                             rate_capacity=battery_component_info['rate_capacity'])

                fire_alert_device = FireAlertDevice(device_id=device_id, co_sensor=co_sensor, fire_sensor=fire_sensor,
                                                    heat_sensor=heat_sensor, smoke_sensor=smoke_sensor,
                                                    lpg_sensor=lpg_sensor, light_component=light_component,
                                                    buzzer_component=buzzer_component, battery_component=battery_component)
                print(f'INFO: Create a fire-alert device with ID {fire_alert_device.get_device_id()}')
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
                    print(f'INFO: Create BUTTON component with device ID {button_component_info['device_id']} '
                          f'and component ID {button_component_info['component_id']}')
                buzzer_component = None
                if len(alert_device['buzzer']) > 0:
                    buzzer_component_info = alert_device['buzzer'][0]
                    device_id = buzzer_component_info['device_id']
                    buzzer_component = OutputComponent(feed_id=buzzer_component_info['feed_id'],
                                                       device_id=buzzer_component_info['device_id'],
                                                       component_id=buzzer_component_info['component_id'],
                                                       component_enable=True)
                    print(f'INFO: Create BUZZER component with device ID {buzzer_component_info['device_id']} '
                          f'and component ID {buzzer_component_info['component_id']}')

                battery_component = None
                if 'battery' in alert_device:
                    if len(alert_device['battery']) > 0:
                        battery_component_info = alert_device['battery'][0]
                        device_id = battery_component_info['device_id']
                        battery_component = BatteryComponent(device_id=battery_component_info['device_id'],
                                                             component_id=battery_component_info['component_id'],
                                                             rate_capacity=battery_component_info['rate_capacity'])

                alert_device = AlertDevice(device_id=device_id, button_component=button_component,
                                           buzzer_component=buzzer_component, battery_component=battery_component)
                print(f'INFO: Create a alert device with ID {alert_device.get_device_id()}')
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

    def sync_output_component_object(self, device, new_light_state, new_buzzer_state):
        device_metrics = device.get_metrics()
        prev_light_state = device_metrics['fire-light'][0]['value']
        prev_buzzer_state = device_metrics['fire-buzzer'][0]['value']
        if not new_light_state == prev_light_state:     # state_change == True
            # Update to gateway
            device.set_state_light_component(new_light_state)
            # Update to the application
            cur_light_metrics = device.get_metrics()['fire-light']
            self.publish_component_state(message_kind=KENUM_READ_DEVICE_DATA, light_component_list=cur_light_metrics)
            print(f'INFO: Update the light state of the application ({cur_light_metrics})')
            pass
        if not new_buzzer_state == prev_buzzer_state:   # state_change == True
            # Update to gateway
            device.set_state_buzzer_component(new_buzzer_state)
            # Update to software
            cur_buzzer_metrics = device.get_metrics()['fire-buzzer']
            self.publish_component_state(message_kind=KENUM_READ_DEVICE_DATA, buzzer_component_list=cur_buzzer_metrics)
            print(f'INFO: Update the buzzer state of the application ({cur_buzzer_metrics})')
            pass
    #############################################################################################

    # Get attr of the object ####################################################################
    def get_components_list(self):
        components_list = []
        for device in self.device_list['fire-alert-devices']:
            components_list = components_list + device.get_info()
        for device in self.device_list['alert-devices']:
            components_list = components_list + device.get_info()
        # print(components_list)
        return components_list
    #############################################################################################

    # MQTT Server method ########################################################################
    def get_topic(self, channel_type):
        if channel_type == 'fire-alert':
            return self.mqtt_client_id + '/fire-alert-metrics'
        elif channel_type == 'devices-status':
            return self.mqtt_client_id + 'devices-status-metrics'
        return ''

    def publish_components_server(self):
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
        # self.mqtt_client_socket.publish(topic=message_topic, payload=json.dumps(message))
        try:
            self.mqtt_client_socket.publish(topic=message_topic, payload=json.dumps(message))
        except:
            print('ERROR: Can not publish the message to the MQTT Server (1)')

    def publish_component_state(self, message_kind=KENUM_READ_DEVICE_DATA, fire_sensor_list=None, smoke_sensor_list=None,
                                co_sensor_list=None, heat_sensor_list=None, light_component_list=None,
                                lpg_component_list=None, button_component_list=None, buzzer_component_list=None):
        message_topic = self.get_topic(channel_type='fire-alert')   # Fixed this
        message = {
            'kind': message_kind,    # 0-manual update; 1-alert
            "payload": {
                "token": self.mqtt_client_token,
                "fire": fire_sensor_list,
                "smoke": smoke_sensor_list,
                "co": co_sensor_list,
                "heat": heat_sensor_list,
                "lpg": lpg_component_list,
                "fire-button": button_component_list,
                "fire-light": light_component_list,
                "fire-buzzer": buzzer_component_list
            },
        }
        try:
            self.mqtt_client_socket.publish(topic=message_topic, payload=json.dumps(message))
        except:
            print('ERROR: Can not publish the message to the MQTT Server (2)')
    #############################################################################################

    # Processing ################################################################################
    def manual_update_device_metrics(self):    # For fire-alert-devices
        while True:
            time.sleep(5)
            for device in self.device_list['fire-alert-devices']:
                device.update_new_data()
                device_metrics = device.get_metrics()
                message_kind = 0
                if device.get_status() == 'safe':
                    message_kind = KENUM_READ_DEVICE_DATA  # Manual update enum
                else:
                    message_kind = KENUM_ALERT_FIRE_DANGER  # Alert enum
                # Publish to MQTT Server
                self.publish_component_state(message_kind=message_kind, co_sensor_list=device_metrics['co'],
                                             fire_sensor_list=device_metrics['fire'],
                                             heat_sensor_list=device_metrics['heat'],
                                             smoke_sensor_list=device_metrics['smoke'],
                                             lpg_component_list=device_metrics['lpg'],
                                             light_component_list=device_metrics['fire-light'],
                                             buzzer_component_list=device_metrics['fire-buzzer'])
                print(f'INFO: Publish device metrics (msg_kind = {message_kind}) with payload: {device_metrics}')
                # Update to the device
                component_status_dict = device.get_component_status()
                fire_light_alert = component_status_dict['fire'] == 'dangerous'
                co_light_alert = component_status_dict['co'] == 'dangerous'
                smoke_light_alert = component_status_dict['smoke'] == 'dangerous'
                lpg_light_alert = component_status_dict['lpg'] == 'dangerous'
                command_to_serial = ('!' + '1' + ':' +
                                     str(device.get_device_id()) + ':' +
                                     str(int(co_light_alert)) + ':' +
                                     str(int(smoke_light_alert)) + ':' +
                                     str(int(fire_light_alert)) + ':' +
                                     str(int(lpg_light_alert)) + '#')
                print(f'INFO: Write to the serial: {command_to_serial}')
                if not self.WITHOUT_SERIAL_CONNECTION:
                    self.serial_obj.write(command_to_serial.encode('utf-8'))

    def dangerous_detector(self):   # For 'fire-alert-device'
        while True:
            for device in self.device_list['fire-alert-devices']:
                new_status_device = device.inspect_new_status()
                cur_status_device = device.get_status()
                if not new_status_device == cur_status_device: # The device status is changed
                    # Update immediately
                    device.update_new_data()
                    # Publish to MQTT Server
                    device_metrics = device.get_metrics()
                    message_kind = 0
                    if device.get_status() == 'safe':
                        message_kind = KENUM_READ_DEVICE_DATA    # Manual update enum
                    else:
                        message_kind = KENUM_ALERT_FIRE_DANGER    # Alert enum
                    self.publish_component_state(message_kind=message_kind, co_sensor_list=device_metrics['co'],
                                                 fire_sensor_list=device_metrics['fire'],
                                                 heat_sensor_list=device_metrics['heat'],
                                                 smoke_sensor_list=device_metrics['smoke'],
                                                 lpg_component_list=device_metrics['lpg'],
                                                 light_component_list=device_metrics['fire-light'],
                                                 buzzer_component_list=device_metrics['fire-buzzer'])
                    print(f'INFO: Publish device metrics (msg_kind ={message_kind}) with payload: {device_metrics}')
            time.sleep(0.5)
        pass

    def manual_update_device_status(self):
        time.sleep(10) # Setup time
        while True:
            device_battery_list = []
            for device in self.device_list['fire-alert-devices']:
                device_battery_list.append(device.get_battery_status())
            for device in self.device_list['alert-devices']:
                device_battery_list.append(device.get_battery_status())
            message_topic = self.get_topic(channel_type='devices-status')
            message_body = {
                "kind": KENUM_READ_DEVICE_BATTERY,     # (readBattery),
                'payload': {'token': self.mqtt_client_token, "data": device_battery_list}
            }

            print(f'INFO: Publish battery status of each device to the MQTT server (message: {message_body})')
            # self.mqtt_client_socket.publish(topic=message_topic, payload=json.dumps(message))
            try:
                self.mqtt_client_socket.publish(topic=message_topic, payload=json.dumps(message_body))
            except:
                print('ERROR: Can not publish the message to the MQTT Server (3)')

            time.sleep(180) # Update every 180s (3 minutes)

    #############################################################################################

    # Serial thread #############################################################################
    def read_serial(self):
        while True:
            if not self.WITHOUT_SERIAL_CONNECTION:
                bytes_to_read = self.serial_obj.in_waiting
            else:
                bytes_to_read = input('Your commands: \n')

            if len(bytes_to_read) > 0:
                global mess
                if not self.WITHOUT_SERIAL_CONNECTION:
                    mess = mess + self.serial_obj.read(bytes_to_read).decode("UTF-8")
                else:
                    mess = mess + bytes_to_read
                # print(mess + "\n")
                while ("#" in mess) and ("!" in mess):
                    start = mess.find("!")
                    end = mess.find("#")
                    print(f'INFO: Received a command with content {mess[start:end + 1]}')
                    self.serial_message_buffer.put(mess[start:end + 1])
                    # self.processing_data(mess[start:end + 1])
                    if end == len(mess):
                        mess = ""
                    else:
                        mess = mess[end + 1:]

    def handle_serial_message(self, serial_message):
        # Put data to buffer
        # Parser
        print(f'INFO: Handling a command with content {serial_message}')
        data = serial_message.replace("!", "")
        data = data.replace("#", "")
        split_data = data.split(":")
        node_funct_id = split_data[NODE_FUNCT_ID_IDX]
        node_device_id = int(split_data[NODE_DEVICE_ID_IDX])
        node_value = [0] * (len(split_data) - NODE_VALUE_1_IDX)
        for idx in range(len(split_data) - NODE_VALUE_1_IDX):  #
            node_value[idx] = split_data[NODE_VALUE_1_IDX + idx]

        # Handling
        if node_funct_id == FUNCT_READ_INPUT_UART:
            device_type = self.get_device_type(node_device_id)
            if device_type == 'fire-alert-device':
                if len(node_value) == 7:        # Fire-alert device
                    co_str = node_value[0]
                    smoke_str = node_value[1]
                    fire_str = node_value[2]
                    co_light_str = node_value[3]
                    smoke_light_str = node_value[4]
                    fire_light_str = node_value[5]
                    buzzer_str = node_value[6]
                    co_value = decode_node_value(int(co_str), 'co')
                    smoke_value = decode_node_value(int(smoke_str), 'smoke')
                    fire_value = decode_node_value(int(fire_str), 'fire')
                    co_light_value = int(co_light_str)
                    smoke_light_value = int(smoke_light_str)
                    fire_light_value = int(fire_light_str)
                    buzzer_value = int(buzzer_str)
                    merged_light = co_light_value or smoke_light_value or fire_light_value
                    for device in self.device_list['fire-alert-devices']:
                        if device.get_device_id() == node_device_id:
                            device.put_data_co_sensor(component_id=COMP_ID_CO, value=co_value)
                            device.put_data_smoke_sensor(component_id=COMP_ID_SMOKE, value=smoke_value)
                            device.put_data_fire_sensor(component_id=COMP_ID_FIRE, value=fire_value)
                            print(f'INFO: Handling the updating command from the UART with content {serial_message} '
                                  f'to the device with ID {node_device_id}')
                            # Update CO/SMOKE/FIRE lights, if they are changed
                            self.sync_output_component_object(device=device, new_light_state=merged_light,
                                                              new_buzzer_state=buzzer_value)
                            return
                    print(f'ERROR: Can not find the device with ID {node_device_id} (1)')
                    return
                elif len(node_value) == 3:      # LPG sensor
                    lpg_str = node_value[0]
                    light_str = node_value[1]
                    buzzer_str = node_value[2]
                    lpg_value = decode_node_value(int(lpg_str), 'lpg')
                    light_value = int(light_str)
                    buzzer_value = int(buzzer_str)
                    for device in self.device_list['fire-alert-devices']:
                        if device.get_device_id() == node_device_id:
                            device.put_data_lpg_sensor(component_id=COMP_ID_LPG, value=lpg_value)
                            print(f'INFO: Handling the updating command from the UART with content {serial_message} '
                                  f'to the device with ID {node_device_id}')
                            self.sync_output_component_object(device=device, new_light_state=light_value,
                                                              new_buzzer_state=buzzer_value)
                            return
                    print(f'ERROR: Can not find the device with ID {node_device_id} (2)')
                    return
                else:
                    print('ERROR: Wrong UART format')
                    return
            elif device_type == 'alert-device':
                button_str = node_value[0]
                buzzer_str = node_value[1]
                button_value = int(button_str)
                buzzer_value = int(buzzer_str)
                for device in self.device_list['alert-devices']:
                    if device.get_device_id() == node_device_id:    # Find the device out
                        # Toggle the button (only toggle)
                        device.toggle_button_component_state()
                        cur_buzzer_metrics = device.get_metrics()['fire-buzzer']
                        cur_buzzer_value = cur_buzzer_metrics['value']
                        message_kind = 0
                        if cur_buzzer_value:    # Alert kind
                            message_kind = KENUM_ALERT_FIRE_DANGER
                        else:                   # Safe kind
                            message_kind = KENUM_READ_DEVICE_DATA
                        print(f'INFO: Handling the updating command from the UART with content {serial_message} '
                              f'to the device with ID {node_device_id}')
                        self.publish_component_state(message_kind=message_kind, buzzer_component_list=cur_buzzer_metrics)
                        print(f'INFO: Update the buzzer status of the application ({device.get_metrics()})')
                        return
                print(f'ERROR: Can not find the device with ID {node_device_id} (3)')
                pass
            else:
                print(f'WARNING: Can not find a device with ID {node_device_id} (0)')
                pass
        else:
            print(f'ERROR: The command from the UART - the FUNCTION_ID field is invalid {node_funct_id}')
        # if node_device_id == CO_DETECTION_ENUM:
        #     co_str = node_value[0]
        #     component_id = 4
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

    def mqtt_server_on_message(self, client, userdata, msg):
        print("INFO: Received message '" + str(msg.payload) + "' on topic '" + msg.topic)
        self.mqtt_message_buffer.put(msg.payload)

    def mqtt_server_connection(self):
        self.mqtt_client_socket.on_message = self.mqtt_server_on_message
        self.mqtt_client_socket.loop_start()

    def handle_mqtt_server(self):
        while True:
            if self.mqtt_message_buffer.qsize() > 0:
                self.handle_mqtt_server_message(self.mqtt_message_buffer.get())

    def handle_mqtt_server_message(self, message):
        # Todo: Handle MQTT message (from user)
        print(f'INFO: Received a message from MQTT server with content {message}')
        pass

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
        self.publish_components_server()

        # Connect to Adafruit server for Dashboard
        adafruit_server_connection_thread = threading.Thread(target=self.adafruit_server_connection)
        adafruit_server_connection_thread.start()

        # Connect to MQTT server (create a MQTT connection thread)
        mqtt_server_connection_thread = threading.Thread(target=self.mqtt_server_connection)
        mqtt_server_connection_thread.start()

        # Serial Reader thread
        serial_reader_thread = threading.Thread(target=self.read_serial)
        serial_reader_thread.start()

        # Manual update device metrics
        manual_update_device_metrics_thread = threading.Thread(target=self.manual_update_device_metrics)
        manual_update_device_metrics_thread.start()

        # Manual update device status
        manual_update_device_status_thread = threading.Thread(target=self.manual_update_device_status)
        manual_update_device_status_thread.start()

        # Serial handle
        self.handle_serial()
    ######################################################################################


mess = ''

if __name__ == '__main__':
    gateway = Gateway()
    gateway.start()

    # End #

