class Brazo:
    def __init__(self, linea):
        self.posicion_actual = 0
        self.linea = linea
        self.estado = "inactivo"

class LineaEnsamblaje:
    def __init__(self, numero):
        self.numero = numero
        self.brazo = Brazo(numero)
