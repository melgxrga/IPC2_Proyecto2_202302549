from listaEnlazadaSimple import ListaEnlazadaSimple

class Producto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.componentes = ListaEnlazadaSimple()

    def agregar_componente(self, linea, numero):
        self.componentes.agregar(Componente(linea, numero))

class Componente:
    def __init__(self, linea, numero):
        self.linea = linea
        self.numero = numero