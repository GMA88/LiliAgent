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