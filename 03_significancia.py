"""
03_significancia.py
Teste qui-quadrado e intervalos de confiança para validação estatística das diferenças entre variantes.
"""

import pandas as pd
import json
import numpy as np
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

visits = pd.read_csv('../data/raw/visits.csv')
visit_meta = pd.read_csv('../data/raw/visit_url_metadata.csv')
transactions = pd.read_csv('../data/raw/transactions.csv')

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
has_transaction = transactions.groupby('visit_id').size().reset_index(name='n_transactions')
df = df.merge(has_transaction, on='visit_id', how='left')
df['converted'] = df['n_transactions'].notna().astype(int)

agg = df.groupby('variante').agg(
    visitas=('visit_id','count'),
    convertidas=('converted','sum')
).reset_index()
agg['nao_convertidas'] = agg['visitas'] - agg['convertidas']
agg['taxa'] = agg['convertidas'] / agg['visitas']

# Intervalo de confiança 95% (Wilson score interval)
def wilson_ci(p, n, z=1.96):
    denom = 1 + z**2/n
    center = (p + z**2/(2*n)) / denom
    margin = (z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))) / denom
    return center - margin, center + margin

print("=== TAXA DE CONVERSÃO COM INTERVALO DE CONFIANÇA 95% ===\n")
for _, row in agg.iterrows():
    lo, hi = wilson_ci(row['taxa'], row['visitas'])
    print(f"Variante {row['variante'].upper()}: {row['taxa']*100:.4f}%  |  IC 95%: [{lo*100:.4f}%, {hi*100:.4f}%]  |  n={int(row['visitas']):,}")

# Teste qui-quadrado geral
contingency = np.array([
    agg[agg['variante']=='a'][['convertidas','nao_convertidas']].values[0],
    agg[agg['variante']=='b'][['convertidas','nao_convertidas']].values[0],
    agg[agg['variante']=='c'][['convertidas','nao_convertidas']].values[0],
])

chi2, p, dof, _ = chi2_contingency(contingency)
print(f"\n=== TESTE QUI-QUADRADO GERAL (A vs B vs C) ===")
print(f"Chi2: {chi2:.4f} | p-valor: {p:.6f} | graus de liberdade: {dof}")
print(f"Resultado: {'SIGNIFICANTE (p < 0.05)' if p < 0.05 else 'NÃO significante'}")

# Testes par a par
print("\n=== TESTES PAR A PAR ===")
for v1, v2 in [('a','b'), ('a','c'), ('b','c')]:
    r1 = agg[agg['variante']==v1].iloc[0]
    r2 = agg[agg['variante']==v2].iloc[0]
    ct = np.array([
        [r1['convertidas'], r1['nao_convertidas']],
        [r2['convertidas'], r2['nao_convertidas']]
    ])
    chi2_p, p_p, _, _ = chi2_contingency(ct)
    diff = (r2['taxa'] - r1['taxa']) * 100
    print(f"\n{v1.upper()} vs {v2.upper()}:")
    print(f"  Diferença: {diff:+.4f} pp")
    print(f"  p-valor: {p_p:.6f} | {'SIGNIFICANTE' if p_p < 0.05 else 'NÃO significante'}")
