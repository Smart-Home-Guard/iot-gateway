import math


def decode_node_value(node_value, component_enc):
    if component_enc == 'lpg':
        # Node's value = voltage / 100
        if node_value < 110:
            node_value = 110
        elif node_value >= 450:
            node_value = 449
        voltage = node_value / 100
        # Parts Per Million = ln((voltage - 4.5) / (-3.5)) / (-0.0005)
        ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0005)
        ppm = 0 if ppm < 0 else ppm
        return round(ppm, 2)
    elif component_enc == 'co':
        # Node's value = voltage * 50
        if node_value >= 450:
            node_value = 450 - 1
        voltage = node_value / 100
        ppm = math.log((voltage - 4.5) / (-3.4)) / (-0.0011)
        ppm = 0 if ppm < 0 else ppm
        return round(ppm, 2)
    elif component_enc == 'fire':
        # Node's value = voltage * 50
        voltage = node_value / 100
        ppm = 5 - voltage
        ppm = 0 if ppm < 0 else ppm
        return round(ppm, 2)
    elif component_enc == 'smoke':
        # Node's value = voltage * 50
        if node_value >= 340:
            node_value = 340 - 1
        voltage = node_value / 100
        ppm = math.log((voltage - 3.4) / (-2.3)) / (-0.0025)
        ppm = 0 if ppm < 0 else ppm
        return round(ppm, 2)
    elif component_enc == 'heat':
        # Node's value = voltage * 50
        voltage = node_value / 100
        ppm = voltage
        ppm = 0 if ppm < 0 else ppm
        return round(ppm, 2)
    else:
        return node_value
