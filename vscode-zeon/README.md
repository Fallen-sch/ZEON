# ZEON Language Support

Official VSCode extension for the [ZEON](https://github.com/Fallen-sch/ZEON) data configuration language.

ZEON is a highly readable, indentation-based data format that supports block groupings, arrays, and native key-value pairs without the syntax clutter of JSON or YAML. Designed specifically for AI and LLM token efficiency.

## Features

- **Syntax Highlighting**: Beautiful colorization for ZEON primitives, blocks, strings, keywords, and matrix syntaxes (`[]`, `[][]`, `[2]`, `[3]`, `{}`).
- **Real-time Diagnostics (Linter)**: Catch formatting errors and invalid suffixes instantly.
- **Interactive Live Preview**: Open a side-by-side visual preview of your ZEON data!
  - Click the preview icon in the top right corner of any `.zeon` file.
  - View data in clean grid/tabular layouts.
  - Dynamically collapse/expand large tables and long text strings.
  - Edit cell values directly in the preview and press `Ctrl+S` to instantly reflect changes in your `.zeon` file.

## Usage

1. Create a `.zeon` file (e.g. `data.zeon`).
2. Write your data using ZEON's indentation rules.
3. Click the "Preview" button in the editor title bar to open the visual grid.

## License

MIT
