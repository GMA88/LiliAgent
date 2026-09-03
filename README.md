# 🤖 LiliAgent

Un agente inteligente desarrollado en Python diseñado para automatizar tareas y proporcionar asistencia conversacional. LiliAgent es un sistema basado en IA que puede procesar comandos, realizar análisis y responder consultas complejas.

## ✨ Características

- **Procesamiento de Lenguaje Natural**: Comprensión y análisis de texto
- **Automatización de Tareas**: Ejecución automática de operaciones complejas
- **Interfaz Conversacional**: Chat inteligente y respuestas contextuales
- **Extensible**: Fácil de extender con nuevas capacidades y módulos
- **Logging y Monitoreo**: Sistema completo de registros y auditoría

## 🛠️ Tecnologías

- **Lenguaje**: Python 3.8+
- **Librerías principales**:
  - `nltk` - Procesamiento de lenguaje natural
  - `requests` - Llamadas HTTP a APIs
  - `logging` - Sistema de logs
  - `json` - Manejo de datos JSON

## 📦 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GMA88/LiliAgent.git
cd LiliAgent
```

2. Crear entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🎯 Uso Rápido

### Ejecutar el Agente

```bash
python main.py
```

### Ejemplo de Código

```python
from lili_agent import LiliAgent

# Inicializar el agente
agent = LiliAgent(name="Lili", verbose=True)

# Procesar comando
response = agent.process_command("¿Cuál es la capital de Francia?")
print(response)

# Iniciar modo conversacional
agent.start_chat()
```

### Ejemplos de Comandos

```
> Hola Lili
Agent: ¡Hola! Soy Lili, tu asistente virtual. ¿Cómo puedo ayudarte?

> ¿Qué hora es?
Agent: La hora actual es [timestamp]

> Búscame información sobre Python
Agent: Buscando información sobre Python...
```

## 📁 Estructura del Proyecto

```
LiliAgent/
├── lili_agent/
│   ├── __init__.py
│   ├── agent.py              # Clase principal del agente
│   ├── nlp_processor.py       # Procesamiento de lenguaje
│   ├── commands/              # Comandos disponibles
│   └── utils/                 # Utilidades
├── tests/                     # Tests unitarios
├── config/                    # Configuración
├── requirements.txt           # Dependencias
├── main.py                    # Punto de entrada
└── README.md                  # Este archivo
```

## 🔧 Configuración

Editar `config/config.json`:

```json
{
  "agent": {
    "name": "Lili",
    "language": "es",
    "debug_mode": false
  },
  "api": {
    "timeout": 30,
    "retries": 3
  }
}
```

## 📚 Funcionalidades Principales

### 1. Procesamiento de Comandos
```python
agent.register_command("weather", get_weather)
```

### 2. Análisis de Sentimientos
```python
sentiment = agent.analyze_sentiment("Me encanta este proyecto")
```

### 3. Búsqueda de Información
```python
results = agent.search("machine learning")
```

## 🧪 Pruebas

Ejecutar suite de tests:

```bash
pytest tests/
```

Ejecución con cobertura:

```bash
pytest --cov=lili_agent tests/
```

## 📝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Ejecutar tests para verificar integridad
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abrir un Pull Request

## 🐛 Reporte de Bugs

Reporta bugs abriendo un [Issue](https://github.com/GMA88/LiliAgent/issues) con:
- Descripción clara del problema
- Pasos para reproducirlo
- Versión de Python y dependencias
- Logs relevantes

## 📚 Documentación

- [Guía de Instalación](docs/INSTALL.md)
- [Guía de Uso](docs/USAGE.md)
- [API Reference](docs/API.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE). Ver archivo `LICENSE` para más detalles.

## 👥 Autor

**GMA88** - [GitHub Profile](https://github.com/GMA88)

## 🙏 Agradecimientos

Agradecimientos a la comunidad open-source de Python y a todos los contribuidores.

## 💬 Soporte

Para soporte, contacta a través de [Issues](https://github.com/GMA88/LiliAgent/issues) o abre una [Discussion](https://github.com/GMA88/LiliAgent/discussions).

---

⭐ Si este proyecto te fue útil, considera darle una estrella

---

# 🤖 LiliAgent (English)

An intelligent agent developed in Python designed to automate tasks and provide conversational assistance. LiliAgent is an AI-based system that can process commands, perform analysis, and respond to complex queries.

## ✨ Features

- **Natural Language Processing**: Text comprehension and analysis
- **Task Automation**: Automatic execution of complex operations
- **Conversational Interface**: Smart chat and contextual responses
- **Extensible**: Easy to extend with new capabilities and modules
- **Logging and Monitoring**: Complete logging and audit system

## 🛠️ Technologies

- **Language**: Python 3.8+
- **Main Libraries**:
  - `nltk` - Natural language processing
  - `requests` - HTTP API calls
  - `logging` - Logging system
  - `json` - JSON data handling

## 📦 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/GMA88/LiliAgent.git
cd LiliAgent
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

## 🎯 Quick Start

### Run the Agent

```bash
python main.py
```

### Code Example

```python
from lili_agent import LiliAgent

# Initialize the agent
agent = LiliAgent(name="Lili", verbose=True)

# Process command
response = agent.process_command("What is the capital of France?")
print(response)

# Start conversational mode
agent.start_chat()
```

### Example Commands

```
> Hello Lili
Agent: Hello! I'm Lili, your virtual assistant. How can I help you?

> What time is it?
Agent: The current time is [timestamp]

> Search for information about Python
Agent: Searching for information about Python...
```

## 📁 Project Structure

```
LiliAgent/
├── lili_agent/
│   ├── __init__.py
│   ├── agent.py              # Main agent class
│   ├── nlp_processor.py       # Language processing
│   ├── commands/              # Available commands
│   └── utils/                 # Utilities
├── tests/                     # Unit tests
├── config/                    # Configuration
├── requirements.txt           # Dependencies
├── main.py                    # Entry point
└── README.md                  # This file
```

## 🔧 Configuration

Edit `config/config.json`:

```json
{
  "agent": {
    "name": "Lili",
    "language": "en",
    "debug_mode": false
  },
  "api": {
    "timeout": 30,
    "retries": 3
  }
}
```

## 📚 Main Features

### 1. Command Processing
```python
agent.register_command("weather", get_weather)
```

### 2. Sentiment Analysis
```python
sentiment = agent.analyze_sentiment("I love this project")
```

### 3. Information Search
```python
results = agent.search("machine learning")
```

## 🧪 Testing

Run test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=lili_agent tests/
```

## 📝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Run tests to verify integrity
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 🐛 Bug Reports

Report bugs by opening an [Issue](https://github.com/GMA88/LiliAgent/issues) with:
- Clear problem description
- Steps to reproduce
- Python version and dependencies
- Relevant logs

## 📚 Documentation

- [Installation Guide](docs/INSTALL.md)
- [Usage Guide](docs/USAGE.md)
- [API Reference](docs/API.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 📄 License

This project is licensed under the [MIT](LICENSE) license. See the `LICENSE` file for details.

## 👥 Author

**GMA88** - [GitHub Profile](https://github.com/GMA88)

## 🙏 Acknowledgments

Thanks to the Python open-source community and all contributors.

## 💬 Support

For support, contact via [Issues](https://github.com/GMA88/LiliAgent/issues) or open a [Discussion](https://github.com/GMA88/LiliAgent/discussions).

---

⭐ If this project was helpful to you, please consider giving it a star