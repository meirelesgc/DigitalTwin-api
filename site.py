import streamlit as st
import uuid

st.set_page_config(page_title="Login com Identificador Único")

st.title("Sistema de Login")

# Entrada de dados
email = st.text_input("Email:")
senha = st.text_input("Senha:", type="password")

if st.button("Entrar"):
    if senha == "1234" and email:
        st.success("Login realizado com sucesso!")

        # Gerar um identificador único
        unique_id = str(uuid.uuid4())
        
        st.write("### Seu identificador único é:")
        st.code(unique_id)
    else:
        st.error("Email ou senha incorretos!")
