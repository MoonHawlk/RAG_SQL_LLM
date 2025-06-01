# Devido a alguns contra-tempos, acabei colocando todo o código nesse arquivo...
# Considero isso ruim para essa situação, no entanto, tive compromissos inadiaveis,
# As quais tive de cumprir em paralelo. De resto, a modularização funciona e foi usada
# Na versão v1, assim como outros modulos aos quais não subi pra o git.

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

load_dotenv()  # espera encontrar OPENAI_API_KEY, MYSQL_* no .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MYSQL_USER     = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

assert OPENAI_API_KEY,  "⚠️ Defina OPENAI_API_KEY no .env"
assert MYSQL_USER and MYSQL_PASSWORD and MYSQL_DATABASE, \
       "⚠️ Defina MYSQL_USER, MYSQL_PASSWORD e MYSQL_DATABASE no .env"

connection_string = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
engine = create_engine(connection_string)
sql_db = SQLDatabase(engine=engine)

# Passamos verbose=True para forçar a geração explícita da SQL.
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_db,
    verbose=True
)

def is_valid_query_context(prompt):
    """
    Verifica se a pergunta está dentro do contexto válido (consultas à tabela train)
    """
    prompt_lower = prompt.lower().strip()
    
    # Lista de palavras/frases que indicam contexto inválido
    invalid_contexts = [
        # Perguntas pessoais
        "quem é você", "o que você é", "como você funciona", "você pode",
        "me ajude com", "resolva isso", "calcule isso", "faça isso",
        
        # Perguntas gerais não relacionadas a dados
        "qual é", "como fazer", "me explique", "o que significa",
        "defina", "conceito de", "diferença entre",
        
        # Comandos de sistema/programação não relacionados
        "execute", "rode", "instale", "configure", "crie arquivo",
        "delete", "drop table", "truncate", "alter table",
        
        # Perguntas sobre outras tabelas/bancos
        "tabela user", "tabela cliente", "banco", "database",
        "outra tabela", "outras bases",
        
        # Conversas casuais
        "oi", "olá", "bom dia", "como vai", "tudo bem",
        "obrigado", "tchau", "até logo"
    ]
    
    # Lista de palavras que indicam contexto válido (relacionado a dados/SQL)
    valid_contexts = [
        "train", "tabela", "dados", "registros", "linhas", "colunas",
        "select", "count", "sum", "avg", "max", "min", "group by",
        "where", "order by", "limit", "distinct", "total",
        "quantidade", "quantos", "quantas", "mostrar", "listar",
        "buscar", "encontrar", "filtrar", "agrupar", "ordenar",
        "média", "máximo", "mínimo", "soma", "contagem",
        "grafico", "gráfico", "análise", "estatística"
    ]
    
    # Se contém palavras claramente inválidas, rejeita
    for invalid in invalid_contexts:
        if invalid in prompt_lower:
            return False, f"🚫 Desculpe, só posso responder perguntas sobre consultas à tabela `train`. Sua pergunta parece estar fora deste contexto."
    
    # Se não contém nenhuma palavra válida relacionada a dados/SQL, rejeita
    has_valid_context = any(valid in prompt_lower for valid in valid_contexts)
    if not has_valid_context:
        return False, f"🚫 Posso apenas ajudar com consultas e análises da tabela `train`. Por favor, faça uma pergunta relacionada aos dados."
    
    # Verifica comandos SQL perigosos
    dangerous_sql = ["drop", "delete", "truncate", "alter", "create", "insert", "update"]
    for dangerous in dangerous_sql:
        if dangerous in prompt_lower and "table" in prompt_lower:
            return False, f"⚠️ Por segurança, não posso executar comandos que modifiquem a estrutura ou dados da tabela."
    
    return True, None

def generate_analytical_response(df, original_response, query_text):
    """
    Gera uma resposta mais analítica baseada no DataFrame retornado
    """
    if df is None or df.empty:
        return original_response + "\n\n📊 **Análise:** Não há dados para análise."
    
    analysis = []
    analysis.append("📊 **ANÁLISE DETALHADA:**")
    analysis.append(f"• **Total de registros:** {len(df)}")
    
    # Análise das colunas
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    if numeric_cols:
        analysis.append(f"• **Colunas numéricas:** {', '.join(numeric_cols)}")
        for col in numeric_cols:
            if not df[col].empty:
                analysis.append(f"  - {col}: Min={df[col].min():.2f}, Max={df[col].max():.2f}, Média={df[col].mean():.2f}")
    
    if text_cols:
        analysis.append(f"• **Colunas de texto:** {', '.join(text_cols)}")
        for col in text_cols:
            unique_count = df[col].nunique()
            analysis.append(f"  - {col}: {unique_count} valores únicos")
    
    # Verifica se há valores nulos
    null_counts = df.isnull().sum()
    if null_counts.any():
        analysis.append("• **Valores nulos encontrados:**")
        for col, count in null_counts.items():
            if count > 0:
                analysis.append(f"  - {col}: {count} valores nulos ({count/len(df)*100:.1f}%)")
    
    # Análise contextual baseada na query
    query_lower = query_text.lower()
    if any(word in query_lower for word in ['top', 'maior', 'menor', 'ranking']):
        analysis.append("• **Insight:** Esta consulta parece buscar valores extremos ou rankings.")
    elif any(word in query_lower for word in ['média', 'average', 'sum', 'total']):
        analysis.append("• **Insight:** Esta consulta envolve cálculos agregados.")
    elif any(word in query_lower for word in ['grupo', 'group', 'categoria']):
        analysis.append("• **Insight:** Esta consulta agrupa dados por categorias.")
    
    # Sugestões adicionais
    analysis.append("\n💡 **SUGESTÕES PARA EXPLORAÇÃO:**")
    if len(df) > 10:
        analysis.append("• Considere aplicar filtros para focar em subconjuntos específicos")
    if numeric_cols:
        analysis.append("• Explore correlações entre variáveis numéricas")
    if text_cols and len(df) > 1:
        analysis.append("• Analise a distribuição das categorias de texto")
    
    return original_response + "\n\n" + "\n".join(analysis)

st.set_page_config(page_title="Chat SQL → MySQL", layout="wide")
st.title("💬 Chat SQL → MySQL (via LLM)")

st.markdown("""
Digite no campo abaixo para consultar sua tabela `train` em linguagem natural.  
• Se perguntar "quantas linhas" ou usar "count", executa `SELECT COUNT(*) FROM train;` diretamente.  
• Caso contrário, o LLM (llama-index) traduz o texto em SQL, executa e retorna o resultado.  

**Para exibir um gráfico, inclua a palavra "grafico" (ou "gráfico") na sua pergunta**.  

⚠️ **Importante:** Este assistente responde apenas perguntas sobre consultas e análises da tabela `train`.
""")

# Caixa de informações sobre limitações
st.info("""
🔒 **Limitações de Segurança:**
- Só respondo perguntas sobre a tabela `train`
- Não executo comandos que modifiquem dados (INSERT, UPDATE, DELETE)
- Não respondo perguntas gerais ou fora do contexto de dados
- Foque em consultas como: "quantos registros", "mostre os dados onde...", "qual a média de...", etc.
""")

# NOVA SEÇÃO: Configurações de Análise
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### ⚙️ Configurações de Análise")
with col2:
    analytical_mode = st.toggle("🔍 Modo Analítico", 
                               help="Ativa respostas mais detalhadas com insights e estatísticas")

st.markdown("---")

if "history" not in st.session_state:
    st.session_state.history = []
    # Cada entrada será um dicionário:
    # {
    #     "role": "user"|"assistant",
    #     "message": str,
    #     "sql": str or None,
    #     "dataframe": pd.DataFrame or None,
    #     "show_graph": bool,
    #     "analytical": bool
    # }

if st.button("🗑️ Limpar histórico"):
    st.session_state.history = []

prompt = st.chat_input("Escreva sua pergunta sobre `train`...")

if prompt:
    # VALIDAÇÃO DE CONTEXTO - NOVA TRAVA
    is_valid, error_message = is_valid_query_context(prompt)
    
    if not is_valid:
        # Adiciona pergunta do usuário
        st.session_state.history.append({
            "role": "user",
            "message": prompt,
            "sql": None,
            "dataframe": None,
            "show_graph": False,
            "analytical": False
        })
        
        # Adiciona resposta de erro
        st.session_state.history.append({
            "role": "assistant",
            "message": error_message,
            "sql": None,
            "dataframe": None,
            "show_graph": False,
            "analytical": False
        })
        st.rerun()  # Atualiza a interface
    
    # Armazena a pergunta do usuário no histórico
    st.session_state.history.append({
        "role": "user",
        "message": prompt,
        "sql": None,
        "dataframe": None,
        "show_graph": False,
        "analytical": False
    })

    text_lower = prompt.lower()
    pediu_grafico = ("grafico" in text_lower) or ("gráfico" in text_lower)

    # Verifica caso "count(*) direto" para otimizar
    if (
        "quantas linhas" in text_lower
        or "count(*)" in text_lower
        or ("count" in text_lower and "from" in text_lower)
    ):
        # Executa SELECT COUNT(*) FROM train;
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) AS total FROM train;"))
            total = result.scalar()

        response = f"Existem **{total}** linhas na tabela `train`."
        sql_used = "SELECT COUNT(*) AS total FROM train;"
        df_result = pd.DataFrame([{"total": total}])

    else:
        # Usa o LLM para gerar + executar SQL
        try:
            response_obj = query_engine.query(prompt)
            response = str(response_obj)
            
            # Verifica se a resposta indica que a pergunta está fora do escopo
            if any(phrase in response.lower() for phrase in [
                "não posso", "não consigo", "fora do escopo", "não relacionado",
                "não é sobre", "não encontrei", "não há informações"
            ]):
                response = "🚫 Desculpe, só posso responder perguntas sobre consultas à tabela `train`. Por favor, reformule sua pergunta focando nos dados da tabela."
                sql_used = None
                df_result = None
            else:
                # Processa normalmente...
                
                # Captura a SQL gerada pelo response_obj - MÚLTIPLAS TENTATIVAS
                sql_used = None
                
                # Tentativa 1: response_obj.query_str
                try:
                    if hasattr(response_obj, 'query_str') and response_obj.query_str:
                        sql_used = response_obj.query_str
                except Exception:
                    pass
                
                # Tentativa 2: response_obj.extra_info
                if not sql_used:
                    try:
                        if hasattr(response_obj, 'extra_info') and response_obj.extra_info:
                            sql_used = response_obj.extra_info.get("sql_query", None)
                    except Exception:
                        pass
                
                # Tentativa 3: response_obj.metadata
                if not sql_used:
                    try:
                        if hasattr(response_obj, 'metadata') and response_obj.metadata:
                            sql_used = response_obj.metadata.get("sql_query", None)
                    except Exception:
                        pass
                
                # Tentativa 4: response_obj.source_nodes
                if not sql_used:
                    try:
                        if hasattr(response_obj, 'source_nodes') and response_obj.source_nodes:
                            for node in response_obj.source_nodes:
                                if hasattr(node, 'metadata') and 'sql_query' in node.metadata:
                                    sql_used = node.metadata['sql_query']
                                    break
                    except Exception:
                        pass
                
                # Tentativa 5: Procurar por padrões SQL na resposta texto
                if not sql_used:
                    try:
                        import re
                        sql_patterns = [
                            r'```sql\s*(.*?)\s*```',
                            r'```\s*(SELECT.*?)\s*```',
                            r'SQL.*?:\s*(SELECT.*?)(?:\n|$)',
                            r'Query.*?:\s*(SELECT.*?)(?:\n|$)',
                        ]
                        
                        for pattern in sql_patterns:
                            matches = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
                            if matches:
                                sql_used = matches.group(1).strip()
                                break
                    except Exception:
                        pass

                if not sql_used:
                    sql_used = f"⚠️ SQL não capturada automaticamente para: '{prompt}'"
                    df_result = None
                    response = f"{response}\n\n*Nota: A consulta SQL não pôde ser capturada automaticamente.*"
                else:
                    # Tenta executar a SQL capturada no MySQL para montar o DataFrame
                    try:
                        if sql_used.strip().lower().startswith("select"):
                            df_result = pd.read_sql_query(sql_used, engine)
                        else:
                            df_result = None
                    except Exception as e:
                        df_result = None
                        response = f"{response}\n\n*Erro ao executar SQL: {str(e)}*"
        
        except Exception as e:
            response = "🚫 Ocorreu um erro ao processar sua consulta. Verifique se ela está relacionada à tabela `train` e tente novamente."
            sql_used = None
            df_result = None

    # APLICA MODO ANALÍTICO SE ATIVADO
    if analytical_mode and df_result is not None:
        response = generate_analytical_response(df_result, response, prompt)

    # Armazena a resposta do assistente no histórico
    st.session_state.history.append({
        "role": "assistant",
        "message": response,
        "sql": sql_used,
        "dataframe": df_result,
        "show_graph": pediu_grafico,
        "analytical": analytical_mode
    })

# EXIBIÇÃO DO HISTÓRICO
for idx, entry in enumerate(st.session_state.history):
    if entry["role"] == "user":
        st.chat_message("user").write(entry["message"])
    else:
        # Adiciona indicador de modo analítico
        if entry.get("analytical"):
            st.chat_message("assistant", avatar="🔍").write(entry["message"])
        else:
            st.chat_message("assistant").write(entry["message"])

        # SEMPRE exibe a SQL
        sql_executada = entry.get("sql")
        if sql_executada:
            if sql_executada.startswith("SELECT") or sql_executada.startswith("select"):
                st.markdown(f"**🔎 Consulta SQL executada:**\n```sql\n{sql_executada}\n```")
            elif sql_executada.startswith("⚠️"):
                st.markdown(f"**⚠️ Informação sobre SQL:**\n{sql_executada}")
            else:
                st.markdown(f"**🔎 SQL utilizada:**\n```sql\n{sql_executada}\n```")
        else:
            st.markdown("**⚠️ SQL não disponível para esta consulta**")

        # Se houve DataFrame e o usuário pediu gráfico, exibe imediatamente
        df_last = entry.get("dataframe")
        if entry.get("show_graph") and isinstance(df_last, pd.DataFrame):
            st.subheader("📊 Gráfico automático solicitado")
            st.dataframe(df_last, use_container_width=True)

            num_cols = df_last.select_dtypes(include="number").columns.tolist()
            non_num_cols = [c for c in df_last.columns if c not in num_cols]

            if len(num_cols) == 1 and len(non_num_cols) == 1:
                cat_col = non_num_cols[0]
                val_col = num_cols[0]
                chart_data = df_last.set_index(cat_col)[val_col]
                st.bar_chart(chart_data)
            elif num_cols:
                st.bar_chart(df_last[num_cols])
            else:
                st.info("❗ Não há colunas numéricas para plotagem.")

            st.markdown("---")
            continue

        # Caso não tenha pedido gráfico, mas haja DataFrame de SELECT, oferece checkbox
        if isinstance(df_last, pd.DataFrame):
            sql_txt = entry.get("sql", "")
            if isinstance(sql_txt, str) and sql_txt.strip().lower().startswith("select"):
                checkbox_key = f"chart_{idx}"
                show_chart = st.checkbox("📈 Exibir gráfico da última consulta?", key=checkbox_key)
                if show_chart:
                    st.subheader("📊 Gráfico do resultado")
                    st.dataframe(df_last, use_container_width=True)

                    num_cols = df_last.select_dtypes(include="number").columns.tolist()
                    non_num_cols = [c for c in df_last.columns if c not in num_cols]

                    if len(num_cols) == 1 and len(non_num_cols) == 1:
                        cat_col = non_num_cols[0]
                        val_col = num_cols[0]
                        chart_data = df_last.set_index(cat_col)[val_col]
                        st.bar_chart(chart_data)
                    elif num_cols:
                        st.bar_chart(df_last[num_cols])
                    else:
                        st.info("❗ Não há colunas numéricas para plotagem.")
        st.markdown("---")
