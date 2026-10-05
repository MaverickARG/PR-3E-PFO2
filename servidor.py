from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__, static_folder="assets", static_url_path="/assets")
app.secret_key = "clave_secreta_pfo2"  # necesaria para usar session

# la base se guarda en la misma carpeta que este archivo
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tareas.db")


def crear_tabla():
    conexion = sqlite3.connect(DB)
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    usuario = datos.get("usuario")
    contrasena = datos.get("contraseña")

    if not usuario or not contrasena:
        return jsonify({"mensaje": "Faltan datos"}), 400

    # Guardado del Hash de la contraseña
    contrasena_hash = generate_password_hash(contrasena)

    try:
        conexion = sqlite3.connect(DB)
        conexion.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)",
                         (usuario, contrasena_hash))
        conexion.commit()
        conexion.close()
    except sqlite3.IntegrityError:
        return jsonify({"mensaje": "El usuario ya existe"}), 409

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    usuario = datos.get("usuario")
    contrasena = datos.get("contraseña")

    conexion = sqlite3.connect(DB)
    fila = conexion.execute("SELECT contrasena FROM usuarios WHERE usuario = ?",
                            (usuario,)).fetchone()
    conexion.close()

    # Comparación de la contraseña ingresada con el hash guardado
    if fila and check_password_hash(fila[0], contrasena):
        session["usuario"] = usuario
        return jsonify({"mensaje": "Login exitoso"}), 200

    return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401


@app.route("/tareas", methods=["GET"])
def tareas():
    # solo se puede entrar si antes se hizo login
    if "usuario" not in session:
        return jsonify({"mensaje": "Primero tenés que iniciar sesión"}), 401

    capturas = [
        ("Inicio del servidor", "server.png"),
        ("Inicio del cliente", "client.png"),
        ("Registro de usuario", "register.png"),
        ("Inicio de sesión", "login.png"),
        ("Bienvenida en consola", "initconsol.png"),
        ("Bienvenida en navegador", "inithtml.png"),
        ("Error de usuario o contraseña", "logerror.png"),
        ("Error al registrar", "errorreg.png"),
    ]

    # arma el HTML de cada captura pidiendo la imagen al servidor
    imagenes = ""
    for titulo, archivo in capturas:
        imagenes += f'<h3>{titulo}</h3><img src="{request.host_url}assets/{archivo}" width="700"><br>'

    return f"""
    <html>
        <head><meta charset="utf-8"><title>PFO2 - Programacion sobre redes</title></head>
                <body>
                    <h1>Bienvenido Usuario {session['usuario']}</h1>
                    <h2></h2>
        
                    <h2>Respuestas conceptuales</h2>
                    <h3>¿Por qué hashear contraseñas?</h3>
                    <p>Porque si alguien accede a la base de datos no puede ver las contraseñas reales.
                    El hash no se puede revertir, así que para el login se compara el hash de la contraseña
                    ingresada con el guardado. Además muchas personas usan la misma contraseña en varios sitios,
                    entonces guardarlas en texto plano pondría en riesgo también otras cuentas. La librería
                    werkzeug agrega una "sal" aleatoria, por lo que dos usuarios con la misma contraseña
                    tienen hashes distintos.</p>
        
                    <h3>Ventajas de usar SQLite en este proyecto</h3>
                    <p>No hace falta instalar ni configurar un servidor de base de datos, ya viene incluido en Python.
                    Toda la base está en un solo archivo (<code>tareas.db</code>), que se crea solo al ejecutar
                    el servidor, así que el proyecto es fácil de compartir y probar. Los datos quedan guardados
                    aunque se apague el servidor.</p>

            <h2>Capturas | Pruebas de funcionamiento</h2>
            {imagenes}
        </body>
    </html>
    """

# se crea la tabla al iniciar, de cualquier forma que se ejecute el servidor
crear_tabla()

if __name__ == "__main__":
    app.run(debug=True)