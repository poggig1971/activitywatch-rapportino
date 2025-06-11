import streamlit as st
import pandas as pd
import os
import gdown
import bcrypt
from datetime import datetime

# === CONFIG ===
FOLDER_ID = "1tBpyY1VFi-hTxTWWlow4dE0PXrvV7Pvs"
FOLDER_URL = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
USERS_FILE = "users.csv"
RAPPORTI_DIR = "rapporti"

# === INIZIALIZZAZIONE ===
def crea_cartelle():
    if not os.path.exists(RAPPORTI_DIR):
        os.makedirs(RAPPORTI_DIR)

def scarica_tutti_i_csv():
    os.system(f"gdown --folder https://drive.google.com/drive/folders/{FOLDER_ID} -O ./ --quiet")
    for file in os.listdir("."):
        if file.endswith(".csv") and file != USERS_FILE:
            os.replace(file, os.path.join(RAPPORTI_DIR, file))

def scarica_users_csv():
    # Cerca il file users.csv scaricato da gdown
    if not os.path.exists(USERS_FILE):
        st.error("⚠️ Il file users.csv non è stato trovato nella cartella corrente.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(USERS_FILE)
        if "username" not in df.columns:
            st.error("⚠️ Il file utenti non contiene la colonna 'username'.")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"❌ Errore lettura users.csv: {e}")
        return pd.DataFrame()

def check_login(user, pwd, df_users):
    # Accesso garantito all'admin "poggi" con password "123"
    if user == "poggi" and pwd == "123":
        return True, "admin"

    if "username" not in df_users.columns or "password_hash" not in df_users.columns:
        return False, None

    if user in df_users["username"].values:
        user_row = df_users[df_users["username"] == user].iloc[0]
        return bcrypt.checkpw(pwd.encode(), user_row["password_hash"].encode()), user_row["ruolo"]

    return False, None

def elenca_file_csv(user, ruolo):
    files = [f for f in os.listdir(RAPPORTI_DIR) if f.endswith(".csv")]
    if ruolo != "admin":
        files = [f for f in files if user.lower() in f.lower()]
    return sorted(files, reverse=True)

# === AVVIO ===
crea_cartelle()
scarica_tutti_i_csv()

# === STREAMLIT UI ===
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
            df_utenti = scarica_users_csv()
            success, ruolo = check_login(username, password, df_utenti)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.ruolo = ruolo
                st.success("Accesso effettuato con successo")
                st.rerun()
            else:
                st.error("Credenziali non valide")

else:
    st.sidebar.success(f"Sei connesso come: {st.session_state.user} ({st.session_state.ruolo})")
    files = elenca_file_csv(st.session_state.user, st.session_state.ruolo)
    file_sel = st.selectbox("📅 Seleziona un giorno", files)

    if file_sel:
        df = pd.read_csv(os.path.join(RAPPORTI_DIR, file_sel))
        st.subheader("🧾 Dettaglio attività")
        st.dataframe(df)

        if "app" in df.columns:
            top_apps = df["app"].value_counts().head(5)
            st.subheader("📈 App più usate")
            st.bar_chart(top_apps)
