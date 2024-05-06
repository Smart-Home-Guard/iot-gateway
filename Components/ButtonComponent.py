class ButtonComponent:
    def __init__(self, feed_id=None, device_id=None, component_id=None, component_status=False):
        self.feed_id = feed_id,
        self.device_id = device_id
        self.component_id = component_id
        self.state = 0
        self.component_status = component_status

    def get_state(self):
        return self.state

    def get_metrics(self):
        metrics = {}
        if self.component_status:
            metrics = {
                'id': self.device_id,
                'component': self.component_id,
                'value': self.state
            }
        return metrics

    def get_info(self):
        info_dict = {}
        if self.component_status:
            info_dict = {
                'id': self.device_id,
                'component': self.component_id
            }
        return info_dict

    def toggle_state(self):
        self.state = not self.state

    def set_state(self, state_in):
        if state_in == 0:
            self.state = 0
        else:
            self.state = 1
