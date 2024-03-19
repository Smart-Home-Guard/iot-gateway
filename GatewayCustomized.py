# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# # For Adafruit
# import sys
# import time
# import serial
# import serial.tools.list_ports
# # For MQTT Broker
# import paho.mqtt.client as mqtt
# import json
# import math
# # Gateway configuration
# GATEWAY_ID = "0"
# MQTT_SERVER = ""
# DEVICE_NAME = ["SMOKE", "FIRE", "HEAT", "CO", "LPG", "LIGHT", "BUZZER"]
#
# # Node configuration
# ## Message Format
# NODE_ID_IDX = 0
# NODE_COMPONENT_IDX = 1
# NODE_VALUE_IDX = 2
# NODE_ALERT_IDX = 3
# NODE_STATUS_IDX = 4
#
#
# client_telemetry_topic = GATEWAY_ID + '/telemetry'
# server_command_topic = GATEWAY_ID + '/commands'
#
# # Connect segment (Sever Interface)
# mqtt_client = mqtt.Client(GATEWAY_ID)
# mqtt_client.connect(MQTT_SERVER)
# mqtt_client.loop_start()
#
#
# def message(client, userid, payload):
#     print("User's ID: " + userid + "receives data: " + payload)
#     ser.write((str(payload) + "#").encode())
#
#
# mqtt_client.subscribe(server_command_topic)
# mqtt_client.on_message = message
#
#
# def getPort():
#     ports = serial.tools.list_ports.comports()
#     N = len(ports)
#     commPort = "None"
#     for i in range(0, N):
#         port = ports[i]
#         strPort = str(port)
#         if "USB Serial Device" in strPort:
#             splitPort = strPort.split(" ")
#             commPort = (splitPort[0])
#     return commPort
#
#
# # Connect segment (Nodes Interface)
# ser = serial.Serial(port=getPort(), baudrate=115200)
#
#
# # todo: decode/encode from Nodes
# def decodeNodeValue(node_value, component):
#     if component == "LPG":
#         # Node's value = voltage * 50
#         voltage = node_value / 50
#         # Parts Per Million = ln((voltage - 4.5) / (-3.5)) / (-0.0005)
#         ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0005)
#         return ppm
#     else:
#         return node_value
#
#
# def processData(data):
#     data = data.replace("!", "")
#     data = data.replace("#", "")
#     splitData = data.split(":")
#     node_id = splitData[NODE_ID_IDX]
#     node_component = splitData[NODE_COMPONENT_IDX]
#     node_value = splitData[NODE_VALUE_IDX]
#     node_alert = splitData[NODE_ALERT_IDX]
#     node_status = splitData[NODE_STATUS_IDX]
#     # Decode value
#     real_value = decodeNodeValue(int(node_value), node_component)
#     # todo: seperate data_type from "content" segment of MQTT command
#     # todo: move data_type to Topic of MQTT command
#     server_command = node_id + ':' + node_component + ':' + str(real_value) + ':' + node_alert + ':' + node_status
#     print("Command to server: " + server_command)
#     mqtt_client.publish(client_telemetry_topic, json.dumps(server_command))
#
# mess = ""
#
#
# def readSerial():
#     bytesToRead = ser.in_waiting
#     if bytesToRead > 0:
#         global mess
#         mess = mess + ser.read(bytesToRead).decode("UTF-8")
#         while ("#" in mess) and ("!" in mess):
#             start = mess.find("!")
#             end = mess.find("#")
#             processData(mess[start:end + 1])
#             if end == len(mess):
#                 mess = ""
#             else:
#                 mess = mess[end+1:]
#
#
# while True:
#     readSerial()
#     time.sleep(1)