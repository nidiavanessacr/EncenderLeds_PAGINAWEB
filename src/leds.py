from flask import Flask, request, jsonify, render_template
from config import config
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)
conexion = MySQL(app)

# ===========================================================
#   UTILIDAD PARA CIFRAR CONTRASEÑAS
# ===========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ===========================================================
#   ENDPOINTS DE USUARIOS (REGISTER / LOGIN)
# ===========================================================

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True, silent=True)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"mensaje": "Faltan datos"}), 400

        hashed = hash_password(password)

        cursor = conexion.connection.cursor()

        # Validar si el usuario ya existe
        cursor.execute("SELECT username FROM usuarios WHERE username = %s", (username,))
        existe = cursor.fetchone()

        if existe:
            return jsonify({"mensaje": "El usuario ya existe"}), 409

        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (username, hashed)
        )
        conexion.connection.commit()

        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201

    except Exception as e:
        return jsonify({"mensaje": "Error en el registro", "error": str(e)}), 500



@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"mensaje": "Faltan datos"}), 400

        hashed = hash_password(password)

        cursor = conexion.connection.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE username = %s AND password = %s",
            (username, hashed)
        )
        user = cursor.fetchone()

        if user:
            return jsonify({
                "mensaje": "Login exitoso",
                "login": True,
                "user_id": user[0]
            }), 200

        return jsonify({"mensaje": "Credenciales incorrectas", "login": False}), 401

    except Exception as e:
        return jsonify({"mensaje": "Error en login", "error": str(e)}), 500


# ===========================================================
#   OPCIONAL: LISTAR USUARIOS (DEBUG)
# ===========================================================
@app.route("/usuarios", methods=["GET"])
def usuarios():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT id, username FROM usuarios")
        result = cursor.fetchall()

        lista = [{"id": row[0], "username": row[1]} for row in result]

        return jsonify({"usuarios": lista})
    except Exception as e:
        return jsonify({"mensaje": "Error al obtener usuarios", "error": str(e)})


# ===========================================================
#   ENDPOINTS DE LEDS
# ===========================================================

@app.route("/leds", methods=["GET"])
def listar_leds():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT id, descripcion, status FROM leds")
        datos = cursor.fetchall()

        leds = [{
            "id": d[0],
            "descripcion": d[1],
            "status": bool(d[2])
        } for d in datos]

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
            return jsonify({
                "led": {
                    "id": led[0],
                    "descripcion": led[1],
                    "status": bool(led[2])
                }
            })
        return jsonify({"mensaje": "LED no encontrado"}), 404

    except Exception as e:
        return jsonify({"mensaje": "Error en la consulta", "error": str(e)})


@app.route("/leds", methods=["POST"])
def agregar_led():
    try:
        data = request.json
        cursor = conexion.connection.cursor()

        cursor.execute(
            "INSERT INTO leds (id, descripcion, status) VALUES (%s, %s, %s)",
            (data['id'], data['descripcion'], int(data['status']))
        )
        conexion.connection.commit()

        return jsonify({"mensaje": "LED agregado exitosamente"})

    except Exception as e:
        return jsonify({"mensaje": "Error al agregar el LED", "error": str(e)})


@app.route("/leds/<int:id>", methods=["PUT"])
def editar_led(id):
    try:
        data = request.json
        cursor = conexion.connection.cursor()

        cursor.execute(
            "UPDATE leds SET descripcion = %s WHERE id = %s",
            (data['descripcion'], id)
        )
        conexion.connection.commit()

        return jsonify({"mensaje": "Descripción del LED actualizada"})

    except Exception as e:
        return jsonify({"mensaje": "Error al actualizar LED", "error": str(e)})



@app.route("/leds/<int:id>/status", methods=["PUT"])
def cambiar_estado_led(id):
    try:
        nuevo_estado = request.json['status']
        cursor = conexion.connection.cursor()

        cursor.execute(
            "UPDATE leds SET status = %s WHERE id = %s",
            (int(nuevo_estado), id)
        )
        conexion.connection.commit()

        return jsonify({"mensaje": "Estado del LED actualizado"})

    except Exception as e:
        return jsonify({"mensaje": "Error al cambiar estado del LED", "error": str(e)})



@app.route("/leds/<int:id>", methods=["DELETE"])
def eliminar_led(id):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("DELETE FROM leds WHERE id = %s", (id,))
        conexion.connection.commit()

        return jsonify({"mensaje": "LED eliminado exitosamente"})

    except Exception as e:
        return jsonify({"mensaje": "Error al eliminar LED", "error": str(e)})


# ===========================================================
#   HOME Y ERROR 404
# ===========================================================
@app.route("/")
def home():
    return render_template("index.html")


def pagina_no_encontrada(e):
    return "<h1>Página no encontrada</h1>", 404


# ===========================================================
#   EJECUCIÓN
# ===========================================================
if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)
