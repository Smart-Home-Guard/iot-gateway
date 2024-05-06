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
CO_DETECTION_ENUM = "0"
LpgDetectionEnum = "1"
FireDetectionEnum = "2"
AlertButtonEnum = "3"
AlertLightEnum = "4"
AlertBuzzerEnum = "5"

# Function field
# Function ID ('kind' enum)
# 1. fire-metrics
KENUM_READ_DEVICE_DATA = 0
KENUM_ALERT_FIRE_DANGER = 1
# 2. device-status-metrics
KENUM_CONNECT_DEVICE = 2
KENUM_DISCONNECT_DEVICE = 3
KENUM_READ_DEVICE_BATTERY = 0
KENUM_READ_DEVICE_ERROR = 1
