import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import socket

st.set_page_config(page_title="Rapportino Giornaliero", layout="wide")
st.title("🕵️‍♂️ Monitoraggio attività PC – Rapportino giornaliero")

# === CONFIGURAZIONE BASE ===
hostname = socket.gethostname()
BASE_URL = f"http://localhost:5600/api/0/buckets/aw-watcher-window_{hostname}/events"

# === INTERVALLO DI ANALISI ===
oggi = datetime.now()
ieri = oggi - timedelta(days=1)

start_time = ieri.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
end_time = oggi.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

params = {"start": start_time, "end": end_time}

try:
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Elabora dati
    logs = []
    for item in data:
        timestamp = item["timestamp"]
        durata = item["duration"]
        app = item["data"]["app"]
        titolo = item["data"]["title"]
        logs.append([timestamp, durata, app, titolo])

    df = pd.DataFrame(logs, columns=["Inizio", "Durata (s)", "Applicazione", "Titolo finestra"])
    df["Inizio"] = pd.to_datetime(df["Inizio"])
    df["Durata (min)"] = df["Durata (s)"] / 60
    df_grouped = df.groupby("Applicazione")["Durata (min)"].sum().reset_index().sort_values(by="Durata (min)", ascending=False)

    st.subheader("⏱️ Tempo per applicazione")
    st.dataframe(df_grouped, use_container_width=True)

    st.subheader("📋 Dettaglio sessioni")
    st.dataframe(df[["Inizio", "Applicazione", "Titolo finestra", "Durata (min)"]], use_container_width=True)

except Exception as e:
    st.error(f"Errore durante la connessione a ActivityWatch: {e}")
