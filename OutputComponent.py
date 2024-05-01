class OutputComponent:
    def __init__(self, feed_id, device_id, component_id):
        self.feed_id = feed_id,
        self.device_id = device_id
        self.component_id = component_id
        self.state = False

    def get_state(self):
        return self.state

    def get_metrics(self):
        metrics = {
            'id': self.device_id,
            # Todo: Có tách `component` ra thành `type` và 'component` không?
            # 'type': self
        }

    def set_state(self, state_in):
        if state_in == 0:
            self.state = False
        else:
            self.state = True
