from listaEnlazadaSimple import ListaEnlazadaSimple

class Producto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.componentes = ListaEnlazadaSimple()

    def agregar_componente(self, linea, numero):
        self.componentes.agregar(Componente(linea, numero))

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f'Producto({self.nombre})'

class Componente:
    def __init__(self, linea, numero):
        self.linea = linea
        self.numero = numero
        
    def __str__(self):
        return f'Componente({self.linea}, {self.numero})'

    def __repr__(self):
        return f'Componente({self.linea}, {self.numero})'