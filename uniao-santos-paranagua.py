import pandas as pd

df_santos = pd.read_csv('dados_porto_santos.csv')
df_paranagua = pd.read_csv('dados_porto_paranagua.csv')

df_total = pd.concat([df_santos, df_paranagua], ignore_index=True)


df_total.to_csv('dados_portos.csv', index=False)
print("Dados juntos 'dados_portos.csv'")

df_ordenado = df_total.sort_values(by='Quantidade', ascending=False)
df_ordenado.to_csv('dados_portos_ordenado_por_quanitade.csv', index=False)

print("Dados organizados por 'Mercadoria' e 'Quantidade' e salvos em 'dados_portos_ordenado.csv'")
