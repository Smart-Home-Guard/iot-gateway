from Components.ButtonComponent import *
from Components.OutputComponent import *
from Components.BatteryComponent import *


class AlertDevice:
    def __init__(self, device_id=None, button_component=ButtonComponent(),
                 buzzer_component=OutputComponent(), battery_component=BatteryComponent()):
        self.device_id = device_id
        self.button_component = button_component
        self.buzzer_component = buzzer_component
        self.battery_component = battery_component
        self.mute_alert_buzzer = 0     # 1-'on' / 0-'off'
        self.state = 0   # (1-'alert' / 0-'safe')

    #################################################################

    def get_button_component_state(self):
        return self.button_component.get_state()

    def get_buzzer_component_state(self):
        return self.buzzer_component.get_state()
    ################################################################

    def get_device_id(self):
        return self.device_id

    def get_device_state(self):
        return self.state

    def get_mute_alert_buzzer_state(self):
        return self.mute_alert_buzzer

    def toggle_button_component_state(self):
        self.button_component.toggle_state()
        button_state = self.button_component.get_state()
        # Update output component
        self.buzzer_component.set_state(button_state)
        # Update device state
        self.state = button_state

    def set_button_component_state(self, state_in):
        self.button_component.set_state(state_in)
        button_state = self.button_component.get_state()
        # Update output component
        self.buzzer_component.set_state(button_state)
        # Update device state
        self.state = button_state

    def set_mute_alert_buzzer(self, option):
        self.mute_alert_buzzer = option
        self.buzzer_component.set_mute_alert(option=option)

    # Info #########################################
    def get_metrics(self):
        metrics_dict = {
            'fire-button': [self.button_component.get_metrics()],
            'fire-buzzer': [self.buzzer_component.get_metrics()]
        }
        return metrics_dict

    def get_info(self):
        alert_device_info = [self.button_component.get_info(),
                             self.buzzer_component.get_info()]
        device_info_list = []
        for device_info in alert_device_info:
            if not device_info == {}:
                device_info_list.append(device_info)
        return device_info_list

    def get_battery_status(self):
        return self.battery_component.get_metrics()
