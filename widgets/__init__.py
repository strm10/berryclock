class WidgetBase:
    def __init__(self, settings, expected_size):
        self.settings = settings
        self.expected_size = expected_size

    def draw(self):
        raise NotImplementedError()
