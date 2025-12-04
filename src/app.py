from flask import Flask, request
from config import config
from flask_mysqldb import MySQL
from flask import jsonify

app = Flask(__name__)
conexion = MySQL(app)

@app.route("/cursos", methods=["GET"])
def listar_cursos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT codigo, nombre, creditos FROM curso"
        cursor.execute(sql)
        datos = cursor.fetchall()
        cursos = []
        for curso in datos:
            curso = {
                "codigo": curso[0],
                "nombre": curso[1],
                "creditos": curso[2]
            }
            cursos.append(curso)
             
        return jsonify({"cursos": cursos, "mensajes " : "consulta exitosa"})
    except Exception as e:
        return jsonify({"mensaje" : "Error en + consulta" , "error" :  str(e)})
    

@app.route("/cursos/<codigo>", methods=["GET"])
def leer_curso(codigo):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT codigo, nombre, creditos FROM 
        curso WHERE codigo = '{0}' """.format(codigo)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            curso = {"codigo": datos[0], "nombre": datos[1], "creditos": datos[2]}
            return jsonify({'curso': curso, 'mensaje': 'consulta exitosa'})
        else:
            return jsonify({'mensaje': 'No existe el curso'})
    except Exception as e:
        return jsonify({'mensaje': 'Error en la consulta', 'error': str(e)})

@app.route("/cursos", methods=["POST"])
def crear_curso():
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO curso (codigo, nombre, creditos)
        VALUES ('{0}','{1}', {2})
        """.format(request.json['codigo'], request.json['nombre'], request.json['creditos'])
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': 'Curso creado exitosamente'})
    except Exception as e:
        return jsonify({'mensaje': 'Error al crear el curso', 'error': str(e)})
    
@app.route("/cursos/<codigo>", methods=["DELETE"])
def eliminar_curso(codigo):
    try:
        cursor = conexion.connection.cursor()
        sql = """DELETE FROM curso WHERE codigo = '{0}' """.format(codigo)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': 'Curso eliminado exitosamente'})
    except Exception as e:
        return jsonify({'mensaje': 'Error al eliminar el curso', 'error': str(e)})

@app.route("/cursos/<codigo>", methods=["PUT"])
def actualizar_curso(codigo):
    try:
        cursor = conexion.connection.cursor()
        sql = """UPDATE curso SET nombre = '{0}', creditos = {1}
        WHERE codigo = '{2}' """.format(request.json['nombre'], request.json['creditos'], codigo)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': 'Curso actualizado exitosamente'})
    except Exception as e:
        return jsonify({'mensaje': 'Error al actualizar el curso', 'error': str(e)})
    
def pagina_no_encontrada(e):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])	
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()