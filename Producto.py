from Componente import Componente

class Producto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.componentes = None

    def agregar_componente(self, linea, numero):
        nuevo_componente = Componente(linea, numero)
        if not self.componentes:
            self.componentes = nuevo_componente
        else:
            actual = self.componentes
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_componente