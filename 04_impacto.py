"""
04_impacto.py
Quantificação do impacto potencial da solução proposta para o login social.
"""

import pandas as pd
import json
import numpy as np

visits = pd.read_csv('../data/raw/visits.csv')
visit_meta = pd.read_csv('../data/raw/visit_url_metadata.csv')
transactions = pd.read_csv('../data/raw/transactions.csv')
url_params = pd.read_csv('../data/raw/url_params.csv')

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

has_transaction = transactions.groupby('visit_id').size().reset_index(name='n_transactions')
df = df.merge(has_transaction, on='visit_id', how='left')
df['converted'] = df['n_transactions'].notna()

tx_agg = transactions.groupby('visit_id').agg(
    total_sale=('sale_amount','sum')
).reset_index()
df = df.merge(tx_agg, on='visit_id', how='left')

# Saídas por login social
login_visits = df[
    (df['utm_content'] == 'EXTERNAL_BROWSER_MODAL') &
    (df['utm_term'] == 'LOGIN')
].copy()

# Referência InApp
inapp = df[df['mz_redirect'] == 'inapp']
inapp_conv = inapp['converted'].mean()
inapp_receita_media = inapp['total_sale'].mean()

total_login = len(login_visits)
conv_atual = login_visits['converted'].mean()
conv_potencial = inapp_conv

ganho_conversoes = (conv_potencial - conv_atual) * total_login
ganho_receita = ganho_conversoes * inapp_receita_media

print("=== IMPACTO POTENCIAL DA SOLUÇÃO PROPOSTA ===\n")
print(f"Total de saídas por LOGIN no período: {total_login:,}")
print(f"Conversão atual (LOGIN): {conv_atual*100:.2f}%")
print(f"Conversão de referência (InApp): {inapp_conv*100:.2f}%")
print(f"Diferença: {(conv_potencial - conv_atual)*100:.2f} pp")
print(f"\nGanho estimado de conversões: +{ganho_conversoes:.0f}")
print(f"Ganho estimado de receita: R$ {ganho_receita:,.2f}")
print(f"\nNota: projeção conservadora assumindo recuperação total da diferença de conversão.")
print(f"Resultado real dependerá da taxa de retorno ao app após login externo.")
