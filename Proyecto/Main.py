import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from Maquina import Maquina
from Producto import Producto
from listaEnlazadaSimple import ListaEnlazadaSimple
from Simulacion import Simulacion

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

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

@app.route('/', methods=['GET', 'POST'])
def index():
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
            return redirect(url_for('iniciar_simulacion', ruta_archivo=filepath))
    return render_template('index.html', resultados=resultados)

@app.route('/simulacion')
def iniciar_simulacion():
    ruta_archivo = request.args.get('ruta_archivo')
    
    if not ruta_archivo:
        return redirect(url_for('index'))
    
    # Leer el archivo XML y obtener las máquinas
    maquinas = leer_xml(ruta_archivo)

    # Ejecutar la simulación para cada máquina y sus productos
    resultados = ListaEnlazadaSimple()
    for maquina in maquinas:
        for producto in maquina.productos:
            simulacion = Simulacion(maquina, producto)
            simulacion.iniciar_simulacion()
            log = ListaEnlazadaSimple()
            for accion in simulacion.log:
                log.agregar(accion)
            resultado = {
                "maquina": maquina.nombre,
                "producto": producto.nombre,
                "log": log
            }
            resultados.agregar(resultado)
    
    return render_template('index.html', resultados=resultados)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)