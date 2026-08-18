# zeon-parser

O parser oficial em JavaScript/TypeScript para a linguagem de configuração de dados [ZEON](https://github.com/lion-project/zeon).

ZEON é um formato de dados altamente legível, baseado em indentação, que suporta agrupamento de blocos, arrays e propriedades nativas de chave-valor sem a poluição visual do JSON ou YAML.

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

// Fazer o parse do texto ZEON para Objeto JS
const result = parse(zeonText);
console.log(result.project_name); // ZEON

// Converter Objeto JS de volta para formato ZEON
import { dumps } from 'zeon-format';
const zeonString = dumps(result);
console.log(result.config.timeout); // 30

// Ou usar a API Converter de Arquivos (JSON/YAML/ZEON)
import { convert } from 'zeon-format';

// Ler ZEON e exportar
convert('data.zeon').toJson('data.json', 2); // 2 espaços
convert('data.zeon').toYaml('data.yaml');

// Ler JSON/YAML e exportar para ZEON
convert('data.yaml').toZeon('data.zeon');
```

## Recursos

- **Zero Dependências**: Parser escrito em TypeScript puro.
- **Rápido**: Analisa textos complexos em apenas alguns milissegundos.
- **100% de Paridade**: Espelha o comportamento exato do parser oficial em Python do ZEON.
- **Feito em TypeScript**: Já inclui definições de tipos internas (`.d.ts`).

## Testes Automatizados

Este projeto é testado contra casos extremos (edge cases) rigorosos de parsing de dados utilizando o \`Jest\`.

```bash
npm install
npm run test
```

## Licença

MIT
