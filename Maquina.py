from Brazo import LineaEnsamblaje
from listaEnlazadaSimple import ListaEnlazadaSimple

class Maquina:
    def __init__(self, nombre, n_lineas):
        self.nombre = nombre
        self.lineas = [LineaEnsamblaje(i+1) for i in range(n_lineas)]
        self.productos = ListaEnlazadaSimple()
        self.tiempo_total = 0

    def agregar_producto(self, producto):
        self.productos.agregar(producto)
