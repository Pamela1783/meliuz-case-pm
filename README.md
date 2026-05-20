# Méliuz — Case Técnico PM Pleno

Análise do teste A/B/C do In-App Browser e PRD da melhoria proposta.

---

## Estrutura do repositório

```
meliuz-case/
│
├── README.md
│
├── data/
│   ├── raw/                        # CSVs originais entregues pelo Méliuz
│   └── processed/                  # Outputs gerados pela análise
│
├── analysis/
│   ├── 01_exploracao.py            # Estrutura dos dados, grão, joins e distribuição de variantes
│   ├── 02_metricas.py              # Conversão, receita por visita e adoção do browser externo
│   ├── 03_significancia.py         # Teste qui-quadrado e intervalos de confiança
│   └── 04_impacto.py               # Quantificação do impacto da solução proposta
│
├── outputs/
│   ├── resumo_por_variante.csv
│   ├── conversao_por_variante_canal.csv
│   └── saidas_externas_por_termo.csv
│
└── docs/
    ├── entrega_1_perguntas.docx    # Respostas das 6 perguntas
    └── entrega_2_prd.docx          # PRD da melhoria proposta
```

---

## Como reproduzir a análise

**Requisitos:**
```
python >= 3.9
pandas
scipy
numpy
```

**Instalação:**
```bash
pip install pandas scipy numpy
```

**Execução (na ordem):**
```bash
cd analysis
python 01_exploracao.py
python 02_metricas.py
python 03_significancia.py
python 04_impacto.py
```

Os outputs processados são salvos automaticamente em `data/processed/`.

---

## Sobre o processo de análise

A análise foi conduzida com o Claude como agente de suporte, com uma estrutura clara de trabalho: cada etapa foi definida antes da execução, os outputs foram revisados criticamente e nenhum resultado foi aceito sem validação.

O fluxo seguiu a ordem natural de um teste A/B: entendimento do modelo de dados, limpeza e joins relacionais, cálculo de métricas, validação estatística e interpretação dos resultados.

Três validações foram aplicadas durante a análise:
- Verificação do grão das tabelas antes dos joins para evitar distorção nas métricas
- Checagem de contaminação entre variantes (0,94% dos usuários em mais de uma variante, volume baixo o suficiente para não comprometer os resultados)
- Teste qui-quadrado com 95% de confiança para separar diferenças reais de ruído

O pipeline é modular e reutilizável. Para analisar um novo teste A/B, basta substituir os CSVs em `data/raw/` e ajustar o parâmetro de identificação de variante nos scripts. O restante segue igual.

---

## Entregas

| Documento | Descrição |
|---|---|
| `docs/entrega_1_perguntas.docx` | Respostas das 6 perguntas com análise fundamentada nos dados |
| `docs/entrega_2_prd.docx` | PRD completa da melhoria proposta com tasks para engenharia |
