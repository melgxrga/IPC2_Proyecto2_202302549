import xml.etree.ElementTree as ET
import argparse
from Maquina import Maquina
from Producto import Producto
from listaEnlazadaSimple import ListaEnlazadaSimple
from Simulacion import Simulacion

def leer_xml(ruta_archivo):
    arbol = ET.parse(ruta_archivo)
    raiz = arbol.getroot()
    
    maquinas = ListaEnlazadaSimple()
    
    for maquina_elem in raiz.findall('Maquina'):
        nombre_maquina = maquina_elem.find('NombreMaquina').text
        cantidad_lineas = int(maquina_elem.find('CantidadLineasProduccion').text)
        maquina = Maquina(nombre_maquina, cantidad_lineas)
        
        for producto_elem in maquina_elem.find('ListadoProductos').findall('Producto'):
            nombre_producto = producto_elem.find('nombre').text
            elaboracion = producto_elem.find('elaboracion').text.strip().split()
            
            producto = Producto(nombre_producto)
            for componente in elaboracion:
                linea, numero = map(int, componente[1:].split('C'))
                producto.agregar_componente(linea, numero)
            
            maquina.agregar_producto(producto)
        
        maquinas.agregar(maquina)
    
    return maquinas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulación de máquinas de ensamblaje.")
    parser.add_argument("ruta_archivo", help="Ruta del archivo XML con la configuración de las máquinas.")
    args = parser.parse_args()

    # Leer el archivo XML y obtener las máquinas
    maquinas = leer_xml(args.ruta_archivo)

    # Ejecutar la simulación para cada máquina y sus productos
    for i in range(maquinas.longitud()):
        maquina = maquinas.obtener(i)
        for j in range(maquina.productos.longitud()):
            producto = maquina.productos.obtener(j)
            simulacion = Simulacion(maquina, producto)
            simulacion.iniciar_simulacion()
            simulacion.generar_log()