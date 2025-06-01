from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

def get_nlsql_query_engine(engine):
    """
    Recebe uma instância de SQLAlchemy Engine (MySQL) e instancia:
      1) SQLDatabase
      2) NLSQLTableQueryEngine (com verbose=True)

    Retorna apenas o objeto NLSQLTableQueryEngine pronto para uso.
    (A LLM usa OPENAI_API_KEY carregada no env_config.)
    """
    sql_db = SQLDatabase(engine=engine)

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_db,
        verbose=True
    )

    return query_engine
