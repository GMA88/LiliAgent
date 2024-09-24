import sys
import pyttsx3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QMenuBar, QAction)
import speech_recognition as sr
import pywhatkit
from datetime import datetime
import mysql.connector
import random
import requests
import wikipedia
from gtts import gTTS
import os
import time
from wikidata.client import Client
from tkinter import messagebox
from googletrans import Translator
#from functions.online_ops import search_on_google, search_on_wikipedia, search_on_wikidata 

# Variables globales para controlar el idioma y estado
current_language = 'es-MX'  # Idioma predeterminado
tts_voice_language = 'es'  # Idioma para TTS
is_listening = False
retry_count = 0
MAX_RETRY = 5
original_text = ''

USERNAME = 'Usuario'
BOTNAME = 'Lili'

# Inicializa el motor de texto a voz (pyttsx3) y configura sus propiedades
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.setProperty('volume', 100.0)

# Cambiar la voz a Sabina si está disponible
voices = engine.getProperty('voices')
for voice in voices:
    if 'Sabina' in voice.name:
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    """Texto a voz"""
    print(f"{BOTNAME}: {text}")
    engine.say(text)
    engine.runAndWait()

# Saluda al usuario basado en la hora del día
def greet_user():
    hour = datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Buenos días {USERNAME}")
    elif (hour >= 12) and (hour < 16):
        speak(f"Buenas tardes {USERNAME}")
    else:
        speak(f"Buenas noches {USERNAME}")
    speak(f"Yo soy {BOTNAME}. ¿Cómo puedo asistirte hoy?")

# Función para tomar la entrada de voz del usuario
def take_user_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Escuchando....')
        audio = r.listen(source)

    try:
        print('Reconociendo...')
        query = r.recognize_google(audio, language=current_language)  # Cambia según el idioma seleccionado
        print(query)
        if 'para' in query or 'detente' in query:
            speak('¡Tenga un buen día!')
            exit()
    except sr.UnknownValueError:
        speak('Disculpa, no he podido entender. ¿Podrías repetirlo?')
        query = 'None'
    return query

# Función para reproducir música en YouTube
def play_music(song):
    try:
        pywhatkit.playonyt(song)
        speak(f"Reproduciendo {song}")
    except Exception as e:
        print(f"Error al reproducir música: {e}")
        speak("No pude reproducir la música.")

# Conectar a MySQL
def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            user="root",
            password="1234",
            host="127.0.0.1",
            database="agente",
            port='3306'
        )
        return conexion
    except mysql.connector.Error as err:
        speak(f"Error al conectar a la base de datos: {err}")
        return None

# Consultar la cultura de un estado
def consultar_estado(estado):
    conexion = conectar_base_datos()
    if conexion is None:
        return "No se pudo conectar a la base de datos."
    
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

# Función para contar un chiste
def contar_chiste():
    jokes = ["¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
             "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!", 
             "Sí los zombies se deshacen con el paso del tiempo, ¿zombiodegradables?"]
    chiste = random.choice(jokes)
    speak(chiste)
    
#Funcion para traducir
# Instanciar el traductor
translator = Translator()

# Función para traducir el texto
def translate_text(original_text, target_lang, translation_output):
     if original_text:
        try:
            # Traducir el texto
            translation = translator.translate(original_text, dest=target_lang).text
            # Insertar la traducción en el widget de salida
            translation_output.insert('end', f"Traducción: {translation}\n")
        except Exception as e:
            messagebox.showerror("Error de traducción", f"Error en la traducción: {e}")

# ===================== NUEVAS FUNCIONES =====================

# Función para buscar información en Google
def buscar_en_google(query):
    try:
        search_on_google(query)
        speak(f"Buscando en Google: {query}")
    except Exception as e:
        speak(f"Ocurrió un error al buscar en Google: {e}")

# Función para buscar eventos históricos en Wikipedia
def buscar_eventos_wikipedia(query):
    try:
        resultados = search_on_wikipedia(query)
        speak(f"De acuerdo con Wikipedia: {resultados}")
        return resultados
    except Exception as e:
        speak(f"Error al buscar en Wikipedia: {e}")
        return None

# Función para buscar eventos en Wikidata
def buscar_eventos_wikidata(query):
    try:
        resultados = search_on_wikidata(query)
        speak(f"De acuerdo con Wikidata: {resultados}")
        return resultados
    except Exception as e:
        speak(f"Error al buscar en Wikidata: {e}")
        return None

# ===================== FIN NUEVAS FUNCIONES =====================

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asistente de Voz - Lili")
        self.layout = QVBoxLayout()

        # Menú para las funcionalidades del asistente
        self.menubar = QMenuBar(self)
        self.menu = self.menubar.addMenu("Opciones")

        # Crear acciones para cada funcionalidad
        self.reproduce_action = QAction("Reproducir Música", self)
        self.reproduce_action.triggered.connect(lambda: self.execute_command("reproduce"))
        self.culture_action = QAction("Consultar Cultura", self)
        self.culture_action.triggered.connect(lambda: self.execute_command("cultura"))
        self.math_action = QAction("Resolver Operación", self)
        self.math_action.triggered.connect(lambda: self.execute_command("matemáticas"))
        self.joke_action = QAction("Contar Chistes", self)
        self.joke_action.triggered.connect(lambda: self.execute_command("chiste"))
        self.google_action = QAction("Buscar en Google", self)
        self.google_action.triggered.connect(self.handle_google_search)
        self.wikipedia_action = QAction("Buscar en Wikipedia", self)
        self.wikipedia_action.triggered.connect(self.handle_wikipedia_search)
        self.wikidata_action = QAction("Buscar en Wikidata", self)
        self.wikidata_action.triggered.connect(self.handle_wikidata_search)
        self.exit_action = QAction("Salir", self)
        self.exit_action.triggered.connect(self.close)

        # Añadir las acciones al menú
        self.menu.addAction(self.reproduce_action)
        self.menu.addAction(self.culture_action)
        self.menu.addAction(self.math_action)
        self.menu.addAction(self.joke_action)
        self.menu.addAction(self.google_action)
        self.menu.addAction(self.wikipedia_action)
        self.menu.addAction(self.wikidata_action)
        self.menu.addAction(self.exit_action)

        # Añadir barra de menú al layout
        self.layout.setMenuBar(self.menubar)

        # Área de texto para mostrar resultados
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        # Añadir área de texto al layout
        self.layout.addWidget(self.output_area)

        self.setLayout(self.layout)

        # Anunciar opciones disponibles
        self.announce_options()

    def announce_options(self):
        speak("Las opciones disponibles son: Reproducir música, Consultar cultura, Resolver operación matemática, Contar chistes, Buscar en Google, Wikipedia y Wikidata.")

    def execute_command(self, command):
        if command == "reproduce":
            speak("¿Qué canción te gustaría escuchar?")
            music = take_user_input()
            if music:
                play_music(music)
        elif command == "cultura":
            speak("¿De qué estado te gustaría conocer la cultura?")
            estado = take_user_input()
            if estado:
                cultura_info = consultar_estado(estado)
                speak(cultura_info)
                self.output_area.append(f"Cultura de {estado}: {cultura_info}")
        elif command == "chiste":
            contar_chiste()
            self.output_area.append("Contando chiste...")

    def handle_google_search(self):
        """Maneja la búsqueda en Google"""
        speak("¿Qué te gustaría buscar en Google?")
        query = take_user_input()
        if query:
            buscar_en_google(query)
            self.output_area.append(f"Búsqueda en Google: {query}")

    def handle_wikipedia_search(self):
        """Maneja la búsqueda de eventos históricos en Wikipedia"""
        speak("¿Qué año te gustaría consultar para eventos en Wikipedia?")
        query = take_user_input()
        if query:
            resultados = buscar_eventos_wikipedia(query)
            self.output_area.append(f"Eventos históricos en Wikipedia:\n{resultados}")

    def handle_wikidata_search(self):
        """Maneja la búsqueda de eventos históricos en Wikidata"""
        speak("¿Qué año te gustaría consultar para eventos en Wikidata?")
        query = take_user_input()
        if query:
            resultados = buscar_eventos_wikidata(query)
            self.output_area.append(f"Eventos históricos en Wikidata:\n{resultados}")

# Función principal para inicializar el programa
if __name__ == "__main__":
    greet_user()  # Saludo inicial
    app = QApplication(sys.argv)  # Crear la aplicación PyQt
    window = MainWindow()  # Crear la ventana principal
    window.show()  # Mostrar la ventana
    sys.exit(app.exec_())  # Iniciar el bucle principal de la aplicación
