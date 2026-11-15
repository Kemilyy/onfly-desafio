
---

**kemily:**

```
PS C:\Users\kemil\Projects\onfly-desafio> python3.11 -m venv .venv
PS C:\Users\kemil\Projects\onfly-desafio> source .venv/bin/activate
source : O termo 'source' não é reconhecido como nome de cmdlet, função, arquivo de script ou programa operável. Verifique a grafia do nome 
ou, se um caminho tiver sido incluído, veja se o caminho está correto e tente novamente.
No linha:1 caractere:1
+ source .venv/bin/activate
+ ~~~~~~
    + CategoryInfo          : ObjectNotFound: (source:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\kemil\Projects\onfly-desafio>
```

**Claude:**

O erro acontece porque o source .venv/bin/activate é um comando de Linux/macOS (bash). Você está no PowerShell do Windows, que não tem o source e usa outra pasta (Scripts em vez de bin).

Ativar o ambiente virtual no PowerShell
```powershell
.venv\Scripts\Activate.ps1
```

Se aparecer um erro de "execução de scripts desabilitada", libere para a sessão atual e tente de novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Quando funcionar, você verá (.venv) no início do prompt.

Instalar as dependências
```powershell
pip install -r requirements-dev.txt
```

Rodar o CLI

No PowerShell, a barra invertida \ do README não funciona para quebrar linha (o PowerShell usa crase `), e a sintaxe PYTHONPATH=src também não existe. Use assim:

```powershell
$env:PYTHONPATH = "src"
python -m onfly_report `
  --input data/reservas_hoteis.csv `
  --rates data/taxas_cambio.csv `
  --output output/report.json
```

Ou tudo em uma linha:

```powershell
$env:PYTHONPATH = "src"; python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Observação: o README na imagem mostra onfly\_report, reservas\_hoteis.csv etc. com \_. Isso é só um artefato de formatação do Markdown. Os nomes reais usam _ simples, como acima.

Rodar os testes
```powershell
pytest -q
```

Se o pytest não for reconhecido, use python -m pytest -q.

Alternativa: usar o Git Bash ou WSL

Se preferir seguir o README exatamente como está, abra o Git Bash ou o WSL, onde source .venv/bin/activate e PYTHONPATH=src funcionam normalmente. Note que no Git Bash a ativação às vezes é source .venv/Scripts/activate, porque o venv criado no Windows usa a pasta Scripts.

**kemily:**

tem algum comando para eu ver quais testes passaram e não só os que falharam?

**Claude:**

Sim, use a flag -v (verbose), que lista cada teste com PASSED ou FAILED:

```powershell
pytest -v
```

Saída de exemplo:

```
tests/test_report.py::test_total_por_hotel PASSED
tests/test_report.py::test_conversao_cambio FAILED
```

Outras opções úteis

Mostrar o motivo de todos os testes que passaram também, com o resumo no final:

```powershell
pytest -rA
```

Mostrar só um resumo dos passados (-rp) ou dos falhados (-rf):

```powershell
pytest -rp
pytest -rf
```

Combinar verbose com resumo curto das falhas:

```powershell
pytest -v --tb=short
```

Rodar um arquivo ou um teste específico:

```powershell
pytest tests/test_report.py -v
pytest tests/test_report.py::test_conversao_cambio -v
```

Rodar só os que falharam na última execução (ótimo enquanto você corrige o código):

```powershell
pytest --lf -v
```

A combinação que mais ajuda no dia a dia é pytest -v --tb=short: mostra cada teste com seu status e um traceback enxuto para os que falharam.

**Claude:**

Essa linha muda como o Python trata as anotações de tipo (aquelas dicas como amount: Decimal ou -> Decimal). Sem ela, o Python avalia a anotação no momento em que a função é definida. Com ela, a anotação vira apenas texto e só é avaliada se alguém precisar.

O que você ganha com isso

1. Referências a tipos ainda não definidos (forward references)

```python
# Sem o import: dá NameError
class No:
    def proximo(self) -> No:   # "No" ainda não existe aqui
        ...

# Com o import: funciona
from __future__ import annotations

class No:
    def proximo(self) -> No:
        ...
```

Sem o import, você teria que escrever -> "No" (entre aspas).

2. Sintaxe moderna em versões antigas

```python
from __future__ import annotations

def somar(valores: list[int], taxa: int | None = None) -> dict[str, int]:
    ...
```

list[int] e int | None funcionam como anotação mesmo em versões que ainda não os aceitariam em tempo de execução. No seu projeto (Python 3.11+) isso já funciona sem o import, então ele é mais uma convenção segura do que uma necessidade.

3. Importar tipos só para checagem

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal   # só o mypy/IDE precisa dele

def convert(amount: Decimal) -> Decimal:
    ...
```

Isso evita imports circulares e acelera a inicialização, porque a anotação não é avaliada em execução.

O que não muda

As anotações continuam sem fazer checagem em execução. O Python não impede você de passar um str onde se espera Decimal. Quem usa as anotações são ferramentas como mypy, pyright e o autocompletar da sua IDE.

Cuidado

Bibliotecas que leem anotações em tempo de execução (como Pydantic ou dataclasses com get_type_hints) recebem strings. Normalmente elas resolvem isso sozinhas, mas é um ponto a lembrar se algo estranho acontecer.

Resumo para o seu código

No convert_to_brl, a linha from __future__ import annotations não afeta o resultado do cálculo. Você pode deixá-la como está, porque é o padrão adotado pelo projeto e não atrapalha em nada.

**kemily:**

qual o equivalente desses comandos no powershell?

**Claude:**

Mesma ideia de antes: defina o PYTHONPATH com $env: e use a crase ` para quebrar linha.

```powershell
$env:PYTHONPATH = "src"
python -m onfly_report `
  --input data/exemplo-validacao.csv `
  --rates data/taxas_cambio.csv `
  --output output/exemplo.json
```

Ou em uma linha só:

```powershell
$env:PYTHONPATH = "src"; python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
```

Lembre de tirar as barras \_ que aparecem na imagem (onfly\_report, taxas\_cambio.csv). Os nomes reais usam _ simples.

Ver o resultado

O CLI grava em output/exemplo.json. Para abrir o conteúdo no terminal:

```powershell
Get-Content output/exemplo.json
```

Ou, para ver formatado e facilitar a comparação com o resultado esperado do desafio:

```powershell
Get-Content output/exemplo.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

Comparar com o esperado

Se o desafio fornecer o JSON esperado em um arquivo (por exemplo data/exemplo-esperado.json), você pode comparar direto:

```powershell
Compare-Object (Get-Content output/exemplo.json) (Get-Content data/exemplo-esperado.json)
```

Sem saída significa que os arquivos são idênticos. Se o esperado estiver apenas no texto do README, compare os campos manualmente, prestando atenção em casas decimais ("1542.00" é diferente de "1542.0").

Observação: o $env:PYTHONPATH vale só para a sessão atual do PowerShell. Se abrir um terminal novo, defina de novo.

---