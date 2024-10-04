import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from Maquina import Maquina
from Producto import Producto
from listaEnlazadaSimple import ListaEnlazadaSimple
from listaEnlazadaDoble import ListaEnlazadaDoble
from Simulacion import Simulacion
from TiempoLinea import TiempoLinea
from Resultado import ResultadoMaquina, ResultadoProducto
import os



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key' 

productos_global = ListaEnlazadaSimple()
maquinas_global = ListaEnlazadaSimple()
resultados_global = None
tablas_ensamblaje = ListaEnlazadaSimple()  # Definir tablas_ensamblaje como una lista enlazada
elaboraciones_global = ListaEnlazadaSimple()


@app.route('/leer_xml', methods=['POST'])
def leer_xml(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        xml_content = file.read()
        if not xml_content:
            print("Empty file")
            return "Empty file"
        try:
            session['xml_content'] = xml_content  # Guardar el contenido XML en la sesión
            arbol = ET.ElementTree(ET.fromstring(xml_content))
            raiz = arbol.getroot()
        except ET.ParseError:
            print("Invalid XML file")
            return "Invalid XML file"
        
        for maquina_elem in raiz.findall('Maquina'):
            nombre_maquina = maquina_elem.find('NombreMaquina').text.strip()
            cantidad_lineas = int(maquina_elem.find('CantidadLineasProduccion').text.strip())
            cantidad_componentes = int(maquina_elem.find('CantidadComponentes').text.strip())
            tiempo_ensamblaje = int(maquina_elem.find('TiempoEnsamblaje').text.strip())
            
            print(f"Nombre de la máquina: {nombre_maquina}")
            print(f"Cantidad de líneas de producción: {cantidad_lineas}")
            print(f"Cantidad de componentes: {cantidad_componentes}")
            print(f"Tiempo de ensamblaje: {tiempo_ensamblaje}")
            
            # Guardar el tiempo de ensamblaje en la sesión
            session[f'{nombre_maquina}_tiempo_ensamblaje'] = tiempo_ensamblaje
            
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
                maquina = Maquina(nombre_maquina, cantidad_lineas, cantidad_componentes, tiempo_ensamblaje)
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
                    # Agregar la línea de elaboración a la lista global
                    elaboraciones_global.agregar(f"Línea: {linea}, Número: {numero}")
                    print(f"Guardado exitosamente: Línea: {linea}, Número: {numero}")
                
                maquina.agregar_producto(producto)
                productos_global.agregar(producto)
        
        print("XML leído y procesado correctamente")
        return "XML leído y procesado correctamente"

def calcular_tiempo_ensamblaje(producto, cantidad_lineas):
    tiempos_lineas = ListaEnlazadaSimple()
    for i in range(cantidad_lineas):
        tiempos_lineas.agregar(TiempoLinea(i + 1))
    
    nodo_componente = producto.componentes.cabeza
    while nodo_componente is not None:
        nodo_tiempo = tiempos_lineas.obtener(nodo_componente.dato.linea - 1)
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
    productos = productos_global  # Inicializar productos con la estructura de datos personalizada
    num_lineas = 0
    if request.method == 'POST':
        if 'file' not in request.files:
            print("No file part in the request")
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            print("No selected file")
            return redirect(url_for('index'))
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            mensaje = leer_xml(filepath)  # Llamada a leer_xml con el argumento filepath
            if mensaje != "XML leído y procesado correctamente":
                print(f"Error: {mensaje}")
                return render_template('index.html', message=mensaje, resultados=resultados, productos=productos, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)
            resultados = mostrar_resultados(maquinas_global)
            imprimir_resultados(resultados)
            resultados_global = resultados
            productos = productos_global  # Asignar productos_global a productos
            return render_template('index.html', resultados=resultados, productos=productos, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje)
    return render_template('index.html', resultados=None, productos=productos, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje, num_lineas=num_lineas)

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
    
    return render_template('index.html', productos=productos_maquina, resultados=resultados_global, maquinas=maquinas_global, tablas_ensamblaje=tablas_ensamblaje, maquina_seleccionada=maquina_nombre)
    
class Resultado:
    def __init__(self, dato, lineas):
        self.dato = dato
        self.lineas = lineas
    def longitud(self):
        return self.lineas.longitud()
    def __str__(self):
        return f"Resultado(dato={self.dato}, lineas={self.lineas})"

    def __repr__(self):
        return self.__str__()

def obtener_linea_y_componente(nodo):
    # Asumiendo que el dato del nodo tiene el formato "LíneaXComponenteY" (por ejemplo, "L2C3")
    instruccion = nodo.dato  # Acceder al dato del nodo
    linea = int(instruccion[1])  # Extraer el número de línea (segundo carácter)
    componente = int(instruccion[3])  # Extraer el número de componente (cuarto carácter)
    return linea, componente

@app.route('/simular_producto', methods=['POST'])
def simular_producto():
    maquina_seleccionada = request.form.get('maquina')
    producto_seleccionado = request.form.get('producto')
    resultados = ListaEnlazadaSimple()

    # Mostrar en consola los valores recibidos del formulario
    print(f"Máquina seleccionada desde el formulario: {maquina_seleccionada}")
    print(f"Producto seleccionado desde el formulario: {producto_seleccionado}")

    if not maquina_seleccionada or not producto_seleccionado:
        print("No se seleccionó una máquina o un producto.")
        return render_template('index.html', message='Por favor, seleccione una máquina y un producto.', resultados=ListaEnlazadaSimple(), num_lineas=0, tablas_ensamblaje=tablas_ensamblaje)

    if 'xml_content' not in session:
        print("No se encontró contenido XML en la sesión.")
        return render_template('index.html', message='Por favor, carga un archivo XML primero.', resultados=ListaEnlazadaSimple(), num_lineas=0, tablas_ensamblaje=tablas_ensamblaje)

    xml_content = session['xml_content']
    root = ET.fromstring(xml_content)

    num_lineas = 0  # Inicializar num_lineas
    tiempo_ensamblaje = 0  # Inicializar tiempo de ensamblaje
    for maquina in root.findall('Maquina'):
        nombre_maquina = maquina.find('NombreMaquina').text
        if nombre_maquina == maquina_seleccionada:
            num_lineas = int(maquina.find('CantidadLineasProduccion').text)
            tiempo_ensamblaje = int(maquina.find('TiempoEnsamblaje').text)
            print(f"Máquina encontrada: {nombre_maquina} con {num_lineas} líneas de producción.")
            print(f"Tiempo de ensamblaje: {tiempo_ensamblaje}")

            for producto in maquina.find('ListadoProductos').findall('Producto'):
                nombre_producto = producto.find('nombre').text
                if nombre_producto == producto_seleccionado:
                    elaboracion = producto.find('elaboracion').text.strip()
                    print(f"Producto encontrado: {nombre_producto} con elaboración: {elaboracion}")
                    
                    # Extraer las instrucciones correctamente
                    instrucciones = ListaEnlazadaSimple()
                    pasos = elaboracion.split()
                    for paso in pasos:
                        instrucciones.agregar(paso)
                    
                    brazos = ListaEnlazadaSimple()
                    for _ in range(num_lineas):
                        brazos.agregar(0)
                    
                    segundo = 1
                    ensamblando_lineas = [0] * num_lineas  # Inicializar el tiempo de ensamblaje para cada línea
                    while True:
                        fila_tiempo = Resultado(f"{segundo}", ListaEnlazadaSimple())
                        for _ in range(num_lineas):
                            fila_tiempo.lineas.agregar("No hacer nada")
                        
                        ensamblaje_realizado = False
                        ensamblando = any(ensamblando_lineas)  # Verificar si alguna línea está ensamblando
                        
                        for linea in range(num_lineas):
                            if ensamblando_lineas[linea] > 0:
                                fila_tiempo.lineas.actualizar(linea, f"Ensamblar componente {brazos.obtener(linea).dato}")
                                ensamblando_lineas[linea] -= 1
                                ensamblando = True
                            else:
                                instruccion_actual = None
                                for i in range(instrucciones.longitud()):
                                    if instrucciones.obtener(i).dato != "COMPLETED":
                                        linea_instruccion, componente_instruccion = instrucciones.obtener(i).dato[1:].split('C')
                                        linea_instruccion = int(linea_instruccion)
                                        componente_instruccion = int(componente_instruccion)
                                        if linea_instruccion - 1 == linea:
                                            instruccion_actual = instrucciones.obtener(i)
                                            instruccion_index = i
                                            break
                                
                                if instruccion_actual:
                                    _, componente_actual = instruccion_actual.dato[1:].split('C')
                                    componente_actual = int(componente_actual)
                                    brazo_actual = brazos.obtener(linea).dato
                                    
                                    if ensamblando and brazo_actual == componente_actual:
                                        fila_tiempo.lineas.actualizar(linea, "No hace nada")
                                    elif brazo_actual < componente_actual:
                                        brazo_actual += 1
                                        fila_tiempo.lineas.actualizar(linea, f"Mover brazo – componente {brazo_actual}")
                                        brazos.obtener(linea).dato = brazo_actual
                                    elif brazo_actual > componente_actual:
                                        # No permitir decremento de componentes
                                        fila_tiempo.lineas.actualizar(linea, "No hace nada")
                                    elif brazo_actual == componente_actual and not ensamblaje_realizado and not ensamblando:
                                        # Verificar si es el turno de esta instrucción
                                        can_assemble = True
                                        for j in range(instruccion_index):
                                            if instrucciones.obtener(j).dato != "COMPLETED":
                                                can_assemble = False
                                                break
                                        
                                        if can_assemble:
                                            fila_tiempo.lineas.actualizar(linea, f"Ensamblar componente {componente_actual}")
                                            instrucciones.obtener(instruccion_index).dato = "COMPLETED"
                                            ensamblaje_realizado = True
                                            ensamblando = True  # Marcar que una línea está ensamblando
                                            ensamblando_lineas[linea] = tiempo_ensamblaje - 1  # Establecer el tiempo de ensamblaje para la línea
                        
                        # Actualizar las líneas que no están haciendo nada a "No hace nada" si alguna línea está ensamblando
                        if ensamblando:
                            for linea in range(num_lineas):
                                if fila_tiempo.lineas.obtener(linea).dato == "No hacer nada":
                                    fila_tiempo.lineas.actualizar(linea, "No hace nada")
                        
                        resultados.agregar(fila_tiempo)
                        
                        all_completed = True
                        for i in range(instrucciones.longitud()):
                            if instrucciones.obtener(i).dato != "COMPLETED":
                                all_completed = False
                                break
                        
                        if all_completed:
                            break
                        
                        segundo += 1  # Incrementar el tiempo en 1 segundo

                    # Asegurarse de que el último componente también reciba el tiempo de ensamblaje
                    if ensamblaje_realizado:
                        for linea in range(num_lineas):
                            if ensamblando_lineas[linea] == 0 and fila_tiempo.lineas.obtener(linea).dato.startswith("Ensamblar componente"):
                                ensamblando_lineas[linea] = tiempo_ensamblaje - 1

    # Mostrar los pasos de la simulación en la consola
    print("Pasos de la simulación:")
    nodo_actual = resultados.cabeza
    while nodo_actual:
        print(nodo_actual.dato)
        nodo_actual = nodo_actual.siguiente

    # Agregar la tabla de ensamblaje a la lista de tablas
    tablas_ensamblaje.agregar((producto_seleccionado, resultados))

    print("Simulación completada. Resultados generados.")
    return render_template('index.html', productos=productos_global, resultados=resultados, maquinas=maquinas_global, num_lineas=num_lineas, tablas_ensamblaje=tablas_ensamblaje)
@app.route('/reporte_html/<producto>', methods=['GET'])
def reporte_html(producto):
    # Buscar la tabla de ensamblaje correspondiente al producto
    for nombre_producto, resultados in tablas_ensamblaje:
        if nombre_producto == producto:
            # Generar el HTML a partir de los resultados
            html_content = f"""
            <html>
            <head>
                <title>Reporte de Ensamblaje</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f0;
                        color: #333;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .container {{
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        max-width: 800px;
                        width: 100%;
                    }}
                    h1 {{
                        text-align: center;
                        color: #444;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        color: #333;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    tr:hover {{
                        background-color: #f1f1f1;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Reporte de Ensamblaje para {producto}</h1>
                    <table>
                        <tr><th>Tiempo</th>"""

            # Añadir encabezados de las líneas de ensamblaje
            if resultados.cabeza:
                primera_fila = resultados.cabeza.dato
                for i in range(primera_fila.lineas.longitud()):
                    html_content += f"<th>Línea de Ensamblaje {i + 1}</th>"
            html_content += "</tr>"

            # Añadir filas de resultados
            nodo_actual = resultados.cabeza
            while nodo_actual:
                html_content += f"<tr><td>{nodo_actual.dato.dato}</td>"
                for i in range(nodo_actual.dato.lineas.longitud()):
                    html_content += f"<td>{nodo_actual.dato.lineas.obtener(i).dato}</td>"
                html_content += "</tr>"
                nodo_actual = nodo_actual.siguiente

            html_content += """
                    </table>
                </div>
            </body>
            </html>
            """

            # Guardar el HTML en un archivo
            with open(f"reporte_{producto}.html", "w") as file:
                file.write(html_content)

            return html_content

    return "Producto no encontrado", 404

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
