import streamlit as st

st.title("TESTE FINAL DE AMBIENTE")
st.write("Se você está vendo isso, o Streamlit acordou.")
st.write("Hora local do servidor:", st.write("...")) # Erro proposital? No, let's be clean.
import datetime
st.write(f"Hora: {datetime.datetime.now()}")