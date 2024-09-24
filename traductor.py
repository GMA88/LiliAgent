import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
from gtts import gTTS
import os
import time
import threading
from googletrans import Translator

# Crear la ventana principal
root = tk.Tk()
root.title("Reconocimiento de voz y traducción")
root.geometry("600x400")

# Variables globales
recognition_active = False
listening = False
retry_count = 0
MAX_RETRY = 5
original_text = ""
translator = Translator()

# Elementos de la interfaz
status_label = tk.Label(root, text="Estado: No está grabando", font=("Arial", 12))
status_label.pack(pady=10)

language_select = tk.StringVar(value='es')
language_options = ['es', 'en', 'fr', 'de', 'it', 'pt']
language_menu = tk.OptionMenu(root, language_select, *language_options)
language_menu.pack()

output_text = tk.Text(root, height=5, width=50)
output_text.pack(pady=10)

translation_output = tk.Text(root, height=5, width=50)
translation_output.pack(pady=10)

flag_icon = tk.Label(root)
flag_icon.pack()

# Función para iniciar el reconocimiento de voz
def start_recognition():
    global recognition_active, listening, retry_count
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    def recognize():
        global original_text
        status_label.config(text="Estado: Escuchando...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                original_text = recognizer.recognize_google(audio, language=language_select.get())
                output_text.insert(tk.END, f"Texto original: {original_text}\n")
                translate_text()
                retry_count = 0
            except sr.RequestError as e:
                handle_network_error()
            except sr.UnknownValueError:
                status_label.config(text="No se entendió el audio")

    if not recognition_active:
        recognition_active = True
        threading.Thread(target=recognize).start()

# Función para detener el reconocimiento de voz
def stop_recognition():
    global recognition_active
    recognition_active = False
    status_label.config(text="Estado: Grabación detenida")

# Función para traducir el texto
def translate_text():
    global original_text
    if original_text:
        try:
            target_lang = language_select.get()
            translation = translator.translate(original_text, dest=target_lang).text
            translation_output.insert(tk.END, f"Traducción: {translation}\n")
        except Exception as e:
            messagebox.showerror("Error de traducción", f"Error en la traducción: {e}")

# Función para manejar errores de red y reintentos
def handle_network_error():
    global retry_count
    retry_count += 1
    if retry_count >= MAX_RETRY:
        status_label.config(text="Error de red. Número máximo de reintentos alcanzado.")
    else:
        status_label.config(text=f"Error de red. Reintentando... ({retry_count})")
        time.sleep(2)
        start_recognition()

# Función para reproducir la traducción en voz
def speak_translation():
    translation = translation_output.get("1.0", tk.END).strip()
    if translation:
        tts = gTTS(translation, lang=language_select.get())
        tts.save("output.mp3")
        os.system("start output.mp3")

# Función para actualizar la bandera según el idioma seleccionado
def update_flag():
    selected_language = language_select.get()
    flag_map = {
        'en': "EUA.jpeg",
        'fr': "Francia.jpeg",
        'de': "Alemania.jpeg",
        'it': "Italia.jpeg",
        'pt': "Brasil.jpeg"
    }
    flag_src = flag_map.get(selected_language, None)
    if flag_src:
        img = tk.PhotoImage(file=flag_src)
        flag_icon.config(image=img)
        flag_icon.image = img
    else:
        flag_icon.config(image='')

# Botones de control con colores neón
start_button = tk.Button(root, 
                         text="Iniciar", 
                         command=start_recognition,
                         font=("Arial", 14),
                         bg="#39FF14",  # Verde neón
                         fg="#000000",  # Texto en negro
                         activebackground="#00FF00",  # Color activo
                         activeforeground="#FFFFFF")  # Texto activo
start_button.pack(pady=10)

stop_button = tk.Button(root, 
                        text="Detener", 
                        command=stop_recognition,
                        font=("Arial", 14),
                        bg="#FF073A",  # Rojo neón
                        fg="#000000",  # Texto en negro
                        activebackground="#FF4500",  # Color activo
                        activeforeground="#FFFFFF")  # Texto activo
stop_button.pack(pady=10)

speak_button = tk.Button(root, 
                         text="Hablar Traducción", 
                         command=speak_translation,
                         font=("Arial", 14),
                         bg="#00FFFF",  # Azul neón
                         fg="#000000",  # Texto en negro
                         activebackground="#1E90FF",  # Color activo
                         activeforeground="#FFFFFF")  # Texto activo
speak_button.pack(pady=10)

language_select.trace("w", lambda *args: update_flag())

# Ejecutar la ventana
root.mainloop()