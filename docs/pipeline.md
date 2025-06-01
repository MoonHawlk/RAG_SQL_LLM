# Documentação Técnica - Sistema de Chat SQL para MySQL

## Visão Geral

Este sistema implementa uma interface de chat conversacional que permite aos usuários fazerem consultas em linguagem natural a uma base de dados MySQL. Utiliza a biblioteca **LlamaIndex** com modelos de linguagem para traduzir perguntas em SQL e executar consultas automaticamente.

## Arquitetura do Sistema

### Componentes Principais

1. **Interface Web**: Streamlit para interface de usuário
2. **Processamento de Linguagem Natural**: LlamaIndex + OpenAI
3. **Base de Dados**: MySQL via SQLAlchemy
4. **Validação de Contexto**: Sistema de filtros de segurança
5. **Análise de Dados**: Pandas para manipulação e visualização

### Fluxo de Dados

```
Pergunta do Usuário → Validação de Contexto → Processamento LLM → Execução SQL → Análise e Visualização
```

## Configuração e Inicialização

### Variáveis de Ambiente Requeridas

O sistema requer as seguintes variáveis no arquivo `.env`:

- `OPENAI_API_KEY`: Chave da API OpenAI
- `MYSQL_USER`: Usuário do MySQL
- `MYSQL_PASSWORD`: Senha do MySQL  
- `MYSQL_HOST`: Host do servidor (padrão: localhost)
- `MYSQL_PORT`: Porta do servidor (padrão: 3306)
- `MYSQL_DATABASE`: Nome da base de dados

### String de Conexão

```python
connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
```

## Funcionalidades Principais

### 1. Sistema de Validação de Contexto

A função `is_valid_query_context()` implementa um sistema robusto de validação que:

#### Contextos Inválidos (Rejeitados)
- Perguntas pessoais sobre o sistema
- Comandos de sistema/programação não relacionados
- Consultas sobre outras tabelas/bases de dados
- Conversas casuais
- Comandos SQL perigosos (DROP, DELETE, etc.)

#### Contextos Válidos (Aceitos)
- Consultas sobre a tabela `train`
- Comandos SQL de leitura (SELECT, COUNT, etc.)
- Análises estatísticas e agrupamentos
- Solicitações de gráficos e visualizações

#### Exemplo de Validação
```python
invalid_contexts = [
    "quem é você", "o que você é", "como você funciona",
    "me ajude com", "resolva isso", "calcule isso"
]

valid_contexts = [
    "train", "tabela", "dados", "registros", "select", 
    "count", "média", "gráfico", "análise"
]
```

### 2. Motor de Consultas NL-to-SQL

Utiliza `NLSQLTableQueryEngine` do LlamaIndex para:

- Traduzir linguagem natural em SQL
- Executar consultas automaticamente
- Capturar metadados da execução
- Retornar resultados estruturados

#### Configuração do Motor
```python
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_db,
    verbose=True  # Força geração explícita de SQL
)
```

### 3. Captura de SQL Gerada

O sistema implementa múltiplas estratégias para capturar a SQL gerada pelo LLM:

1. **response_obj.query_str**
2. **response_obj.extra_info["sql_query"]**
3. **response_obj.metadata["sql_query"]**
4. **response_obj.source_nodes[].metadata["sql_query"]**
5. **Regex patterns** na resposta texto

### 4. Modo Analítico

A função `generate_analytical_response()` enriquece as respostas com:

#### Estatísticas Básicas
- Total de registros
- Análise de colunas numéricas (min, max, média)
- Contagem de valores únicos
- Identificação de valores nulos

#### Insights Contextuais
- Análise baseada na query original
- Identificação de padrões (rankings, agregações, agrupamentos)
- Sugestões para exploração adicional

#### Exemplo de Saída Analítica
```
📊 ANÁLISE DETALHADA:
• Total de registros: 1000
• Colunas numéricas: idade, salario
  - idade: Min=18.00, Max=65.00, Média=42.50
  - salario: Min=2000.00, Max=15000.00, Média=7500.00
• Insight: Esta consulta envolve cálculos agregados.

💡 SUGESTÕES PARA EXPLORAÇÃO:
• Explore correlações entre variáveis numéricas
• Analise a distribuição das categorias de texto
```

## Casos de Uso Especiais

### 1. Consulta COUNT(*) Otimizada

Para consultas de contagem simples, o sistema executa SQL direta:

```python
if ("quantas linhas" in text_lower or "count(*)" in text_lower):
    # Executa SELECT COUNT(*) FROM train; diretamente
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) AS total FROM train;"))
        total = result.scalar()
```

### 2. Geração Automática de Gráficos

Quando o usuário inclui "grafico" ou "gráfico" na pergunta:

- Identifica colunas numéricas vs categóricas
- Gera visualizações automáticas usando Streamlit
- Prioriza gráficos de barras para relações categoria-valor
- Oferece fallback para múltiplas colunas numéricas

### 3. Histórico de Conversação

Cada entrada no histórico contém:

```python
{
    "role": "user"|"assistant",
    "message": str,
    "sql": str or None,
    "dataframe": pd.DataFrame or None,
    "show_graph": bool,
    "analytical": bool
}
```

## Medidas de Segurança

### 1. Validação de Entrada
- Filtros de contexto rigorosos
- Detecção de comandos SQL perigosos
- Validação de escopo (apenas tabela `train`)

### 2. Limitações de Execução
- Apenas comandos SELECT permitidos
- Bloqueio de DDL/DML (CREATE, DROP, INSERT, UPDATE, DELETE)
- Conexões controladas via SQLAlchemy

### 3. Tratamento de Erros
- Captura de exceções em todas as operações
- Mensagens de erro contextualizadas
- Fallbacks para operações que falham

## Interface de Usuário

### Componentes Principais

1. **Campo de Chat**: Entrada principal para perguntas
2. **Toggle Analítico**: Ativa/desativa modo de análise detalhada
3. **Histórico Persistente**: Mantém contexto da sessão
4. **Exibição de SQL**: Mostra consultas executadas
5. **Visualizações Dinâmicas**: Gráficos sob demanda

### Indicadores Visuais

- 🔍 **Modo Analítico**: Avatar diferenciado para respostas analíticas
- 🚫 **Erros de Contexto**: Mensagens claras de limitação
- ⚠️ **Avisos de SQL**: Informações sobre captura de consultas
- 📊 **Gráficos**: Seção dedicada para visualizações

## Limitações e Considerações

### Limitações Técnicas
- Dependente da qualidade do modelo LLM
- Limitado à tabela `train` específica
- Requer configuração manual de credenciais

### Limitações de Segurança
- Não executa comandos de modificação
- Contexto restrito a análise de dados
- Validação baseada em palavras-chave (pode ter falsos positivos/negativos)

### Considerações de Performance
- Consultas grandes podem impactar performance
- Dependência de APIs externas (OpenAI)
- Processamento síncrono na interface

## Extensibilidade

O sistema pode ser estendido para:

- Suportar múltiplas tabelas
- Implementar cache de consultas
- Adicionar mais tipos de visualização
- Integrar outros provedores de LLM
- Implementar autenticação de usuários
- Adicionar logging e auditoria