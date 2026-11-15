# Declaração de uso de IA

## Ferramentas e modelos

- Claude (claude.ai, interface web), modelo Claude Sonnet 5.5.
- Codex (aplicativo desktop), modelo GPT-6.

## O que as IAs fizeram

### Claude

- Explicou a diferença entre ativar o ambiente virtual no Linux/macOS e no PowerShell e adaptou os comandos de execução do CLI e da amostra de validação para Windows.
- Explicou opções do pytest para exibir testes aprovados, reprovados e falhas com diferentes níveis de detalhe.
- Ajudou a interpretar a relação entre a conversão de moeda e o teste de regressão, explicou `from __future__ import annotations` e sugeriu uma simplificação para `convert_to_brl`.
- Sugeriu formas de comparar o JSON gerado com o resultado esperado e ajudou a estruturar os documentos de entrega e o registro da sessão.

### Codex

- Apontou lacunas de cobertura nos testes originais, incluindo o teste de ranking cujos IDs coincidiam com a ordem dos valores, e identificou o limite de 200 reservas na leitura do CSV.
- Criou testes adicionais em `tests/test_additional_coverage.py` para o ranking e seu desempate, leitura acima de 200 reservas, status não faturáveis, amostra oficial, argumentos do CLI, diretório de saída, arredondamento, média sem noites e ordenação mensal.
- Revisou o PDF do README do desafio, apontou divergências na documentação de entrega e editou `entrega/README-ENTREGA.md`, incluindo causas raiz e o defeito do limite de 200 reservas.
- Formatou no README de entrega o resultado de testes fornecido: 14 testes aprovados.

## O que eu fiz

- Criei o ambiente virtual, instalei as dependências e executei os testes e o CLI com a amostra de validação.
- Investiguei as falhas dos testes originais e escrevi/apliquei as correções da implementação dos cinco defeitos iniciais: conversão do valor pela multiplicação da taxa usando `Decimal`, cálculo de noites com a diferença entre as datas completas, faturamento somente para `CONFIRMED` e ranking por valor decrescente.
- Depois da revisão de cobertura, removi o limite que interrompia a leitura do CSV após 200 reservas e ajustei o ranking para desempatar pelo `hotel_id` crescente.
- Executei `pytest -q -rA`; os 14 testes passaram. Também executei o CLI na amostra oficial e comparei o relatório com os valores esperados.
