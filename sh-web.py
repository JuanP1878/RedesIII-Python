import RPi.GPIO as GPIO
import psutil
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import Adafruit_DHT

app = Flask(__name__, static_folder='static', template_folder='static/dist')
CORS(app)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

############### DEFINICIÓN GPIO PÁGINA PRINCIPAL ###############
# Variables para el sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

# definimos los pines GPIOs
Xbox = 29
Ventilador = 31
Television = 33
Bocinas = 35
Humo = 37
Luz = 40
Cuarto = [29, 31, 33, 35, 37, 40]

# inicializamos las varibles del status
XboxSts = 0
VentiladorSts = 0
TelevisionSts = 0
BocinasSts = 0
HumoSts = 0
LuzSts = 0
CuartoSts = 0

# Definimos los pines como salida
GPIO.setup(Xbox, GPIO.OUT)
GPIO.setup(Ventilador, GPIO.OUT)
GPIO.setup(Television, GPIO.OUT)
GPIO.setup(Bocinas, GPIO.OUT)
GPIO.setup(Humo, GPIO.OUT)
GPIO.setup(Luz, GPIO.OUT)


GPIO.output(Xbox, GPIO.HIGH)
GPIO.output(Ventilador, GPIO.HIGH)
GPIO.output(Television, GPIO.HIGH)
GPIO.output(Bocinas, GPIO.HIGH)
GPIO.output(Humo, GPIO.HIGH)
GPIO.output(Luz, GPIO.HIGH)


# Ruta base que se renderiza primero
@app.route("/")
def index():
    return render_template('index.html')

# Ruta que se renderiza cuando se ejecuta alguna acción


@app.route("/<deviceName>/<action>")
def action(deviceName, action):

    if deviceName != 'Cuarto':
        if deviceName == 'Xbox':
            actuator = Xbox
        if deviceName == 'Ventilador':
            actuator = Ventilador
        if deviceName == 'Televisión':
            actuator = Television
        if deviceName == 'Bocinas':
            actuator = Bocinas
        if deviceName == 'Humo':
            actuator = Humo
        if deviceName == 'Luz':
            actuator = Luz

        if action == "on":
            GPIO.output(actuator, GPIO.LOW)
        if action == "off":
            GPIO.output(actuator, GPIO.HIGH)

        xboxSts = GPIO.input(Xbox)
        ventiladorSts = GPIO.input(Ventilador)
        televisionSts = GPIO.input(Television)
        bocinasSts = GPIO.input(Bocinas)
        humoSts = GPIO.input(Humo)
        luzSts = GPIO.input(Luz)

        templateData = {
            'Xbox': xboxSts,
            'Ventilador': ventiladorSts,
            'Television': televisionSts,
            'Bocinas': bocinasSts,
            'Humo': humoSts,
            'Luz': luzSts,
        }
    else:
        if action == "on":
            GPIO.output(Xbox, GPIO.LOW)
            GPIO.output(Ventilador, GPIO.LOW)
            GPIO.output(Television, GPIO.LOW)
            GPIO.output(Bocinas, GPIO.LOW)
            GPIO.output(Humo, GPIO.LOW)
            GPIO.output(Luz, GPIO.LOW)

        if action == "off":
            GPIO.output(Xbox, GPIO.HIGH)
            GPIO.output(Ventilador, GPIO.HIGH)
            GPIO.output(Television, GPIO.HIGH)
            GPIO.output(Bocinas, GPIO.HIGH)
            GPIO.output(Humo, GPIO.HIGH)
            GPIO.output(Luz, GPIO.HIGH)

        xboxSts = GPIO.input(Xbox)
        ventiladorSts = GPIO.input(Ventilador)
        televisionSts = GPIO.input(Television)
        bocinasSts = GPIO.input(Bocinas)
        humoSts = GPIO.input(Humo)
        luzSts = GPIO.input(Luz)

        templateData = {
            'Xbox': xboxSts,
            'Ventilador': ventiladorSts,
            'Televisión': televisionSts,
            'Bocinas': bocinasSts,
            'Humo': humoSts,
            'Luz': luzSts,
        }
    return jsonify([templateData])
    # return render_template('index.html', **templateData)


@app.route('/status')
def status():
    xboxSts = GPIO.input(Xbox)
    ventiladorSts = GPIO.input(Ventilador)
    televisionSts = GPIO.input(Television)
    bocinasSts = GPIO.input(Bocinas)
    humoSts = GPIO.input(Humo)
    luzSts = GPIO.input(Luz)

    templateData = {
        'Xbox': xboxSts,
        'Ventilador': ventiladorSts,
        'Televisión': televisionSts,
        'Bocinas': bocinasSts,
        'Humo': humoSts,
        'Luz': luzSts,
    }

    return jsonify([templateData])


@app.route('/reports')
def reports():
    # Estdísticas sobre memoria RAM (libre,usada,activa,etc)
    mem = psutil.virtual_memory()
    memUsada = mem.used/1048576  # Megas

    # Estdísticas sobre uso de CPU
    cpu = psutil.cpu_percent(interval=1)  # Porcentaje

    # Estdísticas sobre uso de espacio en Disco
    disk = psutil.disk_usage('/')
    diskUsed = disk.used / 1073741824  # Gigas

    # Temperatura del CPU
    temp = getCPUtemperature()

    templateData = {
        'mem': memUsada,
        'cpu': cpu,
        'disk': diskUsed,
        'temp': temp
    }

    return jsonify(templateData)


@app.route('/getCurrentSensorData')
def sensorData():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
    	auxTemp = '{:.2f}'.format(temperature)
    	auxHum = '{:.2f}'.format(humidity)
    	templateData = {
        	'temp': auxTemp,
        	'hum': auxHum
    	}
    	return jsonify(templateData)
    else:
        return ({message: "Failed to retrieve data from sensor"})


def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=", "").replace("'C\n", ""))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
