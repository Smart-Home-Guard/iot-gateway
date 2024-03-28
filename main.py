# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# # For Adafruit
import sys
import time
import random
import serial
import serial.tools.list_ports
import math

from Adafruit_IO import MQTTClient
import json

AIO_FEED_ID = ["smarthomeguard.shg-lpg",
               "smarthomeguard.shg-fire",
               "smarthomeguard.shg-co",
               "smarthomeguard.shg-smoke",
               "smarthomeguard.shg-heat",
               "smarthomeguard.shg-fire-alert",
               "smarthomeguard.shg-smoke-alert",
               "smarthomeguard.shg-co-alert",
               "smarthomeguard.shg-lpg-alert",
               "smarthomeguard.shg-alert-button",
               "smarthomeguard.shg-alert-light",
               "smarthomeguard.shg-alert-buzzer"]
AIO_USERNAME = "atfox272"
AIO_KEY = "aio_AiZy57V7CqYlDC4SzEMIeKvXoYMQ"

SHG_LPG_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-lpg" in element][0]
SHG_FIRE_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-fire" in element][0]
SHG_CO_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-co" in element][0]
SHG_SMOKE_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-smoke" in element][0]
SHG_HEAT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-heat" in element][0]
# SHG_FIRE_ALERT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-fire-alert" in element][0]
# SHG_SMOKE_ALERT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-smoke-alert" in element][0]
# SHG_CO_ALERT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-co-alert" in element][0]
# SHG_LPG_ALERT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-lpg-alert" in element][0]
SHG_ALERT_BUTTON_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-alert-button" in element][0]
SHG_ALERT_LIGHT_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-alert-light" in element][0]
SHG_ALERT_BUZZER_ID = [index for index, element in enumerate(AIO_FEED_ID) if "shg-alert-buzzer" in element][0]

# Node configuration
# Format <FUNCTION_ID><DEVICE_ID><VALUE>....<VALUE>
NODE_FUNCT_ID_IDX = 0
NODE_DEVICE_ID_IDX = 1
NODE_VALUE_1_IDX = 2
NODE_VALUE_2_IDX = 3
NODE_VALUE_3_IDX = 4
NODE_VALUE_4_IDX = 5
NODE_VALUE_5_IDX = 6
NODE_VALUE_6_IDX = 7
# Component encode
COMP_SMOKE_ENC = 0
COMP_FIRE_ENC = 1
COMP_HEAT_ENC = 2
COMP_CO_ENC = 3
COMP_LPG_ENC = 4
COMP_LIGHT_ENC = 5
COMP_BUZZER_ENC = 6
COMP_BTN_ENC = 7
# Alert threshold
FEED_LPG_THRESHOLD = 1000       # ppm
FEED_CO_THRESHOLD = 100         # ppm
# FEED_HEAT_THRESHOLD = 3.0     # C/s
FEED_SMOKE_THRESHOLD = 1000      #
FEED_FIRE_THRESHOLD = 2.5       # lux
# Alert level
FEED_LPG_ALERT_HIGH = 1
FEED_LPG_ALERT_LOW = 0
FEED_CO_ALERT_HIGH = 1
FEED_CO_ALERT_LOW = 0
FEED_FIRE_ALERT_HIGH = 1
FEED_FIRE_ALERT_LOW = 0

# Enum table
## Function ID
ReadInputEnum = 0
NotifyBatteryEnum = 1
NotifyErrorEnum = 2
WriteOutputEnum = 3
## Device ID
CoDetectionEnum = "0"
LpgDetectionEnum = "1"
FireDetectionEnum = "2"
AlertButtonEnum = "3"
AlertLightEnum = "4"
AlertBuzzerEnum = "5"


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


# Connect segment
## Adafruit Interface
client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.connect()
client.loop_background()

## IoT Server todo
# client_id = ''
# mqtt_client = mqtt.Client(client_id)
# mqtt_client.connect('test.mosquitto.org')
# mqtt_client.loop_start()


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



mess = ""


def decodeNodeValue(node_value, component_enc):
    if component_enc == COMP_LPG_ENC:
        # Node's value = voltage / 100
        if node_value < 110:
            node_value = 110
        voltage = node_value / 100
        # Parts Per Million = ln((voltage - 4.5) / (-3.5)) / (-0.0005)
        ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0005)
        return ppm
    elif component_enc == COMP_CO_ENC:
        # Node's value = voltage * 50
        voltage = node_value / 100
        ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0011)
        return voltage
    elif component_enc == COMP_FIRE_ENC:
        # Node's value = voltage * 50
        voltage = node_value / 100
        ppm = 5 - voltage
        return ppm
    elif component_enc == COMP_SMOKE_ENC:
        # Node's value = voltage * 50
        voltage = node_value / 100
        ppm = math.log((voltage - 3.4) / (-2.3)) / (-0.0025)
        return ppm
    elif component_enc == COMP_HEAT_ENC:
        # Node's value = voltage * 50
        voltage = node_value / 100

        return voltage
    else:
        return node_value


# def backendSimulator(node_value, component_enc):
    # if int(component_enc) == COMP_LPG_ENC:
    #     # Threshold 1k ppm
    #     if node_value < FEED_LPG_THRESHOLD:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_LPG_ID], FEED_LPG_ALERT_LOW)
    #     else:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_LPG_ID], FEED_LPG_ALERT_HIGH)
    # elif int(component_enc) == COMP_CO_ENC:
    #     if node_value < FEED_CO_THRESHOLD:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_CO_ID], FEED_LPG_ALERT_LOW)
    #     else:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_CO_ID], FEED_LPG_ALERT_HIGH)
    # elif int(component_enc) == COMP_FIRE_ENC:
    #     if node_value < FEED_FIRE_THRESHOLD:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_FIRE_ID], FEED_FIRE_ALERT_LOW)
    #     else:
    #         client.publish(AIO_FEED_ID[SHG_ALERT_FIRE_ID], FEED_FIRE_ALERT_HIGH)
    # elif int(component_enc) == COMP_




# def processData(data):
#     data = data.replace("!", "")
#     data = data.replace("#", "")
#     splitData = data.split(":")
#     print(splitData)
#     if splitData[1] == "LPG":
#         client.publish("smarthomeguard.shg-lpg", splitData[2])
#     elif splitData[1] == "FIRE":
#         client.publish("smarthomeguard.shg-fire", splitData[2])


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
#     real_value = str(decodeNodeValue(int(node_value), node_component))
#     server_command = node_id + ':' + node_component + ':' + real_value + ':' + node_alert + ':' + node_status
#     print("Command to server: " + server_command)
#
    # if node_component == "LPG":
    #     client.publish(AIO_FEED_ID[SHG_LPG_ID], real_value)
    #     client.publish(AIO_FEED_ID[SHG_ALERT_LPG_ID], node_alert)
    # elif node_component == "FIRE":
    #     client.publish(AIO_FEED_ID[SHG_FIRE_ID], real_value)
    #     client.publish(AIO_FEED_ID[SHG_ALERT_FIRE_ID], node_alert)
    # elif node_component == "SMOKE":
    #     client.publish(AIO_FEED_ID[SHG_SMOKE_ID], real_value)
    #     client.publish(AIO_FEED_ID[SHG_ALERT_SMOKE_ID], node_alert)
    # elif node_component == "HEAT":
    #     client.publish(AIO_FEED_ID[SHG_HEAT_ID], real_value)
    #     client.publish(AIO_FEED_ID[SHG_ALERT_HEAT_ID], node_alert)
    # elif node_component == "CO":
    #     client.publish(AIO_FEED_ID[SHG_CO_ID], real_value)
    #     client.publish(AIO_FEED_ID[SHG_ALERT_CO_ID], node_alert)

# def preMQTTTransmission(device_id, node_value):


def processData(data):
    # Parser
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    node_funct_id = splitData[NODE_FUNCT_ID_IDX]
    node_device_id = splitData[NODE_DEVICE_ID_IDX]
    node_value = {}
    for i in range(len(splitData) - NODE_VALUE_1_IDX): #
        node_value[i] = splitData[NODE_VALUE_1_IDX + i]

    # Pre-MQTTTransmission process (Decoder + Package Data)
    co_value = 0
    lpg_value = 0
    smoke_value = 0
    heat_value = 0
    fire_value = 0
    button_value = 0
    level_value = 0
    alert_light_value = 0
    alert_buzzer_value = 0
    if (node_device_id == CoDetectionEnum):
        # Parser
        co_str = node_value[0]
        alert_light_value = int(node_value[1])
        # alert_buzzer_value = int(node_value[2])
        # Decoder
        # co_value = int(''.join(map(str, [ord(char) for char in co_str])))
        co_value = decodeNodeValue(int(co_str), COMP_CO_ENC)
        # Backend simulator ##################################
        # todo: Is value is over the threshold
        # True ->
        #           alert_light_value <- 1;
        #           alert_buzzer_value <- 1;
        #           -> Resend to Node controller (alert)
        if co_value >= FEED_CO_THRESHOLD:
            alert_light_value = 1
            alert_buzzer_value = 1
            # !1:0:1#
            cmd_to_node = "!" + str(1) + ":" + str(0) + ":" + str(1) + "#"
            ser.write(cmd_to_node.encode('utf-8'))
            print("MSG to Node (CO):\t\t\t", cmd_to_node)
        # Debugger
        print("CO: ", co_value)
        ######################################################
        # Package
        client.publish(AIO_FEED_ID[SHG_CO_ID], co_value)
        # client.publish(AIO_FEED_ID[SHG_CO_ALERT_ID], alert_light_value)
        # if alert_light_value >= 0:
        #     client.publish(AIO_FEED_ID[SHG_ALERT_LIGHT_ID], alert_light_value)
        #     client.publish(AIO_FEED_ID[SHG_ALERT_BUZZER_ID], alert_buzzer_value)

    elif node_device_id == LpgDetectionEnum:
        # Parser
        lpg_str = node_value[0]
        alert_light_value = int(node_value[1])
        # alert_buzzer_value = int(node_value[2])
        # Decoder
        # lpg_value = int(''.join(map(str, [ord(char) for char in lpg_str])))
        lpg_value = decodeNodeValue(int(lpg_str), COMP_LPG_ENC)

        # Backend simulator ##################################
        # todo: Is value is over the threshold
        # True ->
        #           alert_light_value <- 1;
        #           alert_buzzer_value <- 1;
        #           -> Resend to Node controller (alert)
        if lpg_value >= FEED_LPG_THRESHOLD:
            alert_light_value = 1
            alert_buzzer_value = 1
            # !1:1:1#
            cmd_to_node = "!" + str(1) + ":" + str(1) + ":" + str(1) + "#"
            ser.write(cmd_to_node.encode('utf-8'))
            print("MSG to Node (LPG alert):\t\t\t", cmd_to_node)

        # Debugger ###########################################
        print("LPG: ", lpg_value)
        ######################################################
        # Package
        client.publish(AIO_FEED_ID[SHG_LPG_ID], lpg_value)
        # client.publish(AIO_FEED_ID[SHG_LPG_ALERT_ID], alert_light_value)
        # client.publish(AIO_FEED_ID[SHG_ALERT_LIGHT_ID], alert_light_value)
        # client.publish(AIO_FEED_ID[SHG_ALERT_BUZZER_ID], alert_buzzer_value)
    elif node_device_id == FireDetectionEnum:
        # Parser
        smoke_str = node_value[0]
        heat_str = node_value[1]
        fire_str = node_value[2]
        alert_smoke_light_value = int(node_value[3])
        alert_fire_light_value = int(node_value[4])
        # alert_buzzer_value = int(node_value[5])
        # Decoder
        # smoke_value = int(''.join(map(str, [ord(char) for char in smoke_str])))
        smoke_value = decodeNodeValue(int(smoke_str), COMP_SMOKE_ENC)

        # heat_value = int(''.join(map(str, [ord(char) for char in heat_str])))
        heat_value = decodeNodeValue(int(heat_str), COMP_HEAT_ENC)

        # fire_value = int(''.join(map(str, [ord(char) for char in fire_str])))
        fire_value = decodeNodeValue(int(fire_str), COMP_FIRE_ENC)
        # Backend simulator ##################################
        # todo: Is value is over the threshold
        # True ->
        #           alert_light_value <- 1;
        #           alert_buzzer_value <- 1;
        #           -> Resend to Node controller (alert)
        if smoke_value >= FEED_SMOKE_THRESHOLD:
            alert_smoke_light_value = 1
            alert_buzzer_value = 1
        if fire_value >= FEED_FIRE_THRESHOLD:
            alert_fire_light_value = 1
            alert_buzzer_value = 1
        # Debugger #####################
        print("SMOKE: ", smoke_value)
        print("FIRE: ", fire_value)
        print("HEAT: ", heat_value)
        ################################
        # Do not alert when temperature is come over THRESHOLD
        # if heat_value >= FEED_HEAT_THRESHOLD:
        #     alert_buzzer_value = 1
        # !1:2:1:1:1#
        cmd_to_node = "!" + "1" + ":" + "2" + ":" + str(alert_smoke_light_value) + ":" + str(alert_fire_light_value) + "#"
        if alert_fire_light_value | alert_smoke_light_value:
            ser.write(cmd_to_node.encode('utf-8'))
            print("MSG to Node (FIRE/SMOKE alert):\t\t", cmd_to_node)
        ######################################################
        # Package
        client.publish(AIO_FEED_ID[SHG_SMOKE_ID], smoke_value)
        client.publish(AIO_FEED_ID[SHG_FIRE_ID], fire_value)
        client.publish(AIO_FEED_ID[SHG_HEAT_ID], heat_value)
        # client.publish(AIO_FEED_ID[SHG_SMOKE_ALERT_ID], alert_smoke_light_value)
        # client.publish(AIO_FEED_ID[SHG_FIRE_ALERT_ID], alert_fire_light_value)
        # if alert_fire_light
        # client.publish(AIO_FEED_ID[SHG_ALERT_LIGHT_ID], (alert_fire_light_value | alert_smoke_light_value))
        # client.publish(AIO_FEED_ID[SHG_ALERT_BUZZER_ID], alert_buzzer_value)
    elif(node_device_id == AlertButtonEnum):
        # Parser
        button_str = node_value[0]
        # alert_light_value = int(node_value[1])
        alert_buzzer_value = int(node_value[1])
        # Decoder
        # button_value = int(''.join(map(str, [ord(char) for char in button_str])))
        button_value = int(button_str)
        # button_value = decodeNodeValue(lpg_value, COMP_LPG_ENC)
        # Backend simulator ##################################
        # todo: Is value is over the threshold
        # True ->
        #           alert_light_value <- 1;
        #           alert_buzzer_value <- 1;
        #           -> Resend to Node controller (alert)
        if button_value >= 1:
            alert_light_value = 1
            alert_buzzer_value = 1
            # !1:1:1:1#
            cmd_to_node = "!" + str(1) + ":" + str(3) + ":" + str(1) + "#"
            ser.write(cmd_to_node.encode('utf-8'))
            print("MSG to Node (BUTTON):\t\t\t", cmd_to_node)
        else:
            alert_light_value = 0
            alert_buzzer_value = 0
            # !1:1:1:1#
            cmd_to_node = "!" + str(1) + ":" + str(3) + ":" + str(0) + ":" + str(0) + "#"
            ser.write(cmd_to_node.encode('utf-8'))
            print("MSG to Node (BUTTON):\t\t", cmd_to_node)
        # Debugger #########################################
        print("BUTTON: ", button_value)
        ######################################################
        # Package
        client.publish(AIO_FEED_ID[SHG_ALERT_BUTTON_ID], button_value)
        client.publish(AIO_FEED_ID[SHG_ALERT_LIGHT_ID], alert_light_value)
        client.publish(AIO_FEED_ID[SHG_ALERT_BUZZER_ID], alert_buzzer_value)
    # In-MQTTTransmission process (Transmit the packet)

    # Post-MQTTTransmission process (DO NOT IMPLEMENT THIS CASE)

    # real_value = str(decodeNodeValue(int(node_value), node_component))
    # server_command = node_id + ':' + node_component + ':' + real_value
    # print("Command to server: " + server_command)
    # if node_component == "LPG":
    #     client.publish(AIO_FEED_ID[SHG_LPG_ID], real_value)
    # elif node_component == "FIRE":
    #     client.publish(AIO_FEED_ID[SHG_FIRE_ID], real_value)
    # elif node_component == "SMOKE":
    #     client.publish(AIO_FEED_ID[SHG_SMOKE_ID], real_value)
    # elif node_component == "HEAT":
    #     client.publish(AIO_FEED_ID[SHG_HEAT_ID], real_value)
    # elif node_component == "CO":
    #     client.publish(AIO_FEED_ID[SHG_CO_ID], real_value)


def readSerial():
    bytesToRead = ser.in_waiting
    if bytesToRead > 0:
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        # print(mess + "\n")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end+1:]


# Connect segment (Nodes Interface)
ser = serial.Serial(port = "COM17", baudrate = 115200) # COM17 - COM15

while True:
    readSerial()
    time.sleep(1)

