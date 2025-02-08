# Bibliotecas
import os
import gdown
import duckdb
import pandas as pd
from sqlalchemy import create_engine    
from dotenv import load_dotenv
from pandas import DataFrame
from datetime import datetime
from duckdb import DuckDBPyRelation

# Carrega variaveis de ambiente
load_dotenv()

def conectar_ao_banco():
    # Conexão com o banco de dados DuckDB; Criar um banco de dados se não exixtir.
    return duckdb.connect(database='duck.db', read_only=False)

def inicialiar_tabela(con):
    # Cria uma tabela no banco de dados DuckDB
    con.execute("""
                CREATE TABLE IF NOT EXISTS historico_arquivos (
                    nome_arquivo  VARCHAR,
                    horario_processamento TIMESTAMP
                    )
                """)
    
def registrar_arquivo(con, nome_arquivo):
    # Registra o arquivo que foi processado no banco de dados
    con.execute("INSERT INTO historico_arquivos VALUES (?, ?)", (nome_arquivo, datetime.now()))
    
def verificar_arquivo_ja_processado(con):
    # retorna a lista de arquivos que já foram processados
    return set(row [0] for row in con.execute("SELECT nome_arquivo FROM historico_arquivos").fetchall())
    

# Função para baixar arquivos de um diretório do Google Drive
def baixar_arquivos_do_google_drive(url, diretorio_local):
    os.makedirs(diretorio_local, exist_ok=True)
    gdown.download_folder(url, output=diretorio_local, quiet=False, use_cookies=False)

# Função para listar arquivos CSV em um diretório    
def listar_arquivos_csv(diretorio):
    arquivos_csv = [] 
    todos_os_arquivos = os.listdir(diretorio)
    for arquivo in todos_os_arquivos:
        if arquivo.endswith(".csv") or arquivo.endswith(".json") or arquivo.endswith(".parquet"):
            caminho_completo = os.path.join(diretorio, arquivo)
            tipo = arquivo.split('.')[-1]
            arquivos_csv.append((caminho_completo, tipo)) 
    return arquivos_csv

# Função para ler arquivos
def ler_csv_json_parquet(caminho_arquivo, tipo):
    if tipo == 'csv':
        return duckdb.read_csv(caminho_arquivo)
    elif tipo == 'json':
        return pd.read_json(caminho_arquivo)
    elif tipo == 'parquet':
        return pd.read_parquet(caminho_arquivo)
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {tipo}")

# Função para adicionar uma coluna de total de vendas
def transformar(df: DuckDBPyRelation) -> DataFrame:
    # Adiciona uma coluna de total de vendas executando com SQL
    df_transformado = duckdb.sql('SELECT *, quantidade * valor AS total_vendas FROM df').df()
    '''
    Querys com sytaxe de postgresql funcionam no duckdb
    
    df_transformado = duckdb.sql("""SELECT
                                 categoria,
                                 COUNT(*) AS total_vendas,
                                 SUM(valor) AS valor_total
                                 FROM df
                                 GROUP BY categoria
                                 ORDER BY valor_total DESC""").df()
    '''
    print(df_transformado)
    return df_transformado

# Função para salvar um dataframe em uma tabela no banco de dados
def salvar_no_db(df_duckdb, tabela):
    # Conexão com o banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    # Salva o dataframe em uma tabela no banco de dados
    df_duckdb.to_sql(tabela, con=engine, if_exists='append', index=False)

def pipeline():
    url_pasta = 'https://drive.google.com/drive/folders/1UIK54nnkSKf2vEp-91XTBSKMEJ7Kc7R-'
    diretorio_local = './pasta_gdown'
    
    #baixar_arquivos_do_google_drive(url_pasta, diretorio_local)    
    con = conectar_ao_banco()
    inicialiar_tabela(con)
    arquivos_processados = verificar_arquivo_ja_processado(con)
    arquivos_e_tipos = listar_arquivos_csv(diretorio_local)
    
    logs = []
    for caminho_arquivo, tipo in arquivos_e_tipos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        if nome_arquivo not in arquivos_processados:
            df = ler_csv_json_parquet(caminho_arquivo, tipo)
            df_transformado = transformar(df)
            salvar_no_db(df_transformado, 'vendas_calculado')
            registrar_arquivo(con, nome_arquivo)
            print(f'Arquivo {nome_arquivo} processado e salvo com êxito')
            logs.append(f'Arquivo {nome_arquivo} processado e salvo com êxito')
        
        else:
            print(f'Arquivo {nome_arquivo} já processado anteriormente')
            logs.append(f'Arquivo {nome_arquivo} já processado anteriormente')
    
    return logs

if __name__ == '__main__':
    pipeline()