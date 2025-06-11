import streamlit as st
import pandas as pd
import os
import bcrypt
import gdown
from datetime import datetime
from io import StringIO

# === CONFIG ===
FOLDER_URL = "https://drive.google.com/drive/folders/1tBpyY1VFi-hTxTWWlow4dE0PXrvV7Pvs"
USERS_FILE = "users.csv"

# === FUNZIONI ===
@st.cache_data
def carica_utenti():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            df = pd.read_csv(f)
        return df
    except FileNotFoundError:
        st.error("⚠️ File utenti non trovato.")
        return pd.DataFrame()

def check_login(user, pwd, df_users):
    if user in df_users["username"].values:
        user_row = df_users[df_users["username"] == user].iloc[0]
        return bcrypt.checkpw(pwd.encode(), user_row["password_hash"].encode()), user_row["ruolo"]
    return False, None

def elenca_file_csv():
    files = [f for f in os.listdir("rapporti") if f.endswith(".csv")]
    return sorted(files, reverse=True)

# === UI LOGIN ===
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
            users_df = carica_utenti()
            success, ruolo = check_login(username, password, users_df)
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
    files = elenca_file_csv()
    if st.session_state.ruolo != "admin":
        files = [f for f in files if f.lower().endswith(f"{st.session_state.user.lower()}.csv")]

    file_sel = st.selectbox("📅 Seleziona un giorno", files)
    if file_sel:
        df = pd.read_csv(os.path.join("rapporti", file_sel))
        st.subheader("🧾 Dettaglio attività")
        st.dataframe(df)

        if "app" in df.columns:
            top_apps = df["app"].value_counts().head(5)
            st.subheader("📈 App più usate")
            st.bar_chart(top_apps)
