# streamlit_app.py

import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MYSQL_USER       = os.getenv("MYSQL_USER")
MYSQL_PASSWORD   = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST       = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT       = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE   = os.getenv("MYSQL_DATABASE")

assert MYSQL_USER and MYSQL_PASSWORD and MYSQL_DATABASE, (
    "⚠️ Defina MYSQL_USER, MYSQL_PASSWORD e MYSQL_DATABASE no seu .env"
)

connection_string = (
    f"mysql+pymysql://"
    f"{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
engine = create_engine(connection_string)

# Ele chama o OPENAI_API_KEY Automaticamente...
sql_db = SQLDatabase(engine=engine)
query_engine = NLSQLTableQueryEngine(sql_database=sql_db, verbose=True)

# ===== 4) Interface Streamlit =====
st.set_page_config(page_title="Consulta MySQL + LLM", layout="wide")
st.title("🔍 Consulta MySQL via LLM (llama-index)")
st.write(
    """
    Digite sua consulta em linguagem natural abaixo.  
    Se você perguntar “quantas linhas” ou “count”, o sistema executará o SQL diretamente.  
    Caso contrário, usaremos o LLM (via llama-index) para traduzir o texto em SQL e retornar a resposta.
    """
)

prompt = st.text_area(
    label="📥 Pergunta em linguagem natural",
    placeholder="Ex.: Quantas linhas existem na tabela `train`?",
    height=120
)

if st.button("🚀 Enviar consulta"):
    if not prompt.strip():
        st.warning("🔴 Digite alguma pergunta antes de enviar.")
    else:
        with st.spinner("⌛ Processando…"):
            try:
                texto_lower = prompt.lower()
                
                # Valida a quantidade de linhas para assegurar 
                # Dataframe correto.
                if (
                    "quantas linhas" in texto_lower
                    or "quantidade de linhas" in texto_lower
                    or "count(*)" in texto_lower
                    or "numero de linhas" in texto_lower
                    or "contar linhas" in texto_lower
                    or (("count" in texto_lower) and ("from" in texto_lower))
                ):
                    with engine.connect() as conn:
                        resultado = conn.execute(text("SELECT COUNT(*) AS total FROM train;"))
                        total = resultado.scalar()
                    st.subheader("📝 Resposta (contagem real):")
                    st.write(f"Existem **{total}** linhas na tabela `train`.")

                # Para casos "normais", segue para outras perguntas.
                else:
                    resposta_obj = query_engine.query(prompt)
                    resposta_texto = str(resposta_obj)

                    if "SELECT" in resposta_texto.upper():
                        st.subheader("📝 Resposta (SQL gerado pelo LLM):")
                        st.code(resposta_texto, language="sql")
                    else:
                        st.subheader("📝 Resposta (Texto gerado pelo LLM):")
                        st.write(resposta_texto)

            except Exception as e:
                st.error(f"❌ Erro ao executar consulta: {e}")