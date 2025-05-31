import pandas as pd
from sqlalchemy import create_engine

from utils.env_config import get_connection_string

def get_engine():
    """
    Cria e retorna uma instância de Engine conectada ao MySQL.
    Internamente, usa a connection string obtida de env_config.get_connection_string().
    """
    conn_str = get_connection_string()
    engine = create_engine(conn_str)
    return engine

def upload_csv_to_train(csv_path: str, table_name: str = "train"):
    """
    Lê um CSV em pandas e grava na tabela MySQL especificada.
    - csv_path: caminho para o arquivo CSV (ex: "data/ready/train.csv")
    - table_name: nome da tabela no MySQL (padrão: "train")
    """

    engine = create_engine(get_connection_string())
    df = pd.read_csv("data/ready/train.csv")
    df.to_sql(name="train", con=engine, if_exists="replace", index=False)
    print("Tabela train carregada com", len(df), "linhas.")