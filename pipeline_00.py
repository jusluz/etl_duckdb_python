# Bibliotecas
import os
import gdown
import duckdb
import pandas as pd
from sqlalchemy import create_engine    
from dotenv import load_dotenv

from duckdb import DuckDBPyRelation
from pandas import DataFrame

load_dotenv()

# Função para baixar arquivos de um diretório do Google Drive
def baixar_arquivos_do_google_drive(url, diretorio_local):
    os.makedirs(diretorio_local, exist_ok=True)
    gdown.download_folder(url_pasta, output=diretorio_local, quiet=False, use_cookies=False)

# Função para listar arquivos CSV em um diretório    
def listar_arquivos_csv(diretorio):
    arquivos_csv = [] 
    todos_os_arquivos = os.listdir(diretorio)
    for arquivo in todos_os_arquivos:
        if arquivo.endswith('.csv'):
            caminho_completo = os.path.join(diretorio, arquivo)
            arquivos_csv.append(caminho_completo) 
    return arquivos_csv

# Função para ler um arquivo CSV
def ler_csv(caminho_arquivo):
    df_duckdb =  duckdb.read_csv(caminho_arquivo)
    #df_duckdb =  duckdb.query('SELECT * FROM "{}"'.format(caminho_arquivo))
    #df_duckdb =  pd.read_csv(caminho_arquivo)
    
    print(df_duckdb)
    print(type(df_duckdb))
    return df_duckdb

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
    return df_transformado

def salvar_no_db(df_duckdb, tabela):
    # Conexão com o banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    # Salva o dataframe em uma tabela no banco de dados
    df_duckdb.to_sql(tabela, con=engine, if_exists='append', index=False)

if __name__ == '__main__':
    url_pasta = 'https://drive.google.com/drive/folders/1UIK54nnkSKf2vEp-91XTBSKMEJ7Kc7R-'
    diretorio_local = './pasta_gdown'
    baixar_arquivos_do_google_drive(url_pasta, diretorio_local)
    listar_arquivos_csv
    lista_de_arquivos = listar_arquivos_csv(diretorio_local)
    
    for caminho_arquivo in lista_de_arquivos:
        duck_db_df = ler_csv(caminho_arquivo)
        pandas_df_transformado = transformar(duck_db_df)
        salvar_no_db(pandas_df_transformado, 'vendas_calculado')

    