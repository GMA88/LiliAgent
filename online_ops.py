from wikidata.client import Client 
import pywhatkit as kit
from email.message import EmailMessage
from decouple import config
import json
import urllib
import wikipediaapi
import wikipedia

# Configura el agente de usuario
wikipedia.set_lang("es")
wikipedia.set_user_agent("Prometeo/1.0")

wikidata_client = Client()

def search_on_google(query):
    kit.search(query)


def search_on_wikipedia(query):    
 # Construye la URL del anexo específico en Wikipedia
    anexo_url = 'Anexo:México_en_' + query
    try:
        page = wikipedia.page(anexo_url)
        content = page.content
        # Encuentra la sección de "Acontecimientos"
        start_index = content.find("Acontecimientos")
        if start_index == -1:
            return "No se encontraron acontecimientos para este año."
        
        # Extrae el contenido de la sección de "Acontecimientos"
        end_index = content.find("Nacimientos", start_index)
        if end_index == -1:
            end_index = len(content)
        
        acontecimientos = content[start_index:end_index]
        
        # Filtra los eventos importantes
        eventos_importantes = []
        for line in acontecimientos.split('\n'):
            if 'de enero' in line or 'de febrero' in line or 'de marzo' in line or 'de abril' in line or 'de mayo' in line or 'de junio' in line or 'de julio' in line or 'de agosto' in line or 'de septiembre' in line or 'de octubre' in line or 'de noviembre' in line or 'de diciembre' in line:
                eventos_importantes.append(line.split('[')[0].strip())
        if not eventos_importantes:
            return "No se encontraron eventos importantes para este año."
        
        return "\n".join(eventos_importantes)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Se encontró una página de desambiguación: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No se encontró la página."
    except Exception as e:
        return f"Ocurrió un error: {e}"

def search_on_wikidata(query):
    # Busca el ítem en Wikidata
    query_complete = 'Eventos historicos de mexico en el año ' + query
    search_results = wikidata_client.search(query_complete, limit=1)
    
    if not search_results:
        return "No se encontraron resultados en Wikidata."
    
    # Obtiene el identificador del ítem de Wikidata
    wikidata_item = search_results[0]
    item_id = wikidata_item.id
    
    # Obtén la descripción del ítem
    item = wikidata_client.get(item_id, load=True)
    description = item.description
    
    if not description:
        return "No se encontró una descripción para este ítem."
    
    return description