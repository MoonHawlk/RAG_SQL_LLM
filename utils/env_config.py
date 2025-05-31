import os
from dotenv import load_dotenv

load_dotenv()  # procura por .env na raiz do projeto

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MYSQL_USER       = os.getenv("MYSQL_USER")
MYSQL_PASSWORD   = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST       = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT       = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE   = os.getenv("MYSQL_DATABASE")

assert OPENAI_API_KEY,  "⚠️ Defina OPENAI_API_KEY no seu arquivo .env"
assert MYSQL_USER and MYSQL_PASSWORD and MYSQL_DATABASE, \
       "⚠️ Defina MYSQL_USER, MYSQL_PASSWORD e MYSQL_DATABASE no seu arquivo .env"

def get_connection_string() -> str:
    """
    Retorna a connection string para SQLAlchemy no formato:
    "mysql+pymysql://<user>:<password>@<host>:<port>/<database>"
    """
    return (
        f"mysql+pymysql://"
        f"{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )