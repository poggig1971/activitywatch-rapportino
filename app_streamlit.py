import streamlit as st
import pandas as pd
import os
from datetime import datetime
import bcrypt

# === CONFIG ===
FOLDER_ID = "1tBpyY1VFi-hTxTWWlow4dE0PXrvV7Pvs"
RAPPORTI_DIR = "rapporti"

# === UTENTI DEFINITI NEL CODICE ===
USERS = {
    "poggi": {"password": "123", "ruolo": "admin"},
    "gosmar": {"password": "123", "ruolo": "user"},
    "mihu": {"password": "123", "ruolo": "user"},
    "tiziano": {"password": "123", "ruolo": "user"},
    "vale": {"password": "123", "ruolo": "user"},
    "gino": {"password": "123", "ruolo": "user"},
}

# === UTILITY ===
def crea_cartella():
    if not os.path.exists(RAPPORTI_DIR):
        os.makedirs(RAPPORTI_DIR)

def check_login(username, password):
    user = USERS.get(username)
    if user and password == user["password"]:
        return True, user["ruolo"]
    return False, None

def elenca_file_csv(user, ruolo):
    files = [f for f in os.listdir(RAPPORTI_DIR) if f.endswith(".csv")]
    if ruolo != "admin":
        files = [f for f in files if user.lower() in f.lower()]
    return sorted(files, reverse=True)

# === AVVIO ===
crea_cartella()

# === UI ===
st.set_page_config(page_title="Dashboard Rapportini", layout="wide")
st.title("📊 Dashboard Rapportini Attività")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.ruolo = ""

if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Nome utente")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Accedi")
        if submit:
            success, ruolo = check_login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.ruolo = ruolo
                st.success("Accesso effettuato con successo")
                st.rerun()
            else:
                st.error("Credenziali non valide")

else:
    username = st.session_state.user
    ruolo = st.session_state.ruolo
    st.sidebar.success(f"Sei connesso come: {username} ({ruolo})")

    # Upload CSV personale
    st.subheader("📤 Carica il tuo file CSV")
    uploaded_file = st.file_uploader("Seleziona un file .csv", type="csv")
    if uploaded_file:
        today = datetime.now().strftime("%Y.%m.%d")
        filename = f"{today}_{username}.csv"
        save_path = os.path.join(RAPPORTI_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File caricato come: {filename}")
        st.rerun()

    # Visualizzazione file disponibili
    st.subheader("📂 Seleziona un giorno")
    files = elenca_file_csv(username, ruolo)
    if not files:
        st.warning("⚠️ Nessun file CSV trovato.")
    else:
        file_sel = st.selectbox("📅 Giorno disponibile", files)
        if file_sel:
            df = pd.read_csv(os.path.join(RAPPORTI_DIR, file_sel))
            st.dataframe(df)
            if "app" in df.columns:
                top_apps = df["app"].value_counts().head(5)
                st.subheader("📈 App più usate")
                st.bar_chart(top_apps)
            st.subheader("📈 App più usate")
            st.bar_chart(top_apps)
