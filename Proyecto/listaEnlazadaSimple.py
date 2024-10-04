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

    def longitud(self):
        actual = self.cabeza
        contador = 0
        while actual:
            contador += 1
            actual = actual.siguiente
        return contador

    def obtener(self, indice):
        actual = self.cabeza
        contador = 0
        while actual:
            if contador == indice:
                return actual
            contador += 1
            actual = actual.siguiente
        return None

    def actualizar(self, indice, dato):
        actual = self.cabeza
        contador = 0
        while actual:
            if contador == indice:
                actual.dato = dato
                return
            contador += 1
            actual = actual.siguiente

    def __str__(self):
        resultado = ""
        actual = self.cabeza
        while actual:
            resultado += str(actual.dato) + " -> "
            actual = actual.siguiente
        return resultado.strip(" -> ")
    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente