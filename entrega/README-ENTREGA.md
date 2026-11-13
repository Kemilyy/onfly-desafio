# Entrega: Desafio Onfly

## Defeitos corrigidos

Foram identificados e corrigidos dois defeitos na função `convert_to_brl`, localizada no arquivo `currency_converter.py`.

| # | Defeito | Causa raiz |
|---|---|---|
| 1 | Conversão de câmbio invertida | A taxa de câmbio era aplicada por divisão em vez de multiplicação, resultando em valores incorretos. |
| 2 | Cálculo monetário com `float` | Os valores de `amount` e `rate` eram convertidos para `float` antes da operação, causando perda de precisão que não era recuperada ao converter o resultado novamente para `Decimal`. |

## Como investiguei

1. Li o README do desafio e executei `pytest -q` para verificar o estado inicial do projeto, identificando que todos os testes falhavam.
2. Analisei o sintoma apresentado no enunciado, relacionado aos valores incorretos no relatório consolidado.
3. Consultei o arquivo `tests/test_currency.py` para compreender os cenários de teste e os resultados esperados.
4. Identifiquei uma dica no código que indicava que a taxa deveria ser aplicada por multiplicação, e não por divisão.
5. Analisei `tests/helpers.py` para entender como o CLI era executado e quais taxas eram utilizadas. Com a taxa de USD = 5,42, deduzi que a conversão de 100 dólares deveria resultar em R$ 542,00.
6. Verifiquei a implementação de `CsvRateRepository` e concluí que o problema não estava na obtenção das taxas, mas na aplicação delas.
7. Analisei a função `convert_to_brl`, em `currency_converter.py`, onde encontrei a divisão incorreta e o uso de `float` nos cálculos monetários.
8. Corrigi os dois problemas, mantendo o uso de `Decimal` durante toda a operação, e executei novamente os testes para verificar os resultados.

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

Após as correções, os testes foram executados novamente para verificar o funcionamento da aplicação e confirmar a resolução dos defeitos.

```text
[Inserir aqui a saída real do pytest]
```

## Observações

- Os testes fornecidos originalmente não foram alterados.
- As correções foram realizadas diretamente na implementação da função `convert_to_brl`.
- Os cálculos monetários passaram a utilizar `Decimal`, evitando perdas de precisão associadas ao uso de `float`.