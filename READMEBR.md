<div align="center">
  <h1>ZEON</h1>
  <p><strong>Zero-overhead Encoding Object Notation</strong></p>
  <p>Uma linguagem de serialização tabular de nova geração, projetada para a máxima eficiência de LLMs.</p>
</div>

O ZEON é uma linguagem de serialização de dados sensível a espaços em branco que reimagina completamente como dados estruturados são apresentados a Modelos de Linguagem Grande (LLMs).

Fortemente inspirado pela estrutura visual limpa do Python e pela leveza do YAML, o ZEON elimina as partes mais "caras" do JSON: chaves repetitivas, colchetes, vírgulas e aspas. Ele introduz uma "Gramática Tabular Orientada a Sufixos" única, que atinge uma densidade extrema de tokens sem sacrificar a legibilidade humana ou a confiabilidade do parser.

## Índice
- [O Problema dos Tokens](#o-problema-dos-tokens)
- [A Solução ZEON](#a-solução-zeon)
- [Guia de Sintaxe](#guia-de-sintaxe)
- [Benchmarks de Desempenho](#benchmarks-de-desempenho)
- [Uso da CLI](#uso-da-cli)
- [Instalação](#instalação)

---

## O Problema dos Tokens

No desenvolvimento moderno de IA, alimentar o contexto dos LLMs com dados via payloads JSON é extremamente caro. O JSON foi construído para máquinas clássicas, não para tokenizadores de LLM.

Ao lidar com arrays de objetos (como uma lista de 1.000 produtos), o JSON te obriga a repetir as chaves `"id"`, `"nome"` e `"preco"` mil vezes. Cada chave repetida, dois-pontos e vírgula consome tokens preciosos, atrasando a geração do modelo e multiplicando seus custos de API.

## A Solução ZEON

O ZEON resolve isso através da **Indentação Tabular**. Ao usar sufixos especiais (`[]` e `[][]`) diretamente nas chaves, você avisa ao parser exatamente como ler o bloco indentado abaixo dele. O cabeçalho é declarado apenas uma vez, e os dados fluem de forma limpa abaixo dele.

### Comparação Prática

Payload em JSON:
```json
"items": [
  {"id": "SKU-100", "qty": 1, "price": 150.0},
  {"id": "SKU-205", "qty": 2, "price": 45.5}
]
```

Equivalente em ZEON:
```python
items[]
  id qty price
  SKU-100 1 150.0
  SKU-205 2 45.5
```
Ao declarar `items[]`, o ZEON entende que a primeira linha indentada é o cabeçalho e mapeia todas as linhas subsequentes para aquelas chaves.

---

## Guia de Sintaxe

O ZEON usa espaços puros para separação e tipos primitivos similares aos do Python (`True`, `False`, `None`).

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
O ZEON permite a inclusão de anotações focadas na legibilidade humana, que não afetam os dados finais em JSON.
- **Sufixos `()` e `[]` em colunas:** Marcam o tipo da coluna visualmente.
- **Anotações Inline `[texto]`:** Descrevem a quem aquela chave pertence.

```python
users[]
  id name preferences(theme) nicknames() aliases[]
  1 Maria (light) nicknames[Maria]=(1=M 2=Mah) [mary mah]
```
O parser ignora completamente `()`, `[]` e `[Maria]`, resultando num JSON de chaves limpas. O Stringifier do ZEON já inclui `()` e `[]` automaticamente ao ser gerado!

### 7. Dicionários e Listas Multilinhas
Ao contrário do JSON que exige vírgulas para tudo, o ZEON permite uma formatação multilinha deslumbrante dentro de `(...)` (dicionários) e `[...]` (arrays), ignorando quebras de linha e indentações de forma nativa e elegante (idêntico ao Python).

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

### 8. Formato Híbrido (Tabular + Inline)
Se um array contiver objetos semi-uniformes (ex: logs de evento em que apenas algumas linhas possuem propriedades extras), o ZEON encontra a interseção de chaves em comum para o cabeçalho e anexa as propriedades excedentes na mesma linha.

```python
event_logs[]
  timestamp level message
  2026-08-17T10:00:00Z INFO "User logged in" user_id=405
  2026-08-17T10:01:00Z ERROR "DB Timeout" retry_count=3 context=(db=users)
```
Isso garante alta economia de tokens mesmo em dados sujos e despadronizados.

### 9. Tabelas Chaveadas (Keyed Tabular)
Ao lidar com dicionários de objetos uniformes (como feature flags ou configurações de ambientes), o ZEON usa o sufixo `{}`. O primeiro valor de cada linha torna-se a chave do dicionário, eliminando a repetição contínua das chaves aninhadas.

```python
environments{}
  region replicas debug
  production eu-central-1 6 False
  staging eu-central-1 2 True
```

### 10. Fallback para Dados Mistos
Se um array contiver tipos mistos, irregulares ou profundamente aninhados onde um cabeçalho não existe, o ZEON volta graciosamente para um formato "inline" de segurança.

JSON:
```json
"mixed_data": [
  1,
  "hello",
  {"flag": true},
  [2, 3]
]
```

Equivalente em ZEON:
```python
mixed_data=[1 "hello" (flag=True) [2 3]]
```
Note como usamos colchetes `[]` para arrays soltos e parênteses `()` para objetos (`flag=True`). Isso permite que você represente qualquer caos de dados mistos e aninhados em uma única linha, garantindo a mesma hierarquia que o JSON, mas removendo aspas e vírgulas desnecessárias.

---

## Benchmarks de Desempenho

O ZEON brilha em estruturas de dados uniformes e baseadas em listas. Rodamos nossa implementacão Python oficial contra 8 formatos de datasets reais e representativos.

**Resultados (Tokenizador: `cl100k_base` — GPT-4 / tiktoken):**

| Conjunto de Dados | Elegibilidade Tabular | JSON Compacto | YAML | **ZEON** | vs JSON | vs YAML |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| Registros de Funcionários (100, uniforme) | 100% | 2.804 | 3.702 | **1.709** | `-39,1%` | `-53,8%` |
| Repositórios GitHub (30, uniforme) | 100% | 2.083 | 2.461 | **1.188** | `-43,0%` | `-51,7%` |
| Série Temporal Analítica (60, uniforme) | 100% | 2.332 | 2.870 | **1.498** | `-35,8%` | `-47,8%` |
| Contatos com Endereço Aninhado (50) | 100% | 2.603 | 3.302 | **1.716** | `-34,1%` | `-48,0%` |
| Pedidos E-commerce (50, aninhado) | 33% | 4.933 | 6.220 | **3.581** | `-27,4%` | `-42,4%` |
| Feature Flags (40, mapa de chaves) | 100% | 825 | 963 | **487** | `-41,0%` | `-49,4%` |
| Logs de Evento Semi-uniformes (75) | 50% | 2.944 | 3.617 | **2.303** | `-21,8%` | `-36,3%` |
| Configuração Profundamente Aninhada | 0% | 137 | 173 | **105** | `-23,4%` | `-39,3%` |
| **TOTAL (todos 8 datasets)** | — | **18.661** | **23.308** | **12.587** | **`-32,5%`** | **`-46,0%`** |

> **Nota:** Para um comparativo detalhado e direto do ZEON contra o TOON e outros formatos orientados a IA, confira nosso arquivo [BENCHMARKS.md](BENCHMARKS.md).

*Em dados altamente uniformes e baseados em listas (elegibilidade tabular 100%), o ZEON alcança até **-43%** de redução de tokens contra JSON minificado, e mais de **-53%** contra YAML.*
*Mesmo em estruturas profundamente aninhadas ou semi-uniformes, o ZEON nunca consome **mais** tokens do que o YAML.*

Isso se traduz em um contexto efetivo significativamente maior para suas aplicações LLM, reduzindo diretamente os custos de inference de API.

---

## Quando NÃO usar o ZEON (E como contornar)

Embora o ZEON seja incrivelmente poderoso para reduzir os custos de inference de IA, ele é altamente sensível à indentação e formatação.

**1. Escrevendo Dados Manualmente**
Escrever ou editar arquivos diretamente em ZEON à mão pode ser difícil, pois errar um espaço ou nível de indentação pode alterar a forma como os dados são interpretados. 
**A Solução:** Você não precisa escrever em ZEON! Como o formato tem compatibilidade 100% bidirecional com JSON, você pode simplesmente escrever e manter seus dados no bom e velho JSON ou YAML, e usar nossa ferramenta CLI ou biblioteca Python para convertê-los para ZEON de forma invisível instantes antes de enviar ao LLM.

**2. Dados 100% Tabulares e Planos (Sem Aninhamento)**
Se os seus dados são completamente planos (como uma planilha clássica de Excel, sem nenhum objeto ou lista dentro das células), um formato CSV puro pode usar ligeiramente menos tokens. No entanto, o CSV quebra completamente assim que você tenta inserir um objeto aninhado nele, enquanto o ZEON absorve isso de forma nativa e limpa.

---

## Uso da CLI

O ZEON vem com uma ferramenta de Linha de Comando (CLI) bidirecional para converter seus conjuntos de dados entre ZEON, JSON e YAML sem esforço.

```bash
# Converter JSON ou YAML para ZEON
zeon convert data.json -> data.zeon
zeon convert config.yaml -> config.zeon

# Converter ZEON de volta para JSON ou YAML
zeon convert data.zeon -> data.json
zeon convert config.zeon -> config.yaml

# Imprimir diretamente no terminal
zeon convert config.yaml --print
```

---

## Instalação

O ZEON está oficialmente disponível no PyPI e pode ser instalado via `pip`:

```bash
pip install zeon-format
```

Para usá-lo em seu código Python:
```python
import zeon

# Decodificar texto ZEON para um Dicionário Python
data = zeon.loads(text)

# Codificar Dicionário Python para formato ZEON
zeon_text = zeon.dumps(data)

# Conversão direta de strings
json_text = zeon.convert(zeon_text).to_json()
yaml_text = zeon.convert(zeon_text).to_yaml()
zeon_text = zeon.convert(yaml_text).to_zeon()

# Conversão direta de arquivos
# 1. Passar apenas o nome do arquivo salvará automaticamente na mesma pasta do original
zeon.convert("pasta/secreta/dados.zeon").to_json("dados.json")
zeon.convert("pasta/secreta/dados.zeon").to_yaml("dados.yaml")

# 2. Ou passe um caminho completo para salvar em outro local específico
zeon.convert("pasta/secreta/dados.zeon").to_json("exports/meus_dados.json")
zeon.convert("pasta/secreta/dados.yaml").to_zeon("exports/meus_dados.zeon")
```

---
*ZEON - O futuro da serialização de dados para IA.*
