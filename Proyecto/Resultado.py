from listaEnlazadaSimple import ListaEnlazadaSimple

class ResultadoProducto:
    def __init__(self, nombre, cantidad_componentes, tiempo_total):
        self.nombre = nombre
        self.cantidad_componentes = cantidad_componentes
        self.tiempo_total = tiempo_total

class ResultadoMaquina:
    def __init__(self, nombre, cantidad_lineas):
        self.nombre = nombre
        self.cantidad_lineas = cantidad_lineas
        self.productos = ListaEnlazadaSimple()

    def agregar_producto(self, producto):
        self.productos.agregar(producto)