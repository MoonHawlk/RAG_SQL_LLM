# load_data.py

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

def get_connection_string():
    """
    Carrega as variáveis de ambiente e retorna a connection string do MySQL.
    Espera encontrar no .env:
      MYSQL_USER
      MYSQL_PASSWORD
      MYSQL_HOST (opcional, padrão 'localhost')
      MYSQL_PORT (opcional, padrão '3306')
      MYSQL_DATABASE
    """
    load_dotenv()
    MYSQL_USER     = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT     = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    assert MYSQL_USER and MYSQL_PASSWORD and MYSQL_DATABASE, (
        "⚠️ Defina MYSQL_USER, MYSQL_PASSWORD e MYSQL_DATABASE no seu .env"
    )

    return (
        f"mysql+pymysql://"
        f"{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

def upload_csv_to_train(csv_path: str, table_name: str = "train"):
    """
    Lê o CSV e grava na tabela MySQL.
    - csv_path: caminho para o arquivo CSV (ex: "data/ready/train.csv")
    - table_name: nome da tabela no MySQL (padrão: "train")
    Usa if_exists="replace" para recriar a tabela do zero.
    """
    conn_str = get_connection_string()
    engine = create_engine(conn_str)

    df = pd.read_csv(csv_path)
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",  # recria a tabela a cada execução
        index=False
    )
    print(f"Tabela '{table_name}' carregada com {len(df)} linhas.")

if __name__ == "__main__":
    csv_path = "data/ready/train.csv"
    upload_csv_to_train(csv_path, table_name="train")