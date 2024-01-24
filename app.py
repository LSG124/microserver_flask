# Importaciones necesarias para la aplicación
# Si el servidor llega a crecer la arquitectura se 
# tendrá que dividir por archivos separados
# @author_: Luis Saavedra Ramos 
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.security import check_password_hash

# Inicialización de la aplicación Flask
# Se considera Flask por ser un microframework 
# Bien podría ser Djando, laravel, CodeIgniter4
# Estos otros frameworks son mucho más potentes y tienen arquitecturas 
# más robustas. 
app = Flask(__name__)
CORS(app)  # Habilitación de CORS para evitar problemas de Cross-Origin
#Se dejan habilitadas para llamadas que no provengan del mismo servidor. 

# Configuración de la conexión a la base de datos MySQL
# En este caso de trabaja con XAMPP por temas de practicidad
# Puede ser dockerizado o si conviene a los desarrolladores y se posee un servidor 
# con otro tipo de base de datos habría que cambiar los conectores. 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # El usuario por defecto en XAMPP
app.config['MYSQL_PASSWORD'] = ''  # La contraseña por defecto en XAMPP suele estar vacía
app.config['MYSQL_DB'] = 'task_manager_db'

mysql = MySQL(app)  # Inicialización del objeto MySQL con la configuración de la aplicación

# Ruta para probar la conexión a la base de datos
# Esta ruta es la inicial para llamar desde la GUI (frontend)
# Si esta ruta no inicia o detecta errores la aplicación de tareas no permitirá seguir avanzando.
@app.route('/testconexion')
def test_conexion():
    #Bloque try catch para comprobar la conexión
    try:
        conn = mysql.connection
        return "CONEXIÓN ESTABLECIDA" if conn else "CONEXIÓN FALLIDA"
    except Exception as e:
        return f"Error al conectar: {e}"

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']  
    # de momento se omite el hashing, por practicidad
    # es una mala práctica no considerar el hashing
    # en actualizaciones futuras este código se refactorizará para dejar todo hasheado.

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        return "Usuario registrado con éxito"
    except MySQLdb.IntegrityError:
        return "Error: El nombre de usuario ya existe", 400
    except Exception as e:
        return f"Error interno: {e}", 500
    finally:
        cursor.close()

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and user[2] == password:
        user_id = user[0]
        return jsonify({"message": "Inicio de sesión exitoso", "user_id": user_id}), 200
    else:
        return jsonify({"message": "Inicio de sesión fallido"}), 401

# Ruta para crear una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    user_id = data['user_id']
    title = data['title']
    description = data['description']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, description) VALUES (%s, %s, %s)", (user_id, title, description))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"message": "Tarea creada exitosamente"}), 201

# Ruta para obtener las tareas de un usuario
@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()
    cursor.close()

    tasks_list = [{"id": task[0], "title": task[2], "description": task[3]} for task in tasks]
    return jsonify(tasks_list)

# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
