import sys
import pyttsx3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import speech_recognition as sr
import pywhatkit
from datetime import datetime
import mysql.connector
import random
import wikipedia
from googletrans import Translator
from dotenv import load_dotenv
import os
import re
import logging
from pint import UnitRegistry, errors
import unidecode

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
tts_voice_language = 'es'    # Idioma para TTS
USERNAME = 'Usuario'
BOTNAME = 'Lili'

# Inicializar el motor TTS
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)  # Rango de volumen correcto

# Cambiar la voz a Sabina si está disponible
voices = engine.getProperty('voices')
selected_voice = None
for voice in voices:
    if 'Sabina' in voice.name:
        selected_voice = voice.id
        break

if selected_voice:
    engine.setProperty('voice', selected_voice)
else:
    logging.warning("La voz 'Sabina' no está disponible. Usando la voz predeterminada.")

def speak(text):
    """Convertir texto a voz."""
    logging.info(f"{BOTNAME}: {text}")
    print(f"{BOTNAME}: {text}")
    engine.say(text)
    engine.runAndWait()

def greet_user():
    """Saludar al usuario según la hora del día."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Buenos días {USERNAME}")
    elif 12 <= hour < 16:
        speak(f"Buenas tardes {USERNAME}")
    else:
        speak(f"Buenas noches {USERNAME}")
    speak(f"Yo soy {BOTNAME}. ¿Cómo puedo asistirte hoy?")

def conectar_base_datos():
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
        if not all([user, password, host, database, port]):
            raise ValueError("Falta uno o más parámetros de conexión a la base de datos.")

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
    except Exception as err:
        speak(f"Error al conectar a la base de datos: {err}")
        logging.error(f"Error al conectar a la base de datos: {err}")
        return None

def consultar_estado(estado):
    """Obtener información cultural sobre un estado específico desde la base de datos."""
    conexion = conectar_base_datos()
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
        speak(f"Error en la consulta: {err}")
        logging.error(f"Error en la consulta: {err}")
        return "Error al consultar la base de datos."

def contar_chiste():
    """Contar un chiste al azar."""
    jokes = [
        "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "Si los zombies se deshacen con el paso del tiempo, ¿zombiodegradables?"
    ]
    chiste = random.choice(jokes)
    speak(chiste)

def translate_text_function(original_text, target_lang):
    """Traducir texto del idioma original al idioma de destino."""
    translator = Translator(service_urls=['translate.googleapis.com'])
    if original_text:
        try:
            translation = translator.translate(original_text, dest=target_lang).text
            logging.info(f"Traducción: {original_text} -> {translation}")
            return translation
        except Exception as e:
            speak(f"Error en la traducción: {e}")
            logging.error(f"Error en la traducción: {e}")
            return None

def UnidadAIng(stringInicial):
    """Convertir nombres de unidades en español a inglés para pint."""
    stringInicial = stringInicial.lower()
    stringInicial = unidecode.unidecode(stringInicial)
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
        "toneladas": "ton",
        "tonelada": "ton",
        "celsius": "celsius",
        "fahrenheit": "fahrenheit",
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

def unit_conversion(expression):
    """Parsear y realizar la conversión de unidades."""
    regex = r"\b([\d.]+)\b\s+(\w+)\s+a\s+(\w+)"
    resultados = re.search(regex, expression)
    
    if resultados:
        valor1 = resultados.group(1)
        try:
            valor1_float = float(valor1)
        except ValueError:
            logging.error("Valor numérico inválido.")
            return "La unidad no se encontró o no se pudo realizar las conversiones."
        
        valor2 = resultados.group(2)
        valor2Eng = UnidadAIng(valor2)
        valor3 = resultados.group(3)
        valor3Eng = UnidadAIng(valor3)
        
        if not valor2Eng or not valor3Eng:
            logging.error("Unidad no reconocida.")
            return "La unidad no se encontró o no se pudo realizar las conversiones."
        
        logging.info(f"Convirtiendo {valor1_float} {valor2Eng} a {valor3Eng}")
        
        ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
        try:
            cantidad = valor1_float * ureg(valor2Eng)
            resultado = cantidad.to(valor3Eng)
            texto = f"{valor1_float} {valor2} en {valor3} son {round(resultado.magnitude,3)} {valor3}"
            logging.info(f"Resultado de conversión: {texto}")
            return texto
        except errors.DimensionalityError as e:
            logging.error(f"Error dimensional: {e}")
            return f"Error: {e}"
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            return f"Un error inesperado con las conversiones sucedió: {e}"
    else:
        logging.info("No se encontraron coincidencias para la conversión.")
        return "No se encontraron coincidencias para hacer alguna conversión."

def take_user_input():
    """Capturar y procesar la entrada de voz del usuario."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info('Escuchando...')
        speak("Estoy escuchando...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    
    try:
        logging.info('Reconociendo...')
        query = r.recognize_google(audio, language=current_language)
        logging.info(f"Usuario dijo: {query}")
        if 'para' in query or 'detente' in query:
            speak('¡Tenga un buen día!')
            logging.info("Usuario solicitó detenerse.")
            sys.exit()
        return query
    except sr.UnknownValueError:
        speak('Disculpa, no he podido entender. ¿Podrías repetirlo?')
        logging.warning("No se pudo entender el audio.")
        return 'None'
    except sr.RequestError as e:
        speak('Error del sistema, no se encuentra disponible.')
        logging.error(f"Error del sistema: {e}")
        return 'None'

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

# ===================== CLASES DE LA INTERFAZ GRÁFICA =====================

class Worker(QObject):
    """Clase Worker para manejar señales desde hilos."""
    translation_completed = pyqtSignal(str)
    conversion_completed = pyqtSignal(str)

# Clase UnitConversionThread actualizada y movida al nivel superior
class UnitConversionThread(QThread):
    """Clase QThread para manejar la conversión de unidades en segundo plano."""
    conversion_finished = pyqtSignal(str)
    text_captured = pyqtSignal(str)  # Nueva señal para el texto capturado

    def run(self):
        """Capturar la entrada de voz y realizar la conversión de unidades."""
        texto = take_user_input()
        if texto and texto != 'None':
            self.text_captured.emit(texto)  # Emitir el texto capturado
            resultado = unit_conversion(texto)
            self.conversion_finished.emit(resultado)
        else:
            self.conversion_finished.emit("No se capturó ninguna entrada de voz.")
            speak("No se capturó ninguna entrada de voz.")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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
            "Consultar Año",  # Renombrado de "Buscar en Wikipedia"
            "Traducir",
            "Conversión de Unidades",
            "Salir"
        ])
        self.option_selector.currentIndexChanged.connect(self.handle_option_selection)
        self.layout.addWidget(self.option_selector)

        # Área de salida de texto
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        self.setLayout(self.layout)

        # Inicializar referencias a las ventanas de traducción y conversión
        self.translation_window = None
        self.unit_conversion_window = None

    def handle_option_selection(self, index):
        """Manejar la selección de una opción desde el ComboBox."""
        if index == 0:
            return  # "Selecciona una opción" seleccionado, no hacer nada

        option = self.option_selector.currentText()
        self.option_selector.setCurrentIndex(0)  # Reiniciar al valor por defecto

        # Ejecutar el comando correspondiente en un hilo separado
        import threading
        thread = threading.Thread(target=self.execute_command, args=(option,))
        thread.start()

    def execute_command(self, command):
        """Ejecutar el comando seleccionado."""
        if command == "Reproducir Música":
            speak("¿Qué canción te gustaría escuchar?")
            music = take_user_input()
            if music and music != 'None':
                play_music(music)
        elif command == "Consultar Cultura":
            speak("¿De qué estado te gustaría conocer la cultura?")
            estado = take_user_input()
            if estado and estado != 'None':
                cultura_info = consultar_estado(estado)
                speak(cultura_info)
                self.output_area.append(f"Cultura de {estado}: {cultura_info}")
        elif command == "Contar Chistes":
            contar_chiste()
            self.output_area.append("Contando chiste...")
        elif command == "Resolver Operación Matemática":
            speak("Por favor, dime la operación que quieres resolver.")
            operacion = take_user_input()
            if operacion and operacion != 'None':
                res = resolver_operacion(operacion)
                if res is not None:
                    speak(f"El resultado es {res}")
                    self.output_area.append(f"Operación: {operacion} = {res}")
                else:
                    speak("No pude entender bien tu pregunta. Por favor, repítela de nuevo.")
                    self.output_area.append("No se pudo resolver la operación.")
        elif command == "Consultar Año":  # Renombrado de "Buscar en Wikipedia"
            speak("¿Sobre qué tema te gustaría consultar el año?")
            tema = take_user_input()
            if tema and tema != 'None':
                try:
                    wikipedia.set_lang('es')  # Establecer el idioma en español
                    resultados = wikipedia.summary(tema, sentences=2, auto_suggest=False)
                    speak(f"De acuerdo con Wikipedia: {resultados}")
                    self.output_area.append(f"Resultados de Wikipedia:\n{resultados}")
                except wikipedia.exceptions.DisambiguationError as e:
                    speak("El término es ambiguo. Por favor, proporciona más detalles.")
                    self.output_area.append("Error de ambigüedad en Wikipedia.")
                except wikipedia.exceptions.PageError:
                    speak("No se encontró ninguna página para ese término en Wikipedia.")
                    self.output_area.append("Página no encontrada en Wikipedia.")
                except Exception as e:
                    speak("Ocurrió un error al consultar Wikipedia.")
                    self.output_area.append(f"Error al consultar Wikipedia: {e}")
        elif command == "Traducir":
            self.open_translation_window()
        elif command == "Conversión de Unidades":
            self.open_unit_conversion_window()
        elif command == "Salir":
            speak("¡Hasta luego!")
            logging.info("Aplicación cerrada por el usuario.")
            QApplication.quit()

    def open_translation_window(self):
        """Abrir la ventana de traducción."""
        if self.translation_window is None:
            self.translation_window = TranslationWindow()
        self.translation_window.show()

    def open_unit_conversion_window(self):
        """Abrir la ventana de conversión de unidades."""
        if self.unit_conversion_window is None:
            self.unit_conversion_window = UnitConversionWindow()
        self.unit_conversion_window.show()

class TranslationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traducción de Texto")
        self.resize(400, 300)
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
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text)

        self.setLayout(self.layout)

    def populate_languages(self):
        """Poblar el selector de idiomas con los idiomas disponibles."""
        # Lista actualizada de idiomas y sus códigos
        languages = {
            "Español": "es",
            "Inglés": "en",
            "Francés": "fr",
            "Alemán": "de",
            "Italiano": "it",
            "Portugués": "pt",
            "Chino": "zh-cn",
            "Japonés": "ja",
            "Ruso": "ru",
            "Árabe": "ar"
        }
        for lang, code in languages.items():
            self.lang_selector.addItem(f"{lang} ({code})", code)

    def capture_voice_input(self):
        """Capturar la entrada de voz y mostrarla en el área de texto original."""
        speak("Por favor, habla ahora.")
        texto = take_user_input()
        if texto and texto != 'None':
            self.input_text.setText(texto)
        else:
            speak("No se capturó ninguna entrada de voz.")
            self.output_text.setText("No se capturó ninguna entrada de voz.")

    def translate_text(self):
        """Traducir el texto de entrada al idioma seleccionado."""
        original_text = self.input_text.toPlainText()
        selected_lang_code = self.lang_selector.currentData()

        if original_text:
            speak("Traduciendo el texto...")
            translated_text = translate_text_function(original_text, selected_lang_code)
            if translated_text:
                self.output_text.setText(translated_text)
                speak(translated_text)
            else:
                self.output_text.setText("Error en la traducción.")
        else:
            speak("No hay texto para traducir.")
            self.output_text.setText("No hay texto para traducir.")

class UnitConversionWindow(QWidget):
    def __init__(self):
        super().__init__()
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
        self.thread = UnitConversionThread()
        self.thread.text_captured.connect(self.display_captured_text)  # Conectar nueva señal
        self.thread.conversion_finished.connect(self.handle_conversion_result)
        self.thread.start()

    def display_captured_text(self, texto):
        """Mostrar el texto capturado en la interfaz."""
        self.audioCapturadoLabel.setText(f"Texto capturado: {texto}")

    def handle_conversion_result(self, resultado):
        """Manejar el resultado de la conversión de unidades."""
        # Actualizar la interfaz gráfica
        self.respuestaObtenidaLabel.setText(f"Resultado: {resultado}")
        speak(resultado)

        # Resetear el botón
        self.startRecordingBtn.setText("Empezar")
        self.startRecordingBtn.setStyleSheet("background-color: green; color: white; font-size: 16px;")
        self.startRecordingBtn.setEnabled(True)

# FUNCIONES ÚTILES

def play_music(song):
    """Reproducir una canción en YouTube."""
    try:
        pywhatkit.playonyt(song)
        speak(f"Reproduciendo {song}")
        logging.info(f"Reproduciendo música: {song}")
    except Exception as e:
        speak("No pude reproducir la música.")
        logging.error(f"Error al reproducir música: {e}")

# APLICACIÓN PRINCIPAL

if __name__ == "__main__":
    app = QApplication(sys.argv)         # Crear la aplicación PyQt5
    window = MainWindow()                # Crear la ventana principal
    window.show()                        # Mostrar la ventana principal
    greet_user()                         # Saludo inicial
    sys.exit(app.exec())                 # Iniciar el bucle de eventos
