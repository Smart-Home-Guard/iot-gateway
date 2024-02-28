# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# # For Adafruit
import sys
import time
import serial
import serial.tools.list_ports
import math

from Adafruit_IO import MQTTClient

# For MQTT Broker
import paho.mqtt.client as mqtt


AIO_FEED_ID = ["smarthomeguard.shg-lpg", "smarthomeguard.shg-fire", "smarthomeguard.shg-alert"]
AIO_USERNAME = "atfox272"
AIO_KEY = "aio_AiZy57V7CqYlDC4SzEMIeKvXoYMQ"

SHG_LPG_ID = indices = [index for index, element in enumerate(AIO_FEED_ID) if "lpg" in element]
SHG_LPG_FIRE = [index for index, element in enumerate(AIO_FEED_ID) if "fire" in element]

# Node configuration
## Message Format
NODE_ID_IDX = 0
NODE_COMPONENT_IDX = 1
NODE_VALUE_IDX = 2
NODE_ALERT_IDX = 3
NODE_STATUS_IDX = 4

def connected(client):
    print("Connected")
    client.subscribe(AIO_FEED_ID, AIO_USERNAME)

# Built-in function of library
# def subscribe(client , userdata , mid , granted_qos):
#     print("Subcribe thanh cong...")


def disconnected(client):
    print("Disconnected")
    sys.exit(1)


def message(client , feed_id , payload):
    print("FEED ID: " + feed_id + "nhan du lieu: " + payload)
    ser.write((str(payload) + "#").encode())


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
# client.on_subscribe = subscribe

# Connect segment (Sever Interface)
client.connect()

client.loop_background()


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort


# Connect segment (Nodes Interface)
ser = serial.Serial(port=getPort(), baudrate=115200)

mess = ""


def decodeNodeValue(node_value, component):
    if component == "LPG":
        # Node's value = voltage * 50
        voltage = node_value / 50
        # Parts Per Million = ln((voltage - 4.5) / (-3.5)) / (-0.0005)
        ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0005)
        return ppm
    else:
        return node_value


# def processData(data):
#     data = data.replace("!", "")
#     data = data.replace("#", "")
#     splitData = data.split(":")
#     print(splitData)
#     if splitData[1] == "LPG":
#         client.publish("smarthomeguard.shg-lpg", splitData[2])
#     elif splitData[1] == "FIRE":
#         client.publish("smarthomeguard.shg-fire", splitData[2])


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    node_id = splitData[NODE_ID_IDX]
    node_component = splitData[NODE_COMPONENT_IDX]
    node_value = splitData[NODE_VALUE_IDX]
    node_alert = splitData[NODE_ALERT_IDX]
    node_status = splitData[NODE_STATUS_IDX]
    # Decode value
    real_value = decodeNodeValue(int(node_value), node_component)
    server_command = node_id + ':' + node_component + ':' + str(real_value) + ':' + node_alert + ':' + node_status
    print("Command to server: " + server_command)
    if int(node_alert) == 0:
        if splitData[1] == "LPG":
            client.publish("smarthomeguard.shg-lpg", real_value)
        elif splitData[1] == "FIRE":
            client.publish("smarthomeguard.shg-fire", real_value)
    else:
        client.publish("smarthomeguard.shg-alert", real_value)



def readSerial():
    bytesToRead = ser.in_waiting
    if bytesToRead > 0:
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end+1:]


while True:
    readSerial()
    time.sleep(1)

