class OutputComponent:
    def __init__(self, feed_id=None, device_id=None, kind=0, component_id=None, component_enable=False):
        self.feed_id = feed_id,
        self.device_id = device_id
        self.kind = kind
        self.component_id = component_id
        self.mute_alert = 0
        self.state = 0
        self.access_lock = True
        self.component_enable = component_enable

    def get_state(self):
        return int((not self.mute_alert) and self.state)

    def get_component_id(self):
        return self.component_id

    def get_metrics(self):
        metrics = {}
        if self.component_enable:
            metrics = {
                'id': self.device_id,
                'component': self.component_id,
                'value': int((not self.mute_alert) and self.state),
                'alert': int((not self.mute_alert) and self.state)
            }
        return metrics

    def get_info(self):
        info_dict = {}
        if self.component_enable:
            info_dict = {
                'id': self.device_id,
                'kind': self.kind,
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

    def set_mute_alert(self, option):
        if option:
            self.mute_alert = 1
        else:
            self.mute_alert = 0
