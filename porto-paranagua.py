from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd

def extrair_dados(elemento, nome_tabela):
    html_table = elemento.get_attribute('outerHTML')
    df = pd.read_html(StringIO(html_table))[0]
    colunas_desejadas = [(nome_tabela, 'Mercadoria'), (nome_tabela, 'Sentido'), 
                        (nome_tabela, 'Chegada' if nome_tabela != 'ESPERADOS' else 'ETA')]
    df_filtrado = df[colunas_desejadas].copy()

    coluna_chegada = (nome_tabela, 'Chegada' if nome_tabela != 'ESPERADOS' else 'ETA')
    df_filtrado[coluna_chegada] = pd.to_datetime(
        df_filtrado[coluna_chegada],
        format='%d/%m/%Y %H:%M', 
        errors='coerce', 
        dayfirst=True
    ).dt.strftime('%d/%m/%Y')

    return df_filtrado

def agrupar_dados(df_filtrado, nome_tabela):
    df_importacao = df_filtrado[df_filtrado[(nome_tabela, 'Sentido')].str.contains('Imp|Imp/Exp')]
    df_exportacao = df_filtrado[df_filtrado[(nome_tabela, 'Sentido')].str.contains('Exp|Imp/Exp')]
    
    df_importacao_agrupado = df_importacao.groupby([(nome_tabela, 'Chegada' if nome_tabela != 'ESPERADOS' else 'ETA'),
                                                    (nome_tabela, 'Mercadoria')]).size().reset_index(name='Quantidade')
    df_exportacao_agrupado = df_exportacao.groupby([(nome_tabela, 'Chegada' if nome_tabela != 'ESPERADOS' else 'ETA'), 
                                                    (nome_tabela, 'Mercadoria')]).size().reset_index(name='Quantidade')
    
    df_importacao_agrupado.columns = ['Chegada', 'Mercadoria', 'Quantidade']
    df_exportacao_agrupado.columns = ['Chegada', 'Mercadoria', 'Quantidade']
    
    return df_importacao_agrupado, df_exportacao_agrupado


url = 'https://www.appaweb.appa.pr.gov.br/appaweb/pesquisa.aspx?WCI=relLineUpRetroativo'
tabelas = ['ATRACADOS', 'PROGRAMADOS', 'AO LARGO PARA REATRACAÇÃO', 'AO LARGO', 'ESPERADOS', 'DESPACHADOS']

df_total = pd.DataFrame()

with webdriver.Chrome() as navegador:
    navegador.get(url)
    elementos = WebDriverWait(navegador, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.table.table-bordered.table-striped.table-hover'))
    )
    
    for i, nome_tabela in enumerate(tabelas):
        if nome_tabela == 'DESPACHADOS':
            elemento = elementos[i + 1]
        else:
            elemento = elementos[i]
        
        print(nome_tabela)
        df_filtrado = extrair_dados(elemento, nome_tabela)
        df_importacao_agrupado, df_exportacao_agrupado = agrupar_dados(df_filtrado, nome_tabela)
        
        df_importacao_agrupado['Origem'] = nome_tabela
        df_importacao_agrupado['Sentido'] = 'Importação'
        df_importacao_agrupado['Porto'] = 'Porto Paranaguá'
        df_exportacao_agrupado['Origem'] = nome_tabela
        df_exportacao_agrupado['Sentido'] = 'Exportação'
        df_exportacao_agrupado['Porto'] = 'Porto Paranaguá'
        
        
        df_total = pd.concat([df_total, df_importacao_agrupado, df_exportacao_agrupado])

df_total.to_csv('dados_porto_paranagua.csv', index=False)

