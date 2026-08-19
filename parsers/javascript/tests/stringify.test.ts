import { describe, expect, test } from '@jest/globals';
import { dumps } from '../src/stringify';
import { convert } from '../src/converter';

describe('Stringifier API', () => {
    test('dumps basic flat dictionary', () => {
        const input = { project: "Test", version: 1 };
        const result = dumps(input);
        expect(result).toContain('project=Test');
        expect(result).toContain('version=1');
    });

    test('dumps nested dictionaries', () => {
        const input = {
            config: {
                timeout: 30,
                retries: 5
            }
        };
        const result = dumps(input);
        expect(result).toBe(`config
  timeout retries
  30 5`);
    });

    test('dumps root level array with [] marker', () => {
        const input = [
            { id: 1, name: "Alice" },
            { id: 2, name: "Bob" }
        ];
        const result = dumps(input);
        expect(result).toBe(`[]
  id name
  1 Alice
  2 Bob`);
    });

    test('Converter toZeon', () => {
        const jsonStr = '{"name":"ZEON","version":2}';
        const zeonResult = convert(jsonStr).toZeon();
        expect(zeonResult).toContain('name=ZEON');
    });

    test('Converter toYaml', () => {
        const zeonStr = 'name="ZEON"';
        const yamlResult = convert(zeonStr).toYaml();
        expect(yamlResult).toContain('name: ZEON');
    });
});
