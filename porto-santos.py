from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd

def extrair_dados(elemento, nome_tabela):
    html_table = elemento.get_attribute('outerHTML')
    df = pd.read_html(StringIO(html_table))[0]
    colunas_desejadas = [(nome_tabela, 'Mercadoria Goods'), (nome_tabela, 'Operaç Operat'), (nome_tabela, 'Cheg/Arrival d/m/y')]
    
    df_filtrado = df[colunas_desejadas]
    return df_filtrado


def agrupar_dados(df_filtrado, nome_tabela):
    df_importacao = df_filtrado[df_filtrado[(nome_tabela, 'Operaç Operat')].str.contains('DESC|Desc/Emb')]
    df_exportacao = df_filtrado[df_filtrado[(nome_tabela, 'Operaç Operat')].str.contains('EMB|Desc/Emb')]
    
    df_importacao_agrupado = df_importacao.groupby([(nome_tabela, 'Cheg/Arrival d/m/y'), (nome_tabela, 'Mercadoria Goods')]).size().reset_index(name='Quantidade')
    df_exportacao_agrupado = df_exportacao.groupby([(nome_tabela, 'Cheg/Arrival d/m/y'), (nome_tabela, 'Mercadoria Goods')]).size().reset_index(name='Quantidade')
    
    df_importacao_agrupado.columns = ['Chegada', 'Mercadoria', 'Quantidade']
    df_exportacao_agrupado.columns = ['Chegada', 'Mercadoria', 'Quantidade']
    
    return df_importacao_agrupado, df_exportacao_agrupado

url = 'https://www.portodesantos.com.br/informacoes-operacionais/operacoes-portuarias/navegacao-e-movimento-de-navios/navios-esperados-carga'
tabelas = ['LIQUIDO A GRANEL', 'TRIGO', 'GRANEIS DE ORIGEM VEGETAL', 'GRANEIS SOLIDOS - IMPORTACAO', 'GRANEIS SOLIDOS - EXPORTACAO', 'ROLL-IN-ROLL-OFF', 'LASH', 'CABOTAGEM', 'CONTEINERES', 'PRIORIDADE C3', 'PRIORIDADE C5', 'SEM PRIORIDADE']

df_total = pd.DataFrame()

with webdriver.Chrome() as navegador:
    navegador.get(url)
    elementos = WebDriverWait(navegador, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'esperados'))
    )
    
    for i, nome_tabela in enumerate(tabelas):
        print(nome_tabela)
        df_filtrado = extrair_dados(elementos[i], nome_tabela)
        df_importacao_agrupado, df_exportacao_agrupado = agrupar_dados(df_filtrado, nome_tabela)
        
        df_importacao_agrupado['Origem'] = nome_tabela
        df_importacao_agrupado['Sentido'] = 'Importação'
        df_importacao_agrupado['Porto'] = 'Porto de Santos'
        df_exportacao_agrupado['Origem'] = nome_tabela
        df_exportacao_agrupado['Sentido'] = 'Exportação'
        df_exportacao_agrupado['Porto'] = 'Porto de Santos'
        
        df_total = pd.concat([df_total, df_importacao_agrupado, df_exportacao_agrupado])

df_total.to_csv('dados_porto_santos.csv', index=False)