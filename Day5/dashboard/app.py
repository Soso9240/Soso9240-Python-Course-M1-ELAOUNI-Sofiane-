"""DevOps Monitoring Dashboard — Streamlit frontend."""

import os
import time
from collections import deque

import httpx
import pandas as pd
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="DevOps Monitoring Dashboard", layout="wide")
st.title("🖥️ DevOps Monitoring Dashboard")

tab_metrics, tab_servers = st.tabs(["📊 Métriques", "🌐 Serveurs"])


# --- Tab 1: live metrics ------------------------------------------------------

@st.cache_data(ttl=2)
def fetch_metrics() -> dict | None:
    """Fetch a metrics snapshot from the API. Cached for 2 seconds."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/metrics", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError:
        return None


with tab_metrics:
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = deque(maxlen=60)  # last 60 seconds

    data = fetch_metrics()

    if data is None:
        st.error(f"Impossible de joindre l'API sur {API_BASE_URL}")
    else:
        st.session_state.metrics_history.append(data)

        col1, col2, col3 = st.columns(3)
        col1.metric("CPU", f"{data['cpu_percent']:.1f} %")
        col2.metric("Mémoire", f"{data['memory_percent']:.1f} %")
        col3.metric("Disque", f"{data['disk_percent']:.1f} %")

        df = pd.DataFrame(list(st.session_state.metrics_history))
        st.line_chart(df[["cpu_percent", "memory_percent", "disk_percent"]])

        st.caption(f"Fenêtre glissante : {len(df)} dernières secondes")

    if st.button("🔄 Rafraîchir"):
        st.rerun()

    # Auto-refresh every second
    time.sleep(1)
    st.rerun()


# --- Tab 2: servers ------------------------------------------------------------

with tab_servers:
    st.subheader("Serveurs enregistrés")

    def fetch_servers() -> list[dict]:
        try:
            resp = httpx.get(f"{API_BASE_URL}/servers", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError:
            return []

    servers = fetch_servers()

    def _color_status(val: str) -> str:
        colors = {"UP": "background-color: #1e7e34", "DEGRADED": "background-color: #b8860b",
                  "DOWN": "background-color: #8b0000", "unknown": "background-color: #444"}
        return colors.get(val, "")

    if servers:
        df_servers = pd.DataFrame(servers)
        st.dataframe(
            df_servers.style.applymap(_color_status, subset=["status"]),
            use_container_width=True,
        )
    else:
        st.info("Aucun serveur enregistré pour le moment.")

    st.divider()
    st.subheader("Enregistrer un nouveau serveur")

    with st.form("register_server_form"):
        name = st.text_input("Nom")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8080)
        api_key = st.text_input("API Key", type="password")
        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            try:
                resp = httpx.post(
                    f"{API_BASE_URL}/servers",
                    json={"name": name, "host": host, "port": int(port)},
                    headers={"X-API-Key": api_key},
                    timeout=5,
                )
                if resp.status_code == 201:
                    st.success(f"Serveur '{name}' enregistré !")
                    st.rerun()
                elif resp.status_code == 403:
                    st.error("Clé API invalide.")
                else:
                    st.error(f"Erreur {resp.status_code}: {resp.text}")
            except httpx.HTTPError as e:
                st.error(f"Impossible de joindre l'API : {e}")
