import streamlit as st
from pipeline_00 import pipeline

st.title('Processador de arquivos')

if st.button('Processar'):
    with st.spinner('Processando...'):
        #executar pipeline
        logs = pipeline()
        #exibir logs
        for log in logs:
            st.write(log)
            