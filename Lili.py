import sys
import os
import tempfile
import pyttsx3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import QThread, pyqtSignal
import whisper
import speech_recognition as sr
from pydub import AudioSegment
from dateparser import parse
import pywhatkit
import keyboard
from pycaw.pycaw import AudioUtilities
from gtts import gTTS
from io import BytesIO
import pygame
from pint import UnitRegistry
import time
import random
import re
from datetime import datetime
import mysql.connector  # Para la conexión con la base de datos MySQL
#from functions.online_ops import search_on_wikipedia  # Importar para buscar en Wikipedia

# Variables globales para controlar el idioma, reintentos y estado
retry_count = 0
MAX_RETRY = 5
ureg = UnitRegistry()
current_language = 'es-MX'  # Idioma predeterminado
tts_voice_language = 'es'  # Idioma para TTS

USERNAME = 'Usuario'
BOTNAME = 'Lili'

# Inicializa el motor de texto a voz (pyttsx3) y configura sus propiedades
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 190)
engine.setProperty('volume', 100.0)

def set_voice_language(language_code):
    """Cambia el idioma de la voz del asistente."""
    voices = engine.getProperty('voices')
    if language_code == 'en':
        engine.setProperty('voice', voices[1].id)  # Cambiar a voz en inglés (si está disponible)
    elif language_code == 'es':
        engine.setProperty('voice', voices[0].id)  # Cambiar a voz en español (si está disponible)

def speak(text):
    print(f"{BOTNAME}: {text}")
    engine.say(text)
    engine.runAndWait()

# Greet the user based on the time of day
def greet_user():
    hour = datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Buenos días {USERNAME}")
    elif (hour >= 12) and (hour < 16):
        speak(f"Buenas tardes {USERNAME}")
    elif (hour >= 16) and (hour < 19):
        speak(f"Buenas noches {USERNAME}")
    speak(f"Yo soy {BOTNAME}. ¿Cómo puedo asistirte hoy?")

def play_music(song):
    try:
        # Utiliza pywhatkit para reproducir una canción en YouTube basada en el nombre o enlace
        pywhatkit.playonyt(song)
        speak("Reproduciendo " + song)
    except Exception as e:
        print("No se pudo reproducir la música debido a:", e)
        speak("Error al intentar reproducir la música.")

# Take voice input from the user
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
    except Exception:
        speak('Disculpa, no he podido entender. ¿Podrías repetirlo?')
        query = 'None'
    return query

# Conectar a MySQL
def conectar_base_datos():
    conexion = mysql.connector.connect(
        user="root",
        password="#Lalo200903",
        host="localhost",
        database="agente",
        port='3306'
    )
    return conexion

# Consultar la cultura de un estado
def consultar_estado(estado):
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)
    consulta_sql = "SELECT cultura FROM info WHERE estado = %s"
    cursor.execute(consulta_sql, (estado,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado['cultura']
    else:
        return "No tengo información sobre ese estado."

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
        self.wiki_action = QAction("Buscar en Wikipedia", self)
        self.wiki_action.triggered.connect(lambda: self.execute_command("buscar"))
        self.joke_action = QAction("Contar Chistes", self)
        self.joke_action.triggered.connect(lambda: self.execute_command("chiste"))
        self.convert_action = QAction("Conversión de Unidades", self)
        self.convert_action.triggered.connect(lambda: self.execute_command("convertir"))
        self.exit_action = QAction("Salir", self)
        self.exit_action.triggered.connect(self.close)

        # Menú para cambiar de idioma
        self.language_menu = self.menubar.addMenu("Cambiar Idioma")
        self.spanish_action = QAction("Español", self)
        self.spanish_action.triggered.connect(lambda: self.change_language('es-MX', 'es'))
        self.english_action = QAction("Inglés", self)
        self.english_action.triggered.connect(lambda: self.change_language('en-US', 'en'))

        # Añadir las acciones al menú
        self.menu.addAction(self.reproduce_action)
        self.menu.addAction(self.culture_action)
        self.menu.addAction(self.math_action)
        self.menu.addAction(self.wiki_action)
        self.menu.addAction(self.joke_action)
        self.menu.addAction(self.convert_action)
        self.menu.addAction(self.exit_action)

        # Añadir opciones de idioma al menú
        self.language_menu.addAction(self.spanish_action)
        self.language_menu.addAction(self.english_action)

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
        speak("Las opciones disponibles son:")
        speak("Reproducir música, Consultar cultura, Resolver operación matemática, Buscar en Wikipedia, Contar chistes, Conversión de unidades.")

    def change_language(self, voice_code, tts_code):
        """Función para cambiar el idioma del asistente"""
        global current_language, tts_voice_language
        current_language = voice_code  # Cambia el idioma para el reconocimiento de voz
        tts_voice_language = tts_code  # Cambia el idioma para el TTS
        set_voice_language(tts_code)  # Cambiar la voz del asistente
        speak(f"El idioma ha sido cambiado a {'español' if tts_code == 'es' else 'inglés'}.")

    def execute_command(self, command):
        if command == "reproduce":
            speak("¿Qué canción te gustaría escuchar?")
            music = take_user_input()
            play_music(music)
        elif command == "cultura":
            speak("¿De qué estado te gustaría conocer la cultura?")
            estado = take_user_input()
            cultura_info = consultar_estado(estado)
            speak(cultura_info)
            self.output_area.append(f"Cultura de {estado}: {cultura_info}")
        elif command == "matemáticas":
            speak("¿Cuál es la operación matemática que quieres resolver?")
            operation = take_user_input()
            solve_math(operation)
        elif command == "buscar":
            speak("¿Qué quieres buscar en Wikipedia?")
            term = take_user_input()
            search_information(term)
        elif command == "chiste":
            tell_joke()
        elif command == "convertir":
            speak("¿Qué unidad quieres convertir?")
            conversion = take_user_input()
            handle_conversion(conversion)

# Procesar varios comandos de usuario
def process_command(command):
    if 'reproduce' in command:
        play_music(command)
    elif 'cultura de' in command:
        estado = command.replace('cultura de', '').strip()
        cultura_info = consultar_estado(estado)
        speak(cultura_info)
        window.output_area.append(f"Cultura de {estado}: {cultura_info}")
    elif 'cuánto es' in command:
        solve_math(command)
    elif 'busca' in command:
        search_information(command)
    elif 'chiste' in command:
        tell_joke(command)
    elif 'convierte' in command:
        handle_conversion(command)

# Función principal para inicializar el programa
if __name__ == "__main__":
    greet_user()  # Saludo inicial
    app = QApplication(sys.argv)  # Crear la aplicación PyQt
    window = MainWindow()  # Crear la ventana principal
    window.show()  # Mostrar la ventana
    sys.exit(app.exec_())  # Iniciar el bucle principal de la aplicación
