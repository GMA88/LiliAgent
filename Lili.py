import sys
import os
import tempfile
import pyttsx3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QComboBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, pyqtSlot
import speech_recognition as sr
import pywhatkit
from datetime import datetime
import mysql.connector
import random
import wikipedia
from translatepy import Translator as TranslatePyTranslator
from dotenv import load_dotenv
import re
import logging
from pint import UnitRegistry, errors
import unidecode
from pydub import AudioSegment
import whisper
from dateparser import parse

# Cargar variables de entorno
load_dotenv()

# Configurar el registro de logs
logging.basicConfig(
    filename='lili.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Variables globales
current_language = 'es-MX'  # Idioma por defecto
USERNAME = 'Usuario'
BOTNAME = 'Lili'

# Inicializar el motor TTS
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)  # Volumen al máximo

# Clase Speaker para manejar las solicitudes de habla en el hilo principal
class Speaker(QObject):
    speak_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.speak_signal.connect(self.handle_speak)

    @pyqtSlot(str)
    def handle_speak(self, text):
        """Manejar la solicitud de hablar en el hilo principal."""
        logging.info(f"{BOTNAME}: {text}")
        print(f"{BOTNAME}: {text}")

        # Intentar establecer la voz a Sabina
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'Sabina' in voice.name:
                engine.setProperty('voice', voice.id)
                break
        else:
            logging.warning("La voz 'Sabina' no está disponible. Usando la voz predeterminada.")

        engine.say(text)
        engine.runAndWait()

def greet_user(speaker):
    """Saludar al usuario según la hora del día."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speaker.speak_signal.emit(f"Buenos días {USERNAME}")
    elif 12 <= hour < 16:
        speaker.speak_signal.emit(f"Buenas tardes {USERNAME}")
    else:
        speaker.speak_signal.emit(f"Buenas noches {USERNAME}")
    speaker.speak_signal.emit(f"Yo soy {BOTNAME}. ¿Cómo puedo asistirte hoy?")

def take_user_input(speaker):
    """Capturar y procesar la entrada de voz del usuario."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info('Escuchando...')
        speaker.speak_signal.emit("Estoy escuchando...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        logging.info('Reconociendo...')
        query = r.recognize_google(audio, language=current_language)
        logging.info(f"Usuario dijo: {query}")
        if 'para' in query or 'detente' in query:
            speaker.speak_signal.emit('¡Tenga un buen día!')
            logging.info("Usuario solicitó detenerse.")
            sys.exit()
        return query
    except sr.UnknownValueError:
        speaker.speak_signal.emit('Disculpa, no he podido entender. ¿Podrías repetirlo?')
        logging.warning("No se pudo entender el audio.")
        return 'None'
    except sr.RequestError as e:
        speaker.speak_signal.emit('Error del sistema, no se encuentra disponible.')
        logging.error(f"Error del sistema: {e}")
        return 'None'

def translate_text_function(original_text, target_lang_name, speaker):
    """Traducir texto utilizando translatepy."""
    try:
        translator = TranslatePyTranslator()
        translation = translator.translate(original_text, destination_language=target_lang_name)
        translation_text = translation.result
        logging.info(f"Traducción: {original_text} -> {translation_text}")
        return translation_text
    except Exception as e:
        speaker.speak_signal.emit(f"Error en la traducción: {e}")
        logging.error(f"Error en la traducción: {e}")
        return None

def play_music(song, speaker):
    """Reproducir una canción en YouTube."""
    try:
        pywhatkit.playonyt(song)
        speaker.speak_signal.emit(f"Reproduciendo {song}")
        logging.info(f"Reproduciendo música: {song}")
    except Exception as e:
        speaker.speak_signal.emit("No pude reproducir la música.")
        logging.error(f"Error al reproducir música: {e}")

def contar_chiste(speaker):
    """Contar un chiste al azar."""
    jokes = [
        "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "Si los zombies se deshacen con el paso del tiempo, ¿zombiodegradables?"
    ]
    chiste = random.choice(jokes)
    speaker.speak_signal.emit(chiste)

def resolver_operacion(operacion):
    """Resolver operación matemática a partir de la entrada hablada."""
    # Eliminar espacios al inicio y al final y convertir a minúsculas
    operacion = operacion.strip().lower()
    # Encontrar la expresión después de "cuánto es"
    match = re.search(r"cuánto es (.+)", operacion)
    if not match:
        return None
    expresion = match.group(1)
    # Reemplazar palabras por operadores
    expresion = expresion.replace('más', '+').replace('menos', '-').replace('por', '*').replace('entre', '/')
    # Eliminar cualquier carácter que no sean números o operadores
    expresion = re.sub(r'[^\d+\-*/.]', '', expresion)
    # Validar que la expresión contenga solo números y operadores
    if not re.match(r'^[\d+\-*/.]+$', expresion):
        return None
    try:
        resultado = eval(expresion)
        return resultado
    except Exception:
        return None

def conectar_base_datos(speaker):
    """Conectar a la base de datos MySQL usando variables de entorno."""
    try:
        # Obtener variables de entorno
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        database = os.getenv("DB_NAME")
        port = os.getenv("DB_PORT")

        # Depuración: Imprimir los valores (eliminar en producción)
        print(f"User: {user}, Password: {password}, Host: {host}, Database: {database}, Port: {port}")

        # Validar parámetros
        if not all([user, password, host, database]):
            raise ValueError("Falta uno o más parámetros de conexión a la base de datos.")

        # Establecer valores predeterminados si es necesario
        if port is None:
            port = 3306  # Puerto predeterminado de MySQL
        else:
            port = int(port)  # Convertir puerto a entero

        conexion = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=port
        )
        logging.info("Conexión a la base de datos exitosa.")
        return conexion
    except mysql.connector.Error as err:
        speaker.speak_signal.emit(f"Error al conectar a la base de datos: {err}")
        logging.error(f"Error al conectar a la base de datos: {err}")
        return None
    except Exception as err:
        speaker.speak_signal.emit(f"Error inesperado: {err}")
        logging.error(f"Error inesperado: {err}")
        return None

def consultar_estado(estado, speaker):
    """Obtener información cultural sobre un estado específico desde la base de datos."""
    conexion = conectar_base_datos(speaker)
    if conexion is None:
        return "No se pudo conectar a la base de datos."

    try:
        cursor = conexion.cursor(dictionary=True)
        consulta_sql = "SELECT cultura FROM info WHERE estado = %s"
        cursor.execute(consulta_sql, (estado,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            return resultado['cultura']
        else:
            return "No tengo información sobre ese estado."
    except mysql.connector.Error as err:
        speaker.speak_signal.emit(f"Error en la consulta: {err}")
        logging.error(f"Error en la consulta: {err}")
        return "Error al consultar la base de datos."
 
def UnidadAIng(stringInicial):
    """Convertir nombres de unidades en español a inglés para pint."""
    stringInicial = stringInicial.lower()
    stringInicial = unidecode.unidecode(stringInicial).strip()
    unidades = {
        # Mapear unidades en español a inglés
        "metros": "meter",
        "m": "meter",
        "metro": "meter",
        "centimetros": "centimeter",
        "cm": "centimeter",
        "centimetro": "centimeter",
        "milimetros": "millimeter",
        "mm": "millimeter",
        "milimetro": "millimeter",
        "kilometros": "kilometer",
        "km": "kilometer",
        "kilometro": "kilometer",
        "micrometros": "micrometer",
        "micrometro": "micrometer",
        "nanometros": "nanometer",
        "nanometro": "nanometer",
        "pulgadas": "inch",
        "pulgada": "inch",
        "pies": "foot",
        "ft": "foot",
        "pie": "foot",
        "yardas": "yard",
        "yd": "yard",
        "yarda": "yard",
        "millas": "mile",
        "milla": "mile",
        "litros": "liter",
        "l": "liter",
        "litro": "liter",
        "mililitros": "milliliter",
        "ml": "milliliter",
        "mililitro": "milliliter",
        "galones": "gallon",
        "galon": "gallon",
        "gramos": "gram",
        "g": "gram",
        "gramo": "gram",
        "kilogramos": "kilogram",
        "kg": "kilogram",
        "kilogramo": "kilogram",
        "miligramos": "milligram",
        "mg": "milligram",
        "miligramo": "milligram",
        "microgramos": "microgram",
        "microgramo": "microgram",
        "libras": "pound",
        "libra": "pound",
        "onzas": "ounce",
        "onza": "ounce",
        "toneladas": "tonne",
        "tonelada": "tonne",
        "celsius": "degC",
        "grados celsius": "degC",
        "grados centigrados": "degC",
        "fahrenheit": "degF",
        "grados fahrenheit": "degF",
        "kelvin": "kelvin",
        "joules": "joule",
        "joule": "joule",
        "kilojoules": "kilojoule",
        "kilojoule": "kilojoule",
        "megajoules": "megajoule",
        "megajoule": "megajoule",
        "calorias": "calorie",
        "caloria": "calorie",
        "kilocalorias": "kilocalorie",
        "kilocaloria": "kilocalorie",
        "electronvoltios": "electronvolt",
        "electronvoltio": "electronvolt"
    }
    return unidades.get(stringInicial, None)

def unit_conversion(expression, speaker):
    """Parsear y realizar la conversión de unidades."""
    expression = expression.lower().strip()
    expression = unidecode.unidecode(expression)
    regex = r"\b([\d\.]+)\b\s+([a-zA-Z\s]+?)\s+a\s+([a-zA-Z\s]+)"
    resultados = re.search(regex, expression)
    
    if resultados:
        valor1 = resultados.group(1)
        try:
            valor1_float = float(valor1)
        except ValueError:
            logging.error("Valor numérico inválido.")
            return "El valor numérico es inválido."
        
        valor2 = resultados.group(2).strip()
        valor3 = resultados.group(3).strip()
        valor2Eng = UnidadAIng(valor2)
        valor3Eng = UnidadAIng(valor3)
        
        if not valor2Eng or not valor3Eng:
            logging.error(f"Unidad no reconocida: {valor2} o {valor3}")
            return f"No reconozco la unidad '{valor2}' o '{valor3}'."
        
        logging.info(f"Convirtiendo {valor1_float} {valor2Eng} a {valor3Eng}")
        
        ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
        Q_ = ureg.Quantity
        try:
            cantidad = Q_(valor1_float, valor2Eng)
            resultado = cantidad.to(valor3Eng)
            texto = f"{valor1_float} {valor2} equivalen a {round(resultado.magnitude,3)} {valor3}"
            logging.info(f"Resultado de conversión: {texto}")
            return texto
        except errors.DimensionalityError as e:
            logging.error(f"Error dimensional: {e}")
            return "No puedo convertir entre esas unidades debido a incompatibilidad dimensional."
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            return f"Ocurrió un error inesperado: {e}"
    else:
        logging.info("No se encontraron coincidencias para la conversión.")
        return "No se encontró una conversión válida en el texto proporcionado."
    
class UnitConversionThread(QThread):
    """Clase QThread para manejar la conversión de unidades en segundo plano."""
    conversion_finished = pyqtSignal(str)
    text_captured = pyqtSignal(str)  # Nueva señal para el texto capturado

    def __init__(self, speaker):
        super().__init__()
        self.speaker = speaker

    def run(self):
        """Capturar la entrada de voz y realizar la conversión de unidades."""
        texto = take_user_input(self.speaker)
        if texto and texto != 'None':
            self.text_captured.emit(texto)  # Emitir el texto capturado
            # Añadir un pequeño retraso para actualizar la interfaz
            QThread.msleep(500)
            resultado = unit_conversion(texto, self.speaker)
            self.conversion_finished.emit(resultado)
        else:
            self.conversion_finished.emit("No se capturó ninguna entrada de voz.")

# ===================== CLASES PARA FUNCIONALIDADES ADICIONALES =====================

class TrabajadorAudio(QThread):
    # Señal para devolver el texto transcrito a la interfaz principal
    senal_resultado = pyqtSignal(str)

    def run(self):
        """ Captura el audio y lo transcribe usando Whisper """
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone(sample_rate=16000) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

                # Guardar el audio en un archivo temporal
                archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                ruta_archivo_temporal = archivo_temporal.name
                archivo_temporal.close()

                with open(ruta_archivo_temporal, "wb") as f:
                    f.write(audio.get_wav_data())

                # Convertir el archivo de audio con pydub
                audio_clip = AudioSegment.from_wav(ruta_archivo_temporal)
                audio_clip = audio_clip.set_frame_rate(16000).set_channels(1)
                audio_clip.export(ruta_archivo_temporal, format="wav")

                # Transcribir el audio con Whisper
                modelo = whisper.load_model("base")
                transcripcion = modelo.transcribe(ruta_archivo_temporal, language="es")
                self.senal_resultado.emit(transcripcion['text'])

                os.remove(ruta_archivo_temporal)

        except Exception as e:
            self.senal_resultado.emit(f"Error capturando el audio: {e}")

class VentanaCalcularDias(QWidget):
    def __init__(self, speaker):
        super().__init__()
        self.speaker = speaker

        # Configuración de la ventana principal
        self.setWindowTitle('Calculador de días entre fechas con voz')
        self.setGeometry(100, 100, 400, 300)

        # Crear elementos de la interfaz
        self.etiqueta_inicio = QLabel("Fecha de inicio:")
        self.entrada_inicio = QLineEdit(self)
        self.boton_inicio = QPushButton("Hablar Fecha de Inicio")

        self.etiqueta_fin = QLabel("Fecha de fin:")
        self.entrada_fin = QLineEdit(self)
        self.boton_fin = QPushButton("Hablar Fecha de Fin")

        self.etiqueta_resultado = QLabel("Resultado:")
        self.area_resultado = QTextEdit(self)
        self.area_resultado.setReadOnly(True)

        self.boton_calcular = QPushButton("Calcular")
        self.boton_salir = QPushButton("Salir")

        # Diseño de la ventana
        layout = QVBoxLayout()
        layout.addWidget(self.etiqueta_inicio)
        layout.addWidget(self.entrada_inicio)
        layout.addWidget(self.boton_inicio)

        layout.addWidget(self.etiqueta_fin)
        layout.addWidget(self.entrada_fin)
        layout.addWidget(self.boton_fin)

        layout.addWidget(self.etiqueta_resultado)
        layout.addWidget(self.area_resultado)

        layout.addWidget(self.boton_calcular)
        layout.addWidget(self.boton_salir)

        self.setLayout(layout)

        # Crear hilos de trabajo para la captura de audio
        self.trabajador_audio_inicio = TrabajadorAudio()
        self.trabajador_audio_inicio.senal_resultado.connect(self.manejar_transcripcion_inicio)

        self.trabajador_audio_fin = TrabajadorAudio()
        self.trabajador_audio_fin.senal_resultado.connect(self.manejar_transcripcion_fin)

        # Conectar botones a funciones
        self.boton_inicio.clicked.connect(self.capturar_fecha_inicio)
        self.boton_fin.clicked.connect(self.capturar_fecha_fin)
        self.boton_calcular.clicked.connect(self.calcular_dias)
        self.boton_salir.clicked.connect(self.close)

    def capturar_fecha_inicio(self):
        self.area_resultado.append("Capturando fecha de inicio...")
        self.trabajador_audio_inicio.start()

    def capturar_fecha_fin(self):
        self.area_resultado.append("Capturando fecha de fin...")
        self.trabajador_audio_fin.start()

    def manejar_transcripcion_inicio(self, texto):
        self.entrada_inicio.setText(texto)
        self.area_resultado.append(f"Fecha de inicio transcrita: {texto}")

    def manejar_transcripcion_fin(self, texto):
        self.entrada_fin.setText(texto)
        self.area_resultado.append(f"Fecha de fin transcrita: {texto}")

    def calcular_dias(self):
        texto_inicio = self.entrada_inicio.text()
        texto_fin = self.entrada_fin.text()

        if not texto_inicio or not texto_fin:
            self.area_resultado.append("Error: Por favor ingrese ambas fechas.")
            return

        try:
            fecha_inicio = parse(texto_inicio, languages=['es'])
            fecha_fin = parse(texto_fin, languages=['es'])
            if fecha_inicio and fecha_fin:
                dias_entre = abs((fecha_fin - fecha_inicio).days)
                texto_resultado = f'Días entre las fechas: {dias_entre}'
                self.area_resultado.append(texto_resultado)
                self.speaker.speak_signal.emit(texto_resultado)
            else:
                self.area_resultado.append('Error: Fechas no válidas. Inténtelo de nuevo.')
        except Exception as e:
            self.area_resultado.append(f"Error calculando los días: {e}")

class UnitConversionWindow(QWidget):
    def __init__(self, speaker):
        super().__init__()
        self.speaker = speaker
        self.setWindowTitle("Conversión de Unidades")
        self.resize(500, 400)
        self.layout = QVBoxLayout()

        # Título
        self.titleLabel = QLabel("Conversor de Unidades", self)
        self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.titleLabel)

        # Etiqueta de instrucción
        self.instructionLabel = QLabel("Di una conversión en el formato: número unidad1 a unidad2", self)
        self.instructionLabel.setWordWrap(True)
        self.layout.addWidget(self.instructionLabel)

        # Botón para empezar a grabar
        self.startRecordingBtn = QPushButton("Empezar", self)
        self.startRecordingBtn.setStyleSheet("background-color: green; color: white; font-size: 16px;")
        self.startRecordingBtn.clicked.connect(self.start_recording)
        self.layout.addWidget(self.startRecordingBtn)

        # Etiqueta para mostrar el texto capturado
        self.audioCapturadoLabel = QLabel("", self)
        self.layout.addWidget(self.audioCapturadoLabel)

        # Etiqueta para mostrar el resultado de la conversión
        self.respuestaObtenidaLabel = QLabel("", self)
        self.layout.addWidget(self.respuestaObtenidaLabel)

        self.setLayout(self.layout)

    def start_recording(self):
        """Manejar el inicio de la grabación para la conversión de unidades."""
        self.startRecordingBtn.setText("Grabando...")
        self.startRecordingBtn.setStyleSheet("background-color: red; color: white; font-size: 16px;")
        self.startRecordingBtn.setEnabled(False)

        # Iniciar el hilo de conversión de unidades
        self.thread = UnitConversionThread(self.speaker)
        self.thread.text_captured.connect(self.display_captured_text)  # Conectar nueva señal
        self.thread.conversion_finished.connect(self.handle_conversion_result)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()
        self.speaker.speak_signal.emit("Por favor, di la conversión que deseas realizar.")

    def display_captured_text(self, texto):
        """Mostrar el texto capturado en la interfaz."""
        self.audioCapturadoLabel.setText(f"Texto capturado: {texto}")

    def handle_conversion_result(self, resultado):
        """Manejar el resultado de la conversión de unidades."""
        # Actualizar la interfaz gráfica
        self.respuestaObtenidaLabel.setText(f"Resultado: {resultado}")
        self.speaker.speak_signal.emit(resultado)

    def on_thread_finished(self):
        """Reactivar el botón después de que el hilo termine."""
        # Resetear el botón
        self.startRecordingBtn.setText("Empezar")
        self.startRecordingBtn.setStyleSheet("background-color: green; color: white; font-size: 16px;")
        self.startRecordingBtn.setEnabled(True)

class TranslationWindow(QWidget):
    def __init__(self, speaker):
        super().__init__()
        self.speaker = speaker
        self.setWindowTitle("Traducción de Texto")
        self.resize(400, 400)
        self.layout = QVBoxLayout()

        # Etiqueta y área de texto para el texto original
        self.input_label = QLabel("Texto original:", self)
        self.input_text = QTextEdit(self)

        # Botón para capturar voz
        self.voice_button = QPushButton("Capturar voz", self)
        self.voice_button.clicked.connect(self.capture_voice_input)

        # Etiqueta y ComboBox para seleccionar el idioma de destino
        self.lang_label = QLabel("Idioma de destino:", self)
        self.lang_selector = QComboBox(self)
        self.populate_languages()

        # Botón para traducir
        self.translate_button = QPushButton("Traducir", self)
        self.translate_button.clicked.connect(self.translate_text)

        # Botón para escuchar la traducción
        self.speak_button = QPushButton("Escuchar Traducción", self)
        self.speak_button.clicked.connect(self.speak_translation)

        # Etiqueta y área de texto para el texto traducido
        self.output_label = QLabel("Texto traducido:", self)
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)

        # Agregar widgets al layout
        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_text)
        self.layout.addWidget(self.voice_button)
        self.layout.addWidget(self.lang_label)
        self.layout.addWidget(self.lang_selector)
        self.layout.addWidget(self.translate_button)
        self.layout.addWidget(self.speak_button)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text)

        self.setLayout(self.layout)

    def populate_languages(self):
        """Poblar el selector de idiomas con los idiomas disponibles."""
        self.languages = {
            "Español": "Spanish",
            "Inglés": "English",
            "Francés": "French",
            "Alemán": "German",
            "Italiano": "Italian",
            "Portugués": "Portuguese"
            # Idiomas eliminados: Chino Simplificado, Árabe, Japonés y Ruso
        }
        for lang_display_name, lang_name in self.languages.items():
            self.lang_selector.addItem(lang_display_name, lang_name)

    def capture_voice_input(self):
        """Capturar la entrada de voz y mostrarla en el área de texto original."""
        self.input_text.setText("Capturando entrada de voz...")
        # Crear y ejecutar el hilo de captura de audio
        self.audio_thread = TrabajadorAudio()
        self.audio_thread.senal_resultado.connect(self.mostrar_transcripcion)
        self.audio_thread.start()

    def mostrar_transcripcion(self, transcripcion):
        """Mostrar el resultado de la transcripción en el área de texto."""
        self.input_text.setText(transcripcion)

    def translate_text(self):
        """Traducir el texto de entrada al idioma seleccionado."""
        original_text = self.input_text.toPlainText()
        selected_lang_name = self.lang_selector.currentData()

        if original_text:
            self.speaker.speak_signal.emit("Traduciendo el texto...")
            translated_text = translate_text_function(original_text, selected_lang_name, self.speaker)
            if translated_text:
                self.output_text.setText(translated_text)
            else:
                self.output_text.setText("Error en la traducción.")
                self.speaker.speak_signal.emit("Error en la traducción.")
        else:
            self.speaker.speak_signal.emit("No hay texto para traducir.")
            self.output_text.setText("No hay texto para traducir.")

    def speak_translation(self):
        """Leer en voz alta la traducción."""
        translated_text = self.output_text.toPlainText()
        if translated_text:
            self.speaker.speak_signal.emit(translated_text)
        else:
            self.speaker.speak_signal.emit("No hay traducción disponible para leer.")

class MainWindow(QWidget):
    def __init__(self, speaker):
        super().__init__()

        self.speaker = speaker

        self.setWindowTitle("Asistente de Voz - Lili")
        self.resize(800, 600)
        self.layout = QVBoxLayout()

        # ComboBox para seleccionar opciones
        self.option_selector = QComboBox(self)
        self.option_selector.addItems([
            "Selecciona una opción",
            "Reproducir Música",
            "Consultar Cultura",
            "Resolver Operación Matemática",
            "Contar Chistes",
            "Consultar Año",
            "Traducir",
            "Conversión de Unidades",
            "Calcular Días",  # Nueva funcionalidad
            "Salir"
        ])
        self.option_selector.currentIndexChanged.connect(self.handle_option_selection)
        self.layout.addWidget(self.option_selector)

        # Área de salida de texto
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        self.setLayout(self.layout)

        # Inicializar referencias a las ventanas adicionales
        self.translation_window = None
        self.unit_conversion_window = None
        self.calculate_days_window = None

    def handle_option_selection(self, index):
        """Manejar la selección de una opción desde el ComboBox."""
        if index == 0:
            return  # "Selecciona una opción" seleccionado, no hacer nada

        option = self.option_selector.currentText()
        self.option_selector.setCurrentIndex(0)  # Reiniciar al valor por defecto

        # Ejecutar el comando correspondiente
        if option == "Calcular Días":
            self.open_calculate_days_window()
        elif option in ["Traducir", "Conversión de Unidades", "Salir"]:
            self.execute_command(option)
        else:
            import threading
            thread = threading.Thread(target=self.execute_command, args=(option,))
            thread.start()

    def open_calculate_days_window(self):
        """Abrir la ventana de calcular días."""
        if self.calculate_days_window is None:
            self.calculate_days_window = VentanaCalcularDias(self.speaker)
        self.calculate_days_window.show()

    def execute_command(self, command):
        """Ejecutar el comando seleccionado."""
        if command == "Traducir":
            self.open_translation_window()
        elif command == "Conversión de Unidades":
            self.open_unit_conversion_window()
        elif command == "Salir":
            self.speaker.speak_signal.emit("¡Hasta luego!")
            logging.info("Aplicación cerrada por el usuario.")
            QApplication.quit()
        elif command == "Reproducir Música":
            self.speaker.speak_signal.emit("¿Qué canción te gustaría escuchar?")
            music = take_user_input(self.speaker)
            if music and music != 'None':
                play_music(music, self.speaker)
        elif command == "Contar Chistes":
            contar_chiste(self.speaker)
            self.output_area.append("Contando chiste...")
        elif command == "Resolver Operación Matemática":
            self.speaker.speak_signal.emit("Por favor, dime la operación que quieres resolver.")
            operacion = take_user_input(self.speaker)
            if operacion and operacion != 'None':
                res = resolver_operacion(operacion)
                if res is not None:
                    self.speaker.speak_signal.emit(f"El resultado es {res}")
                    self.output_area.append(f"Operación: {operacion} = {res}")
                else:
                    self.speaker.speak_signal.emit("No pude entender bien tu pregunta. Por favor, repítela de nuevo.")
                    self.output_area.append("No se pudo resolver la operación.")
        elif command == "Consultar Año":
            self.speaker.speak_signal.emit("¿Sobre qué tema te gustaría consultar el año?")
            tema = take_user_input(self.speaker)
            if tema and tema != 'None':
                try:
                    wikipedia.set_lang('es')
                    resultados = wikipedia.summary(tema, sentences=2, auto_suggest=False)
                    self.speaker.speak_signal.emit(f"De acuerdo con Wikipedia: {resultados}")
                    self.output_area.append(f"Resultados de Wikipedia:\n{resultados}")
                except wikipedia.exceptions.DisambiguationError as e:
                    self.speaker.speak_signal.emit("El término es ambiguo. Por favor, proporciona más detalles.")
                    self.output_area.append("Error de ambigüedad en Wikipedia.")
                except wikipedia.exceptions.PageError:
                    self.speaker.speak_signal.emit("No se encontró ninguna página para ese término en Wikipedia.")
                    self.output_area.append("Página no encontrada en Wikipedia.")
                except Exception as e:
                    self.speaker.speak_signal.emit("Ocurrió un error al consultar Wikipedia.")
                    self.output_area.append(f"Error al consultar Wikipedia: {e}")
        elif command == "Consultar Cultura":
            self.speaker.speak_signal.emit("¿De qué estado te gustaría conocer la cultura?")
            estado = take_user_input(self.speaker)
            if estado and estado != 'None':
                cultura_info = consultar_estado(estado, self.speaker)
                self.speaker.speak_signal.emit(cultura_info)
                self.output_area.append(f"Cultura de {estado}: {cultura_info}")

    def open_translation_window(self):
        """Abrir la ventana de traducción."""
        if self.translation_window is None:
            self.translation_window = TranslationWindow(self.speaker)
        self.translation_window.show()

    def open_unit_conversion_window(self):
        """Abrir la ventana de conversión de unidades."""
        if self.unit_conversion_window is None:
            self.unit_conversion_window = UnitConversionWindow(self.speaker)
        self.unit_conversion_window.show()

# APLICACIÓN PRINCIPAL

if __name__ == "__main__":
    app = QApplication(sys.argv)         # Crear la aplicación PyQt5
    speaker = Speaker()                  # Crear la instancia de Speaker
    window = MainWindow(speaker)         # Crear la ventana principal con Speaker
    window.show()                        # Mostrar la ventana principal
    greet_user(speaker)                  # Saludo inicial
    sys.exit(app.exec())                 # Iniciar el bucle de eventos

