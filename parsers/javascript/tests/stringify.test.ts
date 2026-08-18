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
