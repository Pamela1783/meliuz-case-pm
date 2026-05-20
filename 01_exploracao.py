"""
01_exploracao.py
Exploração inicial dos dados: estrutura das tabelas, grão, joins e distribuição de variantes.
"""

import pandas as pd
import json

# Carregar dados
channels = pd.read_csv('../data/raw/channels.csv')
partners = pd.read_csv('../data/raw/partners.csv')
transactions = pd.read_csv('../data/raw/transactions.csv')
url_params = pd.read_csv('../data/raw/url_params.csv')
visits = pd.read_csv('../data/raw/visits.csv')
visit_meta = pd.read_csv('../data/raw/visit_url_metadata.csv')

print("=== SHAPES ===")
for name, df in zip(['channels','partners','transactions','url_params','visits','visit_meta'],
                    [channels, partners, transactions, url_params, visits, visit_meta]):
    print(f"{name}: {df.shape}")

print("\n=== CANAIS ===")
print(channels)

print("\n=== UTM_CONTENT únicos ===")
print(url_params['utm_content'].value_counts())

print("\n=== UTM_TERM únicos ===")
print(url_params['utm_term'].value_counts(dropna=False))

# Parse metadados
def parse_meta(s):
    try:
        d = json.loads(s)
        return d.get('mz_test_gotoexternalbrowser'), d.get('mz_redirect')
    except:
        return None, None

visit_meta[['variante','mz_redirect']] = pd.DataFrame(
    visit_meta['tracking_url_params'].apply(parse_meta).tolist(),
    index=visit_meta.index
)

print("\n=== DISTRIBUIÇÃO DE VARIANTES ===")
print(visit_meta['variante'].value_counts())

print("\n=== VARIANTE x MZ_REDIRECT ===")
print(pd.crosstab(visit_meta['variante'], visit_meta['mz_redirect']))

print("\n=== NULOS EM VISITS ===")
print(visits.isnull().sum())

visits['visit_at_brt'] = pd.to_datetime(visits['visit_at_brt'])
print(f"\n=== RANGE DE DATAS: {visits['visit_at_brt'].min()} a {visits['visit_at_brt'].max()} ===")

# Verificar grão de transactions
dup = transactions.groupby('visit_id').size()
print(f"\n=== TRANSAÇÕES POR VISIT_ID ===")
print(f"Max: {dup.max()} | Média: {dup.mean():.2f}")
print(dup.value_counts().head())

# Verificar contaminação entre variantes
df = visits.merge(visit_meta[['visit_id','variante']], on='visit_id', how='left')
contaminados = df.groupby('customer_id')['variante'].nunique()
print(f"\n=== CONTAMINAÇÃO ENTRE VARIANTES ===")
print(f"Usuários em mais de uma variante: {(contaminados > 1).sum()}")
print(f"Total de usuários únicos: {contaminados.shape[0]}")
print(f"% contaminados: {(contaminados > 1).sum() / contaminados.shape[0] * 100:.2f}%")

# Distribuição temporal
df['semana'] = pd.to_datetime(df['visit_at_brt']).dt.isocalendar().week
print("\n=== DISTRIBUIÇÃO SEMANAL POR VARIANTE ===")
print(df.groupby(['semana','variante']).size().unstack(fill_value=0))
