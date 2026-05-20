"""
02_metricas.py
Cálculo das métricas principais: conversão, receita por visita e adoção do browser externo.
"""

import pandas as pd
import json

visits = pd.read_csv('../data/raw/visits.csv')
visit_meta = pd.read_csv('../data/raw/visit_url_metadata.csv')
transactions = pd.read_csv('../data/raw/transactions.csv')
url_params = pd.read_csv('../data/raw/url_params.csv')
partners = pd.read_csv('../data/raw/partners.csv')
channels = pd.read_csv('../data/raw/channels.csv')

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

df = visits.merge(visit_meta[['visit_id','variante','mz_redirect']], on='visit_id', how='left')
df = df.merge(url_params, on='url_param_id', how='left')
df = df.merge(partners, on='partner_id', how='left')
df = df.merge(channels, on='channel_id', how='left')

# Flag de conversão (binária por visit_id)
has_transaction = transactions.groupby('visit_id').size().reset_index(name='n_transactions')
df = df.merge(has_transaction, on='visit_id', how='left')
df['converted'] = df['n_transactions'].notna()

# Receita por visita
tx_agg = transactions.groupby('visit_id').agg(
    total_sale=('sale_amount','sum'),
    total_cashback=('cashback_amount','sum')
).reset_index()
df = df.merge(tx_agg, on='visit_id', how='left')

# Resumo por variante
conv = df.groupby('variante').agg(
    visitas=('visit_id','count'),
    convertidas=('converted','sum'),
    saidas_externas=('mz_redirect', lambda x: (x=='browserdefault').sum()),
    receita_total=('total_sale','sum'),
).reset_index()
conv['taxa_conversao_pct'] = (conv['convertidas'] / conv['visitas'] * 100).round(2)
conv['taxa_adocao_ext_pct'] = (conv['saidas_externas'] / conv['visitas'] * 100).round(2)
conv['receita_por_visita'] = (conv['receita_total'] / conv['visitas']).round(2)

print("=== RESUMO POR VARIANTE ===")
print(conv.to_string(index=False))
conv.to_csv('../data/processed/resumo_por_variante.csv', index=False)

# Conversão por variante x canal
conv2 = df.groupby(['variante','mz_redirect']).agg(
    visitas=('visit_id','count'),
    convertidas=('converted','sum'),
    receita_total=('total_sale','sum'),
).reset_index()
conv2['taxa_conversao_pct'] = (conv2['convertidas'] / conv2['visitas'] * 100).round(2)
conv2['receita_por_visita'] = (conv2['receita_total'] / conv2['visitas']).round(2)

print("\n=== CONVERSÃO POR VARIANTE x CANAL ===")
print(conv2.to_string(index=False))
conv2.to_csv('../data/processed/conversao_por_variante_canal.csv', index=False)

# Saídas externas por utm_term
ext = df[df['utm_content']=='EXTERNAL_BROWSER_MODAL'].copy()
ext_resumo = ext.groupby(['variante','utm_term']).agg(
    visitas=('visit_id','count'),
    convertidas=('converted','sum'),
    receita_total=('total_sale','sum'),
).reset_index()
ext_resumo['taxa_conversao_pct'] = (ext_resumo['convertidas'] / ext_resumo['visitas'] * 100).round(2)
ext_resumo['receita_por_visita'] = (ext_resumo['receita_total'] / ext_resumo['visitas']).round(2)

print("\n=== SAÍDAS EXTERNAS POR UTM_TERM ===")
print(ext_resumo.to_string(index=False))
ext_resumo.to_csv('../data/processed/saidas_externas_por_termo.csv', index=False)
