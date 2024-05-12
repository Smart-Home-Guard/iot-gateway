class OutputComponent:
    def __init__(self, feed_id=None, device_id=None, component_id=None, component_enable=False):
        self.feed_id = feed_id,
        self.device_id = device_id
        self.component_id = component_id
        self.state = 0
        self.access_lock = True
        self.component_enable = component_enable

    def get_state(self):
        return self.state

    def get_metrics(self):
        metrics = {}
        if self.component_enable:
            metrics = {
                'id': self.device_id,
                'component': self.component_id,
                'value': self.state
            }
        return metrics

    def get_info(self):
        info_dict = {}
        if self.component_enable:
            info_dict = {
                'id': self.device_id,
                'component': self.component_id
            }
        return info_dict

    def toggle_state(self):
        # Waiting for lock to be freed
        while self.access_lock == False:
            continue
        # Get the lock
        self.access_lock = False
        self.state = not self.state
        # Release the lock
        self.access_lock = True

    def set_state(self, state_in):
        # Waiting for lock to be freed
        while self.access_lock == False:
            continue
        # Get lock
        self.access_lock = False
        if state_in == 0:
            self.state = 0
        else:
            self.state = 1
        # Release the lock
        self.access_lock = True
