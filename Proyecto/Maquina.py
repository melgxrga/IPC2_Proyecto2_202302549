from listaEnlazadaSimple import ListaEnlazadaSimple

class Maquina:
    def __init__(self, nombre, cantidad_lineas):
        self.nombre = nombre
        self.cantidad_lineas = cantidad_lineas
        self.productos = ListaEnlazadaSimple()

    def agregar_producto(self, producto):
        self.productos.agregar(producto)