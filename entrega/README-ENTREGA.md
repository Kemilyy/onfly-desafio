# Entrega: Desafio Onfly

## Defeitos corrigidos

| # | Defeito | Causa raiz |
|---|---|---|
| 1 | Conversão de câmbio invertida | A função dividia o valor pela taxa, em vez de multiplicá-lo por `rate_to_brl`. |
| 2 | Cálculo monetário com `float` | A função convertia `amount` e `rate` para `float`, perdendo precisão antes de retornar o resultado como `Decimal`. |
| 3 | Cálculo de noites entre meses | O cálculo subtraía apenas o dia do mês (`checkout.day - checkin.day`), ignorando mês e ano. |
| 4 | Status faturáveis incorretos | A função considerava faturável qualquer status diferente de `CANCELLED`, incluindo `NO_SHOW`, em vez de aceitar somente `CONFIRMED`. |
| 5 | Ordem do ranking de hotéis | O ranking ordenava os valores em ordem crescente; a regra exige ordem decrescente e desempate por `hotel_id` crescente. |
| 6 | Leitura parcial do CSV de reservas | O repositório interrompia a leitura ao chegar a 200 reservas, deixando de incluir as linhas seguintes. |

## Como investiguei

1. Li o README do desafio e executei `pytest -q` para identificar o estado inicial dos testes.
2. Analisei as falhas e relacionei cada cenário ao teste, ao arquivo e à função correspondentes.
3. Conferi as regras e as docstrings do código para localizar a causa de cada resultado incorreto.
4. Corrigi o câmbio, o cálculo de noites, a regra de faturamento e a ordenação dos hotéis; depois, executei novamente os testes originais.
5. Após os testes originais passarem, pedi à IA uma revisão da cobertura em relação aos requisitos. Essa revisão identificou o limite de 200 linhas no repositório de reservas, que também foi removido.
6. Acrescentei testes para o ranking com desempate, arquivos com mais de 200 reservas, exclusão de reservas não confirmadas, amostra oficial, argumentos do CLI, arredondamento, média sem noites e ordenação mensal.

## Como validar

Para configurar o ambiente e executar os testes:

```bash
python3.11 -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
pytest -v
```

Para gerar o relatório consolidado:

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

## Resultado dos testes

Comando executado no ambiente virtual:

```powershell
pytest -q 
```

```text
.............. 
14 passed in 4.25s
```
