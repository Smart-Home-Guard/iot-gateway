class BatteryComponent:
    def __init__(self, device_id=None, component_id=None, rate_capacity=None):
        self.device_id = device_id
        self.component_id = component_id
        self.rate_capacity = rate_capacity

    def get_rate_capacity(self):
        return self.rate_capacity

    def get_metrics(self):
        metrics_dict = {
            'id': self.device_id,
            'value': self.rate_capacity
        }
        return metrics_dict
