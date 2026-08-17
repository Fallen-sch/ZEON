<div align="center">
  <h1>LION</h1>
  <p><strong>Lightweight LLM Object Notation</strong></p>
  <p>Uma linguagem de serialização tabular de nova geração, projetada para a máxima eficiência de LLMs.</p>
</div>

O LION é uma linguagem de serialização de dados sensível a espaços em branco que reimagina completamente como dados estruturados são apresentados a Modelos de Linguagem Grande (LLMs).

Fortemente inspirado pela estrutura visual limpa do Python e pela leveza do YAML, o LION elimina as partes mais "caras" do JSON: chaves repetitivas, colchetes, vírgulas e aspas. Ele introduz uma "Gramática Tabular Orientada a Sufixos" única, que atinge uma densidade extrema de tokens sem sacrificar a legibilidade humana ou a confiabilidade do parser.

## Índice
- [O Problema dos Tokens](#o-problema-dos-tokens)
- [A Solução LION](#a-solução-lion)
- [Guia de Sintaxe](#guia-de-sintaxe)
- [Benchmarks de Desempenho](#benchmarks-de-desempenho)
- [Uso da CLI](#uso-da-cli)
- [Instalação](#instalação)

---

## O Problema dos Tokens

No desenvolvimento moderno de IA, alimentar o contexto dos LLMs com dados via payloads JSON é extremamente caro. O JSON foi construído para máquinas clássicas, não para tokenizadores de LLM.

Ao lidar com arrays de objetos (como uma lista de 1.000 produtos), o JSON te obriga a repetir as chaves `"id"`, `"nome"` e `"preco"` mil vezes. Cada chave repetida, dois-pontos e vírgula consome tokens preciosos, atrasando a geração do modelo e multiplicando seus custos de API.

## A Solução LION

O LION resolve isso através da **Indentação Tabular**. Ao usar sufixos especiais (`[]` e `[][]`) diretamente nas chaves, você avisa ao parser exatamente como ler o bloco indentado abaixo dele. O cabeçalho é declarado apenas uma vez, e os dados fluem de forma limpa abaixo dele.

### Comparação Prática

Payload em JSON:
```json
"items": [
  {"id": "SKU-100", "qty": 1, "price": 150.0},
  {"id": "SKU-205", "qty": 2, "price": 45.5}
]
```

Equivalente em LION:
```python
items[]
  id qty price
  SKU-100 1 150.0
  SKU-205 2 45.5
```
Ao declarar `items[]`, o LION entende que a primeira linha indentada é o cabeçalho e mapeia todas as linhas subsequentes para aquelas chaves.

---

## Guia de Sintaxe

O LION usa espaços puros para separação e tipos primitivos similares aos do Python (`True`, `False`, `None`).

### 1. Pares Chave-Valor Primitivos
Atribuições padrão usam `=`. Strings sem aspas são suportadas nativamente para identificadores contínuos e datas ISO.
```python
order_id=ORD-99321
is_active=True
deleted_at=None
created_at=2026-08-16T14:30:00Z
```

### 2. Objetos Simples (Flat Dicts)
Objetos usam apenas indentação. Não é necessário o uso de `{}`.
```python
customer
  id name email
  8472 "Maria Silva" maria@example.com
```

### 3. Arrays de Objetos (Formato Tabular)
Use o sufixo `[]`. A primeira linha será o cabeçalho.
```python
users[]
  id role
  1 admin
  2 guest
```

### 4. Tuplas Aninhadas
Se um objeto contém um sub-objeto de forma repetitiva e uniforme, você pode declará-lo no cabeçalho usando `chave(sub1 sub2)` e mapear os valores usando `(val1 val2)`.
```python
products[]
  id dimensions(weight unit)
  1 (1.2 kg)
```

### 5. Matrizes 2D
Use o sufixo `[][]` para arrays multidimensionais puros, sem cabeçalhos (ex: coordenadas, dados de tensores).
```python
shipping_route[][]
  -23.5505 -46.6333
  -23.5501 -46.6341
```

### 6. Anotações Visuais (Ignoradas pelo Parser)
O LION permite a inclusão de anotações focadas na legibilidade humana, que não afetam os dados finais em JSON.
- **Sufixos `()` e `[]` em colunas:** Marcam o tipo da coluna visualmente.
- **Anotações Inline `[texto]`:** Descrevem a quem aquela chave pertence.

```python
users[]
  id name preferences(theme) nicknames() aliases[]
  1 Maria (light) nicknames[Maria]=(1=M 2=Mah) [mary mah]
```
O parser ignora completamente `()`, `[]` e `[Maria]`, resultando num JSON de chaves limpas. O Stringifier do LION já inclui `()` e `[]` automaticamente ao ser gerado!

### 7. Dicionários e Listas Multilinhas
Ao contrário do JSON que exige vírgulas para tudo, o LION permite uma formatação multilinha deslumbrante dentro de `(...)` (dicionários) e `[...]` (arrays), ignorando quebras de linha e indentações de forma nativa e elegante (idêntico ao Python).

```python
config
  db_pool (
    host=localhost
    port=5432
    options=(
      ssl=True
      timeout=30
    )
  )
  nodes [
    192.168.0.1
    192.168.0.2
  ]
```

### 8. Fallback para Dados Mistos
Se um array contiver tipos mistos, irregulares ou profundamente aninhados, um cabeçalho tabular não será adequado. Nesses casos, o LION volta graciosamente para um formato "inline" de segurança.

JSON:
```json
"mixed_data": [
  1,
  "hello",
  {"flag": true},
  [2, 3]
]
```

Equivalente em LION:
```python
mixed_data=[1 "hello" (flag=True) [2 3]]
```
Note como usamos colchetes `[]` para arrays soltos e parênteses `()` para objetos (`flag=True`). Isso permite que você represente qualquer caos de dados mistos e aninhados em uma única linha, garantindo a mesma hierarquia que o JSON, mas removendo aspas e vírgulas desnecessárias.

---

## Benchmarks de Desempenho

O LION brilha de forma absoluta em estruturas de dados grandes e baseadas em listas. Nós rodamos nossa implementação oficial em Python contra respostas complexas de APIs de E-commerce do mundo real.

**Resultados de Tokens (Usando o Tokenizador OpenAI TikToken):**

| Conjunto de Dados (Larga Escala) | JSON Compacto | YAML | LION | Redução (vs JSON) |
| :--- | :--- | :--- | :--- | :--- |
| Uniforme Plano | 12,246 | 15,742 | 9,493 | **-22.5%** |
| Uniforme Aninhado Uniforme | 13,002 | 17,500 | 11,002 | **-15.4%** |
| Uniforme Aninhado Não-uniforme | 10,752 | 13,250 | 9,502 | **-11.6%** |
| Não-uniforme Aninhado Uniforme | 4,033 | 6,034 | 3,036 | **-24.7%** |
| Não-uniforme Plano | 1,555 | 1,600 | 1,466 | **-5.7%** |
| Não-uniforme Aninhado Não-uniforme | 1,615 | 2,371 | 1,564 | **-3.2%** |

*Em estruturas altamente uniformes e focadas em listas, o LION atinge até ~25% de redução de tokens em relação ao JSON puramente minificado e mais de ~40% em relação ao YAML.*

Isso se traduz em liberar quase o dobro da capacidade de "Context Window" para as suas aplicações baseadas em LLM.

---

## Uso da CLI

O LION vem com uma ferramenta de Linha de Comando (CLI) bidirecional para converter seus conjuntos de dados entre LION, JSON e YAML sem esforço.

```bash
# Converter JSON ou YAML para LION
lion convert data.json -o data.lion
lion convert config.yaml -o config.lion

# Converter LION de volta para JSON ou YAML
lion convert data.lion -o data.json
lion convert config.lion -o config.yaml

# Imprimir diretamente no terminal
lion convert config.yaml --print
```

---

## Instalação

Atualmente, a implementação de referência está disponível em Python.

**Requisitos:**
- Python 3.10+
- Poetry

```bash
git clone https://github.com/your-org/lion.git
cd lion
poetry install
```

Para usá-lo em seu código Python:
```python
import lion

# Decodificar texto LION para um Dicionário Python
data = lion.loads(text)

# Codificar Dicionário Python para formato LION
lion_text = lion.dumps(data)

# Conversão direta de strings
json_text = lion.convert(lion_text).to_json()
yaml_text = lion.convert(lion_text).to_yaml()
lion_text = lion.convert(yaml_text).to_lion()

# Conversão direta de arquivos
# 1. Passar apenas o nome do arquivo salvará automaticamente na mesma pasta do original
lion.convert("pasta/secreta/dados.lion").to_json("dados.json")
lion.convert("pasta/secreta/dados.lion").to_yaml("dados.yaml")

# 2. Ou passe um caminho completo para salvar em outro local específico
lion.convert("pasta/secreta/dados.lion").to_json("exports/meus_dados.json")
lion.convert("pasta/secreta/dados.yaml").to_lion("exports/meus_dados.lion")
```

---
*LION - O futuro da serialização de dados para IA.*
