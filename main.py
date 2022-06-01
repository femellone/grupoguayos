import base64
from flask import Flask, jsonify, request,  render_template
from config import config
from models import db, Bache
import folium
from folium import IFrame
from folium.plugins import MarkerCluster

def create_app(enviroment):
    app = Flask(__name__)

    app.config.from_object(enviroment)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    return app

enviroment = config['development']

app = create_app(enviroment)



@app.route('/')
def index():
    return render_template('index.html')

# Traer todos los baches
@app.route('/api/v1/baches', methods=['GET'])
def get_baches():
    baches = [ bache.json() for bache in Bache.query.all() ]
    return jsonify({'baches': baches })


# Traer un bache
@app.route('/api/v1/baches/<id>', methods=['GET'])
def get_bache(id):
    bache = Bache.query.filter_by(id=id).first()
    if bache is None:
        return jsonify({'message': 'El bache existe más :\'D'}), 404

    return jsonify({'bache': bache.json() })

# Crear un bache
@app.route('/api/v1/baches/', methods=['POST'])
def create_bache():
    body_diccionario = request.form

    bache = Bache.create(direccion=body_diccionario['direccion'], categoria=body_diccionario['categoria'], latitud=body_diccionario['latitud'], longitud=body_diccionario['longitud'], nombre_bache=body_diccionario['nombre_bache'], nombre_usuario=body_diccionario['nombre_usuario'])

    return render_template('index.html', bache= bache)

# Borrar un bache
@app.route('/api/v1/baches/<id>', methods=['DELETE'])
def delete_bache(id):
    bache = Bache.query.filter_by(id=id).first()
    if bache is None:
        return jsonify({'message': 'El bache no existe más :\'D'}), 404

    bache.delete()

    return jsonify({'bache': bache.json() })

@app.route('/mapa')
def mapa():
    #Inicializamos el mapa 
    map= folium.Map(
        location=[-25.302058396540463, -57.58112871603071],
        zoom_start=13,
        )
    cluster= MarkerCluster().add_to(map)
    lista_baches =Bache.query.all()
    extraccion = []
    for datos in lista_baches:
        extraccion.append([datos.latitud, datos.longitud, datos.nombre_bache, datos.foto])

    for point in extraccion:
        mark= point[0],point[1]
        #print(point)
        # # point(i)
        foto= f"static/baches/{point[3]}"
        html = '<img src="data:image/jpg;base64,{}">'.format
        encoded = base64.b64encode(open(foto, 'rb').read())
        #print(foto)
        #print(foto)
        iframe= IFrame(html(encoded),width=120,height=120)
        folium.Marker(
            location=mark,
            popup=folium.Popup(iframe),
            tooltip="bache!"
        ).add_to(cluster)
    return map._repr_html_()

