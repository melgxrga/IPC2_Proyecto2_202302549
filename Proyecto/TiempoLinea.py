class TiempoLinea:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo = 0
        self.dato = None  # Añadimos el atributo 'dato'

    def incrementar_tiempo(self):
        self.tiempo += 1