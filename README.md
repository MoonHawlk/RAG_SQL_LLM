# RAG_SQL_LLM - Guia de Execução

Sistema de chat conversacional para consultas SQL em linguagem natural usando LlamaIndex e MySQL.

## 📋 Pré-requisitos

- Python 3.10.11 (Recomendo usar as mesmas versões, bibliotecas como LLama-index e Langchain tem enfrentado problemas significativos de compatibilidade quando trabalhamos com versões diferentes)
- MySQL Server (local ou remoto)
- Conta OpenAI com API Key

## Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/MoonHawlk/RAG_SQL_LLM.git
cd RAG_SQL_LLM
```

### 2. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac (meu caso):
source venv/bin/activate
```

### 3. Instalação das Dependências

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- streamlit
- pandas
- sqlalchemy
- pymysql
- python-dotenv
- llama-index
- openai

### 4. Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Dados genéricos... Considere de acordo com a abordagem
# OpenAI API Configuration
OPENAI_API_KEY=sua_chave_openai_aqui

# MySQL Database Configuration
MYSQL_USER=seu_usuario_mysql
MYSQL_PASSWORD=sua_senha_mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=nome_da_sua_base_dados
```

## 🗄️ Preparação dos Dados

### 1. Processamento dos Dados Raw

Execute os notebooks na ordem correta para processar e limpar os dados:

#### Passo 1: Limpeza Inicial
```bash
jupyter notebook notebooks/data_cleaning/[Cleaning\ -\ Step\ 1]\ notebook.ipynb
```

Este notebook realiza:
- Carregamento do arquivo `.gz` baixado
- Visualização inicial dos dados
- Identificação de inconsistências

#### Passo 2: Processamento Final
```bash
jupyter notebook notebooks/data_cleaning/[Cleaning\ -\ Step\ 2]\ notebook.ipynb
```

Este notebook executa:
- Normalização dos dados
- Validação da qualidade
- Transformações finais
- Exportação para formato compatível com MySQL

### 2. Configuração do MySQL

#### Conectar ao MySQL
```bash
mysql -u root -p
```

#### Criar Base de Dados
```sql
CREATE DATABASE nome_da_sua_base_dados;
USE nome_da_sua_base_dados;
```

## 🖥️ Execução da Aplicação

### 1. Verificar Configurações

Teste a conexão com a base de dados:

```python
python -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

connection_string = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
engine = create_engine(connection_string)

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM train;'))
    print(f'Registros na tabela train: {result.scalar()}')
"
```

### 2. Iniciar a Aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em: `http://localhost:8501`

## 📊 Usando a Aplicação

### Exemplos de Consultas

**Consultas Básicas:**
- "Quantas linhas tem a tabela?"
- "Mostre os primeiros 10 registros"
- "Qual é a média da coluna idade?"

**Consultas com Filtros:**
- "Mostre registros onde salario > 5000"
- "Quantos registros têm status ativo?"
- "Liste os dados ordenados por data"

**Consultas com Gráficos:**
- "Mostre um gráfico da distribuição por categoria"
- "Gráfico da média de vendas por mês"
- "Visualize a relação entre idade e salário"

### Funcionalidades Disponíveis

- **Modo Analítico**: Toggle para respostas detalhadas com estatísticas
- **Histórico**: Mantém contexto da conversa
- **Visualizações**: Gráficos automáticos sob demanda
- **SQL View**: Visualização das consultas executadas

## 🔧 Troubleshooting

### Problemas Comuns

**Erro de Conexão MySQL:**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)
```
- Verifique credenciais no `.env`
- Confirme se MySQL está rodando
- Teste conexão manual

**Erro OpenAI API:**
```
openai.error.AuthenticationError
```
- Verifique se `OPENAI_API_KEY` está correto
- Confirme se tem créditos disponíveis

**Tabela não encontrada:**
```
Table 'database.train' doesn't exist
```
- Execute os notebooks de limpeza
- Crie e popule a tabela `train`

**Dependências em conflito:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Logs de Debug

Para debug mais detalhado:

```bash
# Executar com logs verbose
streamlit run app.py --logger.level=debug

# Ou adicionar ao código:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Estrutura do Projeto

```
RAG_SQL_LLM/
├── streamlit_app.py                            # "main" 
├── .env                                        # Variáveis de ambiente (não commitado)
├── requirements.txt                            # Dependências Python
├── README.md                                   # Este arquivo
│                                  
├── docs/
│   └── pipeline.md                             # Documentação técnica
│
├── data/                                       # Dados Gerais
│   └── raw/
│   └── processing/
│   └── ready/
│
├── notebooks/
│   └── exploratory/
│       ├── [Testing LLama-index] notebook.ipynb
│       └── [Testing MYSQL-DB] notebook.ipynb
│
│   └── data_cleaning/
│       ├── [Cleaning - Step 1] notebook.ipynb
│       └── [Cleaning - Step 2] notebook.ipynb
└── env/                                        # Ambiente virtual (não commitado)
```

## 🔒 Segurança e Limitações

### Limitações de Segurança Implementadas

- Apenas consultas SELECT permitidas
- Contexto restrito à tabela `train`
- Validação de entrada rigorosa
- Bloqueio de comandos DDL/DML perigosos

### Boas Práticas

- Mantenha `.env` fora do controle de versão
- Use usuário MySQL com privilégios limitados
- Monitore uso da API OpenAI
- Faça backup regular dos dados

## Considerações

1. O restante da documentação, explicando a aplicação main em si, está aqui `docs/pipeline.md`.
2. Essa atividade foi feita visando a qualidade dos dados e enterpretabilidade, logo, abdiquei de algumas decisões, como por exemplo, manter os nomes VA5*, pois na minha experiência, esses nomes muitas vezes atrapalhavam o modelo gerar boas queries, logo, deve ser evitado.
3. Tive algumas limitações com relação aos gráficos... Devido ao tempo, obtei por focar no gráfico de barras, simples e direto.

---

**Versão**: 1.0  
**Última atualização**: Maio 2025