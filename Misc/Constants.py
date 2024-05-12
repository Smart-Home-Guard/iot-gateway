# Adafruit feed ID
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

# Node controller message format
NODE_FUNCT_ID_IDX = 0
NODE_DEVICE_ID_IDX = 1
NODE_VALUE_1_IDX = 2
NODE_VALUE_2_IDX = 3
NODE_VALUE_3_IDX = 4
NODE_VALUE_4_IDX = 5
NODE_VALUE_5_IDX = 6
NODE_VALUE_6_IDX = 7

# Device ID
# CO_DETECTION_ENUM = "0"
# LpgDetectionEnum = "1"
# FireDetectionEnum = "2"
# AlertButtonEnum = "3"
# AlertLightEnum = "4"
# AlertBuzzerEnum = "5"

# Component ID
COMP_ID_SMOKE = 50
COMP_ID_HEAT = 51
COMP_ID_CO = 52
COMP_ID_LPG = 53
COMP_ID_FIRE = 54
COMP_ID_FIRE_BUTTON = 55
COMP_ID_FIRE_LIGHT = 56
COMP_ID_FIRE_BUZZER = 57

# Function field
FUNCT_READ_INPUT_UART = '0'
FUNCT_WRITE_OUTPUT_UART = '1'
# Function ID ('kind' enum)
# 1. fire-metrics
KENUM_READ_DEVICE_DATA = '0'
KENUM_ALERT_FIRE_DANGER = '1'
# 2. device-status-metrics
KENUM_CONNECT_DEVICE = '2'
KENUM_DISCONNECT_DEVICE = '3'
KENUM_READ_DEVICE_BATTERY = '0'
KENUM_READ_DEVICE_ERROR = '1'
