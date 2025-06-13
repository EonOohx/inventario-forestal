class ObservableBool:
    def __init__(self, valor_inicial=False):
        self.valor = valor_inicial
        self.valor_prev = valor_inicial

    @property
    def value(self):
        return self.valor

    @value.setter
    def value(self, nuevo_valor):
        if nuevo_valor != self.valor:
            self.valor_prev = self.valor
            self.valor = nuevo_valor

    def has_changed(self):
        return self.valor != self.valor_prev
