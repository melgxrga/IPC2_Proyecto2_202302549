from listaEnlazadaSimple import ListaEnlazadaSimple

class Simulacion:
    def __init__(self, maquina, producto):
        self.maquina = maquina
        self.producto = producto
        self.tiempo_actual = 0
        self.log = ListaEnlazadaSimple()

    def iniciar_simulacion(self):
        componente_actual = self.producto.componentes
        while componente_actual:
            self.ejecutar_segundo(componente_actual)
            componente_actual = componente_actual.siguiente

    def ejecutar_segundo(self, componente):
        # Lógica para mover brazos y ensamblar componentes
        # Actualizar el log con las acciones realizadas
        accion = f"Segundo {self.tiempo_actual + 1}: Ensamblar componente {componente.linea}C{componente.numero} en línea {componente.linea}  {self.producto.nombre}"
        self.log.agregar(accion)
        self.tiempo_actual += 1

    def generar_log(self):
        for i in range(self.log.longitud()):
            print(self.log.obtener(i))