# 📍 Geo Access Logger

**Geo Access Logger** é uma aplicação web simples construída com **Streamlit**, projetada para **capturar e registrar dados de geolocalização de usuários**. O sistema combina informações do navegador (com permissão do usuário) e localização por IP (usando o serviço [ipinfo.io](https://ipinfo.io)).

Este projeto foi desenvolvido com **fins educacionais**, como demonstração de técnicas de geolocalização via navegador e serviços externos em aplicações web.

---

## 🌐 Funcionalidades

- 📌 Captura de geolocalização do navegador (via `navigator.geolocation`) **requer permissão do usuário**
- 🌍 Captura de localização com base no IP usando [ipinfo.io](https://ipinfo.io)
- ☁️ Armazenamento seguro dos dados em banco **MongoDB Atlas**
- 🧾 Simulação de uso real: botão fictício para "Emitir Nota Fiscal Eletrônica", acionando a geolocalização

---

## ⚙️ Requisitos

- Conta no [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Arquivo `.streamlit/secrets.toml` configurado (veja abaixo)
- Dependências listadas no `pyproject.toml`
- Gerenciador de pacotes [uv](https://github.com/astral-sh/uv)

---

## 🚀 Instalação

```bash
# 1. Clone este repositório
git clone https://github.com/PetronioValentini/geo-access-logger.git
cd geo-access-logger

# 2. Instale as dependências
uv sync

# 3. Configure o arquivo de credenciais
# .streamlit/secrets.toml
[mongo]
cluster_url = "mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
db_name = "nome_do_banco"

# 4. Edite as variáveis no arquivo variaveis.py
# TITULO_PAGINA = "Seu título personalizado"
# LEGENDA = "Descrição da simulação de NF-e..."

# 5. Rode a aplicação localmente
uv run streamlit run main.py

# 6. Envie para cloud com streamlit cloud

# 7. Utilize o site "https://grabify.org/br/ip-grabber/" para encurtar e armazenar o IP do visitante

```

## 🛠 Tech Stack Used
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)