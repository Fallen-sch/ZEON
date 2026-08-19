# zeon-parser

O parser oficial em JavaScript/TypeScript para a linguagem de configuração de dados [ZEON](https://github.com/lion-project/zeon).

O ZEON é um formato de dados altamente legível, baseado em indentação, que suporta agrupamentos em blocos, arrays e pares chave-valor nativos, sem a poluição visual do JSON ou YAML.

## Instalação

```bash
npm install zeon-format
```

## Como Usar

```typescript
import { parse } from 'zeon-format';

const zeonText = `
project_name="ZEON"
config
  timeout retries
  30 5
`;

// Fazer o parse de texto ZEON para Objeto JS
const result = parse(zeonText);
console.log(result.project_name); // ZEON

// Converter de um Objeto JS de volta para o formato ZEON
import { dumps } from 'zeon-format';
const zeonString = dumps(result);
console.log(result.config.timeout); // 30

// Ou utilize a API Converter para conversões Arquivo-para-JSON/YAML/ZEON
import { convert } from 'zeon-format';

// Ler arquivo ZEON e exportar
convert('data.zeon').toJson('data.json', 2); // 2 espaços de indentação
convert('data.zeon').toYaml('data.yaml');

// Ler arquivo JSON/YAML e exportar para ZEON
convert('data.yaml').toZeon('data.zeon');
```

## Recursos

- **Zero Dependências**: Parser feito em TypeScript puro.
- **Rápido**: Analisa textos em apenas alguns milissegundos.
- **100% de Paridade**: Espelha o exato comportamento do parser ZEON oficial feito em Python.
- **Focado em TypeScript**: Inclui definições internas `.d.ts`.

## Testes

Este projeto é testado contra casos extremos e situações atípicas usando o `Jest`.

```bash
npm install
npm run test
```

## Licença

MIT
