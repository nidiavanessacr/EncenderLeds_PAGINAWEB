from flask import Flask, request, jsonify, render_template
from config import config
from flask_mysqldb import MySQL

app = Flask(__name__)
conexion = MySQL(app)

@app.route("/leds", methods=["GET"])
def listar_leds():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT id, descripcion, status FROM leds")
        datos = cursor.fetchall()
        leds = [{"id": d[0], "descripcion": d[1], "status": bool(d[2])} for d in datos]
        return jsonify({"leds": leds, "mensaje": "Consulta exitosa"})
    except Exception as e:
        return jsonify({"mensaje": "Error en la consulta", "error": str(e)})

@app.route("/leds/<int:id>", methods=["GET"])
def leer_led(id):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT id, descripcion, status FROM leds WHERE id = %s", (id,))
        led = cursor.fetchone()
        if led:
            return jsonify({"led": {"id": led[0], "descripcion": led[1], "status": bool(led[2])}})
        else:
            return jsonify({"mensaje": "LED no encontrado"}), 404
    except Exception as e:
        return jsonify({"mensaje": "Error en la consulta", "error": str(e)})

@app.route("/leds", methods=["POST"])
def agregar_led():
    try:
        data = request.json
        cursor = conexion.connection.cursor()
        cursor.execute("INSERT INTO leds (id, descripcion, status) VALUES (%s, %s, %s)", (data['id'], data['descripcion'], int(data['status'])))
        conexion.connection.commit()
        return jsonify({"mensaje": "LED agregado exitosamente"})
    except Exception as e:
        return jsonify({"mensaje": "Error al agregar el LED", "error": str(e)})

@app.route("/leds/<int:id>", methods=["PUT"])
def editar_led(id):
    try:
        data = request.json
        cursor = conexion.connection.cursor()
        cursor.execute("UPDATE leds SET descripcion = %s WHERE id = %s", (data['descripcion'], id))
        conexion.connection.commit()
        return jsonify({"mensaje": "Descripción del LED actualizada"})
    except Exception as e:
        return jsonify({"mensaje": "Error al actualizar la descripción", "error": str(e)})

@app.route("/leds/<int:id>/status", methods=["PUT"])
def cambiar_estado_led(id):
    try:
        nuevo_estado = request.json['status']
        cursor = conexion.connection.cursor()
        cursor.execute("UPDATE leds SET status = %s WHERE id = %s", (int(nuevo_estado), id))
        conexion.connection.commit()
        return jsonify({"mensaje": "Estado del LED actualizado"})
    except Exception as e:
        print("ERROR:", str(e))  # Log para depuración
        return jsonify({"mensaje": "Error al cambiar el estado", "error": str(e)})

@app.route("/leds/<int:id>", methods=["DELETE"])
def eliminar_led(id):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("DELETE FROM leds WHERE id = %s", (id,))
        conexion.connection.commit()
        return jsonify({"mensaje": "LED eliminado exitosamente"})
    except Exception as e:
        return jsonify({"mensaje": "Error al eliminar el LED", "error": str(e)})

@app.route("/")
def home():
    return render_template("index.html")

def pagina_no_encontrada(e):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)
