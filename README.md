# Conector para Banco de Dados Vetorial com Python e PostgreSQL (PGVector)

Este repositório contém um código em Python que integra um banco de dados PostgreSQL com a extensão PGVector, permitindo o armazenamento e consulta de perguntas e respostas em formato vetorial. A API foi desenvolvida para facilitar a interação com outros serviços, usando embeddings gerados por modelos de linguagem.

## Funcionalidades principais:

- **Armazenamento de Embeddings**: O código usa o modelo `SentenceTransformer` para gerar embeddings das perguntas e respostas, que são armazenados em um banco de dados PostgreSQL com a extensão PGVector.
  
- **API para Upload e Consulta**: A API Flask oferece endpoints para upload de arquivos CSV contendo perguntas e respostas, bem como uma busca por similaridade de vetores para recuperar perguntas e respostas relevantes.
  
- **Processamento Assíncrono**: O upload de arquivos CSV é tratado de forma assíncrona, permitindo que o processamento de grandes volumes de dados seja feito em segundo plano.

- **Autenticação Básica**: A API implementa autenticação básica, protegendo os endpoints de upload e pesquisa.

- **Banco de Dados PostgreSQL**: O banco de dados é configurado para armazenar as perguntas, respostas e embeddings vetoriais, utilizando a extensão PGVector para consultas por similaridade.

## Como Funciona:

1. **Upload de Arquivo CSV**: O endpoint `/upload` permite que você faça upload de arquivos CSV com duas colunas: `question` e `answer`. O arquivo é processado em segundo plano, e os embeddings são gerados e armazenados no banco de dados.

2. **Consulta de Similaridade**: O endpoint `/search` permite que você envie uma pergunta e receba as respostas mais similares, ordenadas pela distância do vetor gerado para a consulta.

## Tecnologias Utilizadas:
- **Python 3.x**
- **Flask** (para a API)
- **Sentence-Transformers** (para geração de embeddings)
- **PostgreSQL com PGVector** (para armazenamento e consulta de dados vetoriais)
- **Flask-HTTPAuth** (para autenticação básica)
- **Pandas** (para processamento de arquivos CSV)
- **Dotenv** (para configuração de variáveis de ambiente)

## Como Usar:

1. Clone este repositório.
2. Configure o PostgreSQL com a extensão PGVector e crie o banco de dados.
3. Crie um arquivo `.env` com as variáveis de configuração do banco de dados e credenciais de autenticação.
4. Instale as dependências necessárias com `pip install -r requirements.txt`.
5. Inicie o servidor com `python app.py`.
6. Use os endpoints `/upload` e `/search` para interagir com a API.

## Endpoints:

- **POST `/upload`**: Faz o upload de um arquivo CSV com perguntas e respostas. Requer autenticação.
- **POST `/search`**: Consulta o banco de dados por perguntas similares. Requer autenticação.

## Contribuições:

Sinta-se à vontade para fazer contribuições! Se você tiver melhorias ou correções, abra um Pull Request.
