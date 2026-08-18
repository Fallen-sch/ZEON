# zeon-parser

The official JavaScript/TypeScript parser for the [ZEON](https://github.com/lion-project/zeon) data configuration language.

ZEON is a highly readable, indentation-based data format that supports block groupings, arrays, and native key-value pairs without the syntax clutter of JSON or YAML.

## Installation

```bash
npm install zeon-format
```

## Usage

```typescript
import { parse } from 'zeon-format';

const zeonText = `
project_name="ZEON"
config
  timeout retries
  30 5
`;

// Parse ZEON text to JS Object
const result = parse(zeonText);
console.log(result.project_name); // ZEON

// Convert JS Object back to ZEON format
import { dumps } from 'zeon-format';
const zeonString = dumps(result);
console.log(result.config.timeout); // 30

// Or use the Converter API for File-to-JSON/YAML/ZEON
import { convert } from 'zeon-format';

// Read ZEON and export
convert('data.zeon').toJson('data.json', 2); // 2 spaces indent
convert('data.zeon').toYaml('data.yaml');

// Read JSON/YAML and export to ZEON
convert('data.yaml').toZeon('data.zeon');
```

## Features

- **Zero Dependencies**: Pure TypeScript parser.
- **Fast**: Analyzes text in just a few milliseconds.
- **100% Parity**: Mirrors the exact behavior of the official Python ZEON parser.
- **TypeScript First**: Ships with internal `.d.ts` definitions.

## Testing

This project is tested against extreme parsing edge cases using `Jest`.

```bash
npm install
npm run test
```

## License

MIT
