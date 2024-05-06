from Components.ButtonComponent import *
from Components.OutputComponent import *


class AlertDevice:
    def __init__(self, device_id=None, button_component=ButtonComponent(), light_component=OutputComponent(),
                 buzzer_component=OutputComponent()):
        self.device_id = device_id
        self.button_component = button_component
        self.light_component = light_component
        self.buzzer_component = buzzer_component
        self.state = 0   # (1-'alert' / 0-'safe')

    #################################################################

    def get_button_component_state(self):
        return self.button_component.get_state()

    def get_light_component_state(self):
        return self.light_component.get_state()

    def get_buzzer_component_state(self):
        return self.buzzer_component.get_state()
    ################################################################

    def set_light_component_state(self, value):
        self.light_component.set_state(state_in=value)
        # Both the light and the buzzer are turned off -> Turn off the button
        if self.buzzer_component.get_state() == 0:
            self.button_component.set_state(0)
            self.state = 0

    def set_buzzer_component_state(self, value):
        self.buzzer_component.set_state(state_in=value)
        # Both the light and the buzzer are turned off -> Turn off the button
        if self.light_component.get_state() == 0:
            self.button_component.set_state(0)
            self.state = 0

    def get_device_id(self):
        return self.device_id

    def get_device_state(self):
        return self.state

    def toggle_button_component_state(self):
        self.button_component.toggle_state()
        button_state = self.button_component.get_state()
        # Update output component
        self.light_component.set_state(button_state)
        self.buzzer_component.set_state(button_state)
        # Update device state
        self.state = button_state

    def get_metrics(self):
        metrics_dict = {
            'button': self.button_component.get_metrics(),
            'light': self.light_component.get_metrics(),
            'buzzer': self.buzzer_component.get_metrics()
        }
        return metrics_dict

    def get_info(self):
        alert_device_info = [self.button_component.get_info(),
                             self.light_component.get_info(),
                             self.buzzer_component.get_info()]
        return alert_device_info
