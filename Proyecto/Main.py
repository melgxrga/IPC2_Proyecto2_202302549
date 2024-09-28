import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from Maquina import Maquina
from Producto import Producto
from listaEnlazadaSimple import ListaEnlazadaSimple
from listaEnlazadaDoble import ListaEnlazadaDoble
from Simulacion import Simulacion
from TiempoLinea import TiempoLinea
from Resultado import ResultadoMaquina, ResultadoProducto

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

productos_global = ListaEnlazadaSimple()
maquinas_global = ListaEnlazadaSimple()
resultados_global = None
tablas_ensamblaje = ListaEnlazadaSimple()  # Definir tablas_ensamblaje como una lista enlazada

def leer_xml(ruta_archivo):
    arbol = ET.parse(ruta_archivo)
    raiz = arbol.getroot()
    
    for maquina_elem in raiz.findall('Maquina'):
        nombre_maquina = maquina_elem.find('NombreMaquina').text.strip()
        cantidad_lineas = int(maquina_elem.find('CantidadLineasProduccion').text.strip())
        cantidad_componentes = int(maquina_elem.find('CantidadComponentes').text.strip())
        tiempo_ensamblaje = int(maquina_elem.find('TiempoEnsamblaje').text.strip())
        
        print(f"Nombre de la máquina: {nombre_maquina}")
        print(f"Cantidad de líneas de producción: {cantidad_lineas}")
        print(f"Cantidad de componentes: {cantidad_componentes}")
        print(f"Tiempo de ensamblaje: {tiempo_ensamblaje}")
        
        # Buscar si la máquina ya existe
        maquina_existente = None
        nodo_maquina = maquinas_global.cabeza
        while nodo_maquina is not None:
            if nodo_maquina.dato.nombre == nombre_maquina:
                maquina_existente = nodo_maquina.dato
                break
            nodo_maquina = nodo_maquina.siguiente
        
        if maquina_existente:
            maquina = maquina_existente
        else:
            maquina = Maquina(nombre_maquina, cantidad_lineas)
            maquinas_global.agregar(maquina)
        
        for producto_elem in maquina_elem.find('ListadoProductos').findall('Producto'):
            nombre_producto = producto_elem.find('nombre').text.strip()
            elaboracion = producto_elem.find('elaboracion').text.strip().split()
            
            print(f"  Nombre del producto: {nombre_producto}")
            print(f"  Elaboración: {elaboracion}")
            
            producto = Producto(nombre_producto)
            for componente in elaboracion:
                linea, numero = map(int, componente[1:].split('C'))
                producto.agregar_componente(linea, numero)
            
            maquina.agregar_producto(producto)
            productos_global.agregar(producto)

def calcular_tiempo_ensamblaje(producto, cantidad_lineas):
    tiempos_lineas = ListaEnlazadaSimple()
    for i in range(cantidad_lineas):
        tiempos_lineas.agregar(TiempoLinea(i + 1))
    
    nodo_componente = producto.componentes.cabeza
    while nodo_componente is not None:
        nodo_tiempo = tiempos_lineas.buscar(nodo_componente.dato.linea - 1)
        if nodo_tiempo is not None:
            nodo_tiempo.dato.incrementar_tiempo()
        nodo_componente = nodo_componente.siguiente
    
    max_tiempo = 0
    nodo_tiempo = tiempos_lineas.cabeza
    while nodo_tiempo is not None:
        if nodo_tiempo.dato.tiempo > max_tiempo:
            max_tiempo = nodo_tiempo.dato.tiempo
        nodo_tiempo = nodo_tiempo.siguiente
    
    return max_tiempo

def mostrar_resultados(maquinas):
    resultados = ListaEnlazadaSimple()
    nodo_maquina = maquinas.cabeza
    while nodo_maquina is not None:
        maquina = nodo_maquina.dato
        maquina_info = ResultadoMaquina(maquina.nombre, maquina.cantidad_lineas)
        nodo_producto = maquina.productos.cabeza
        while nodo_producto is not None:
            producto = nodo_producto.dato
            tiempo_total = calcular_tiempo_ensamblaje(producto, maquina.cantidad_lineas)
            producto_info = ResultadoProducto(producto.nombre, producto.componentes.longitud(), tiempo_total)
            maquina_info.agregar_producto(producto_info)
            nodo_producto = nodo_producto.siguiente
        resultados.agregar(maquina_info)
        nodo_maquina = nodo_maquina.siguiente
    return resultados

def imprimir_resultados(resultados):
    nodo_maquina = resultados.cabeza
    while nodo_maquina is not None:
        maquina = nodo_maquina.dato
        print(f"Maquina: {maquina.nombre}")
        print(f"Cantidad de líneas de producción: {maquina.cantidad_lineas}")
        nodo_producto = maquina.productos.cabeza
        while nodo_producto is not None:
            producto = nodo_producto.dato
            print(f"  Producto: {producto.nombre}")
            print(f"  Cantidad de componentes: {producto.cantidad_componentes}")
            print(f"  Tiempo total de ensamblaje: {producto.tiempo_total} segundos")
            nodo_producto = nodo_producto.siguiente
        nodo_maquina = nodo_maquina.siguiente

@app.route('/', methods=['GET', 'POST'])
def index():
    global resultados_global
    resultados = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('index'))
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            leer_xml(filepath)
            resultados = mostrar_resultados(maquinas_global)
            imprimir_resultados(resultados)
            resultados_global = resultados
            return render_template('index.html', resultados=resultados, productos=None, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)
    return render_template('index.html', productos=None, resultados=resultados_global, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)

@app.route('/filtrar_maquina', methods=['POST'])
def filtrar_maquina():
    maquina_nombre = request.form.get('maquina')
    maquina_seleccionada = None
    
    nodo_maquina = maquinas_global.cabeza
    while nodo_maquina is not None:
        if nodo_maquina.dato.nombre == maquina_nombre:
            maquina_seleccionada = nodo_maquina.dato
            break
        nodo_maquina = nodo_maquina.siguiente
    
    productos_maquina = ListaEnlazadaSimple()
    if maquina_seleccionada:
        nodo_producto = maquina_seleccionada.productos.cabeza
        while nodo_producto is not None:
            productos_maquina.agregar(nodo_producto.dato)
            nodo_producto = nodo_producto.siguiente
    
    return render_template('index.html', productos=productos_maquina, resultados=resultados_global, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)
@app.route('/simular_producto', methods=['POST'])
def simular_producto():
    global tablas_ensamblaje
    producto_nombre = request.form.get('producto')
    producto_seleccionado = None
    
    print(f"Simulando producto: {producto_nombre}")

    nodo_producto = productos_global.cabeza
    while nodo_producto is not None:
        if nodo_producto.dato.nombre == producto_nombre:
            producto_seleccionado = nodo_producto.dato
            break
        nodo_producto = nodo_producto.siguiente
    
    if producto_seleccionado:
        print(f"Producto seleccionado: {producto_seleccionado.nombre}")
        
        cantidad_lineas = 0
        nodo_componente = producto_seleccionado.componentes.cabeza
        while nodo_componente is not None:
            if nodo_componente.dato.linea > cantidad_lineas:
                cantidad_lineas = nodo_componente.dato.linea
            nodo_componente = nodo_componente.siguiente
        
        print(f"Cantidad de líneas: {cantidad_lineas}")
        
        tiempos_lineas = ListaEnlazadaSimple()
        for i in range(cantidad_lineas):
            tiempos_lineas.agregar(TiempoLinea(i + 1))
        
        tabla_ensamblaje = ListaEnlazadaSimple()
        pasos = ListaEnlazadaSimple()
        brazos = ListaEnlazadaSimple()  # Inicializar los brazos en el componente 1

        for i in range(cantidad_lineas):
            brazos.agregar(1)

        print("Estado inicial de los brazos:")
        nodo_brazo = brazos.cabeza
        while nodo_brazo is not None:
            print(f"Línea {nodo_brazo.dato} - Componente 1")
            nodo_brazo = nodo_brazo.siguiente

        # Agregar el componente inicial a la lista de pasos
        for i in range(1, cantidad_lineas + 1):
            pasos.agregar((i, 1))

        nodo_componente = producto_seleccionado.componentes.cabeza
        while nodo_componente is not None:
            pasos.agregar((nodo_componente.dato.linea, nodo_componente.dato.numero))
            nodo_componente = nodo_componente.siguiente

        print("Pasos de ensamblaje:")
        nodo_paso = pasos.cabeza
        while nodo_paso is not None:
            print(nodo_paso.dato)
            nodo_paso = nodo_paso.siguiente

        tiempo_actual = 1  # Iniciar el tiempo en 1
        while pasos.cabeza is not None:
            fila = ListaEnlazadaSimple()
            fila.agregar(tiempo_actual)
            for i in range(cantidad_lineas):
                fila.agregar("No hace nada")
            tabla_ensamblaje.agregar(fila)

            nodo_paso = pasos.cabeza
            while nodo_paso is not None:
                linea, componente = nodo_paso.dato
                nodo_brazo = brazos.buscar(linea - 1)
                
                # Mover brazo secuencialmente al componente deseado
                while nodo_brazo.dato != componente:
                    if nodo_brazo.dato < componente:
                        nodo_brazo.dato += 1
                    else:
                        nodo_brazo.dato -= 1
                    print(f"Tiempo {tiempo_actual}: Línea {linea} - Mover brazo a componente {nodo_brazo.dato}")
                    nodo_fila = fila.buscar(linea)
                    if nodo_fila is not None:
                        nodo_fila.dato = f"Mover brazo a componente {nodo_brazo.dato}"
                    tiempo_actual += 1
                    fila = ListaEnlazadaSimple()
                    fila.agregar(tiempo_actual)
                    for i in range(cantidad_lineas):
                        fila.agregar("No hace nada")
                    tabla_ensamblaje.agregar(fila)
                
                # Asegurarse de ensamblar solo cuando esté en el componente deseado
                if nodo_brazo.dato == componente:
                    print(f"Tiempo {tiempo_actual}: Línea {linea} - Ensamblar en componente {componente}")
                    nodo_fila = fila.buscar(linea)
                    if nodo_fila is not None:
                        nodo_fila.dato = f"Ensamblar en componente {componente}"
                    pasos.eliminar(nodo_paso.dato)
                nodo_paso = nodo_paso.siguiente

        print(f"Simulación para {producto_nombre} completada.")
        print(f"  Tiempo total de ensamblaje: {tiempo_actual} segundos")
        
        # Agregar la tabla de ensamblaje a la lista de tablas
        tablas_ensamblaje.agregar((producto_nombre, tabla_ensamblaje))
    
    return render_template('index.html', productos=productos_global, resultados=resultados_global, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

    class Componente:
        def __init__(self, linea, numero):
            self.linea = linea
            self.numero = numero
    
    class PasoEnsamblaje:
        def __init__(self, linea, componente):
            self.linea = linea
            self.componente = componente