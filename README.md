# 📍 Geo Access Logger

**Geo Access Logger** is a simple web application built with **Streamlit**, designed to **capture and log user geolocation data**. The system combines browser-based location (with user permission) and IP-based geolocation using the [ipinfo.io](https://ipinfo.io) service.

This project was developed **for educational purposes**, as a demonstration of geolocation techniques using the browser and external services in web applications.

---

## 🌐 Features

- 📌 Geolocation capture using the browser (via `navigator.geolocation`) — **requires user permission**
- 🌍 Location capture based on IP address using [ipinfo.io](https://ipinfo.io)
- ☁️ Secure storage of location data in a **MongoDB Atlas** database
- 🧾 Realistic simulation: a fake "Emit Electronic Invoice" button triggers geolocation collection

---

## ⚙️ Requirements

- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account
- Properly configured `.streamlit/secrets.toml` file (see below)
- Dependencies listed in `pyproject.toml`
- [uv](https://github.com/astral-sh/uv) package manager

---

## 🚀 Installation

```bash
# 1. Clone this repository
git clone https://github.com/PetronioValentini/geo-access-logger.git
cd geo-access-logger

# 2. Install dependencies
uv sync

# 3. Configure MongoDB credentials in the secrets file
# .streamlit/secrets.toml
[mongo]
cluster_url = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
db_name = "your_database_name"

# 4. Edit variables in variaveis.py
# TITULO_PAGINA = "Your custom page title"
# LEGENDA = "Description of the NF-e simulation..."

# 5. Run the application locally
uv run streamlit run main.py

# 6. Deploy using Streamlit Cloud

# 7. (Optional) Use "https://grabify.org/" to shorten and track access to the app


```

## 🛠 Tech Stack Used
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)