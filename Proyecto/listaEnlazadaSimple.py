class TiempoLinea:
    def __init__(self, linea):
        self.linea = linea
        self.tiempo = 0

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazadaSimple:
    def __init__(self):
        self.cabeza = None

    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def obtener(self, indice):
        actual = self.cabeza
        for _ in range(indice):
            if actual is None:
                return None
            actual = actual.siguiente
        return actual

    def eliminar(self, dato):
        actual = self.cabeza
        anterior = None
        while actual and actual.dato != dato:
            anterior = actual
            actual = actual.siguiente
        if anterior is None:
            self.cabeza = actual.siguiente
        elif actual:
            anterior.siguiente = actual.siguiente

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def longitud(self):
        actual = self.cabeza
        contador = 0
        while actual:
            contador += 1
            actual = actual.siguiente
        return contador

    def actualizar(self, indice, nuevo_dato):
        actual = self.cabeza
        for _ in range(indice):
            if actual is None:
                return False
            actual = actual.siguiente
        if actual is not None:
            actual.dato = nuevo_dato
            return True
        return False