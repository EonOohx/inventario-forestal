class ObservableBool:
    def __init__(self, initial_value=False):
        self._value = initial_value
        self._prev_value = initial_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._prev_value = self._value
            self._value = new_value

    def has_changed(self):
        return self._value != self._prev_value
