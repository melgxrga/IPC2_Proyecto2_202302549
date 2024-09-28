from listaEnlazadaDoble import ListaEnlazadaDoble

class Simulacion:
    def __init__(self, maquina, producto):
        self.maquina = maquina
        self.producto = producto
        self.tiempos_lineas = [0] * self.maquina.cantidad_lineas  # Inicializar tiempos de líneas
        self.log = ListaEnlazadaDoble()

    def iniciar_simulacion(self):
        for componente in self.producto.componentes:
            self.ejecutar_segundo(componente)

    def ejecutar_segundo(self, componente):
        # Encontrar la línea con el menor tiempo acumulado
        linea_menor_tiempo = self.tiempos_lineas.index(min(self.tiempos_lineas))
        self.tiempos_lineas[linea_menor_tiempo] += 1  # Incrementar el tiempo de la línea seleccionada
        accion = f"Segundo {self.tiempos_lineas[linea_menor_tiempo]}: Ensamblar componente {componente.linea}C{componente.numero} en línea {linea_menor_tiempo + 1} {self.producto.nombre}"
        self.log.agregar(accion)