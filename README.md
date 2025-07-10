== Auth_Keylogger ==

Este script configura un pequeño entorno virtual con algunas herramientas que podrian ayudarte a practicar tus habilidade en algun ambiente controlado.

Cabe resaltar que esto es hecho con fines educativo, no tengo la intencion de afectar a nadie, ni motivar a los demas a que lo hagan.

Aun asi ten en cuenta que eres responsable del uso que le des, pero te recomiendo que no hagas nada ilicito o ilegal con esta herramienta ya que puedes meterte en problemas serios.

== NO ME HAGO RESPONSABLE DEL USO QUE LE DES A ESTE SCRIPT ==

== Inicio ==

Clona el repositorio con git clone:

[+] $> git clone https://github.com/baphometh-ux/Auth_Keylogger

$> cd Auth_Keylogger

Despues dentro de la carpeta creas un entorno virtual con: 

$> python -m venv .venv

Activas tu entorno virtual:

Windows:
$> .venv\Scripts\activate.ps1

Linux:
$> source .venv\bin\activate

Luego instalas las dependencias:

$> pip install -r requirements.txt

Despues sigues con la configuracion.

== Configuracion del Keylogger ==

Primero necesitas crear un archivo .env dentro de la carpeta del repositorio.
dentro de ella escribiras las siguientes lineas:

RAPIDAPI_KEY=
TEMPMAIL_TOKEN=
USERNAME=
PASSWORD=

Despues puedes proseguir con la configuracion para obtener los datos que van en el archivo .env, tu solo pondras la RAPIDAPI_KEY y el TEMPMAIL_TOKEN.
Lo demas lo dejas tal cual.

La configuracion inicial para crear los correos temporales es la siguiente:

1. Necesitas La RAPIDAPI-KEY y el TOKEN de TempMailSo.

Para conseguir la RAPIDAPI-KEY debes de ir a la pagina web de TempMailSo en rapidapi.com:

[+] https://rapidapi.com/tempmailso-tempmailso-default/api/tempmail-so

y presionas algunos de los endpoints, te aparecera una pantalla divida en dos, de lado izquierdo 3 campos, App, X-RapidAPI-Key y request URL. y del lado derecho te explica como usarlo. Bien pues necesitas la API que aparece en X-RapidAPI-Key. y si no te aparece debes debes crear una aplicacion en tu perfil (Crea un perfil si no lo tienes) y añades un "Authorization Key" luego de eso ya deberia aparecerte la X-RapidAPI-Key.

Para conseguir el TOKEN de TempMailSo debes ir a:

[+] https://tempmail.so/us

Creas una cuenta y una vez creada presionas las tres barritas que aparecen de lado derecho en la parte de arriba, presionas donde esta tu correo te mandara a otra pagina, vuelves a presionar tu correo y te apareceran varias opciones, tu presionas la que dice Account y te aparece "API-Token" y esa es la que necesitas.

2. Cuando hayas clonado ya el repositorio, debes crear un archivo ".env", y dentro del archivo escribes dos lineas:

RAPIDAPI-KEY = [Tu api de X-RapidAPI-Key]
TEMPMAIL_TOKEN = [Token de la pagina TempMailSo]

lo guardas y listo.

Cuando tengas todo configurado, solo debes iniciar el script en la maquina objetivo y listo.