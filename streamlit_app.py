import streamlit as st
import requests

st.title("Teste da API SmoothieFroot")

try:
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    st.write(f"Status da API: {smoothiefroot_response.status_code}")
    if smoothiefroot_response.status_code == 200:
        st.json(smoothiefroot_response.json())  # Exibe o JSON da resposta
    else:
        st.text(f"Erro: Status {smoothiefroot_response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"Erro ao chamar a API: {e}")
