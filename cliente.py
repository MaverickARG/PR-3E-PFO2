import requests
import webbrowser
import os

URL = "http://127.0.0.1:5000"

# la sesión guarda la cookie del login para poder entrar a /tareas
sesion = requests.Session()


def mostrar_mensaje(respuesta):
    # si el servidor no devuelve JSON (por ejemplo un error 500) se muestra el código
    try:
        print(respuesta.json()["mensaje"])
    except ValueError:
        print("Error del servidor, código:", respuesta.status_code)


def registrar():
    usuario = input("Usuario: ")
    contrasena = input("Contraseña: ")
    respuesta = sesion.post(URL + "/registro", json={"usuario": usuario, "contraseña": contrasena})
    mostrar_mensaje(respuesta)


def iniciar_sesion():
    usuario = input("Usuario: ")
    contrasena = input("Contraseña: ")
    respuesta = sesion.post(URL + "/login", json={"usuario": usuario, "contraseña": contrasena})
    mostrar_mensaje(respuesta)


def bienvenida():
    respuesta = sesion.get(URL + "/tareas")
    if respuesta.status_code == 200:
        # guarda el HTML recibido y lo abre en el navegador
        with open("tareas.html", "w", encoding="utf-8") as archivo:
            archivo.write(respuesta.text)
        webbrowser.open("file://" + os.path.abspath("tareas.html"))
        print("Se abrió la página de bienvenida en el navegador")
    else:
        mostrar_mensaje(respuesta)


def main():
    while True:
        print("\n1. Registrarse\n2. Iniciar sesión\n3. Bienvenida\n4. Salir")
        opcion = input("Seleccione una opción: ")
        print("\n")
        if opcion == "1":
            registrar()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            bienvenida()
        elif opcion == "4":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()