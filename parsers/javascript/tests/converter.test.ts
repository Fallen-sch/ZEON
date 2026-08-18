import { convert } from '../src/converter';
import * as fs from 'fs';
import * as path from 'path';

describe('Converter API', () => {
    const testFilePath = path.join(__dirname, 'test_data.zeon');
    const outFilePath = path.join(__dirname, 'test_output.json');

    beforeAll(() => {
        const input = `
project="Test"
version=1
config(
  timeout=30
)
`;
        fs.writeFileSync(testFilePath, input, 'utf-8');
    });

    afterAll(() => {
        if (fs.existsSync(testFilePath)) fs.unlinkSync(testFilePath);
        if (fs.existsSync(outFilePath)) fs.unlinkSync(outFilePath);
    });

    test('converts direct string to json string', () => {
        const input = `name="ZEON"`;
        const result = convert(input).toJson();
        expect(result).toBe('{"name":"ZEON"}');
    });

    test('reads from file and converts to json string', () => {
        const result = convert(testFilePath).toJson();
        expect(result).toBe('{"project":"Test","version":1,"config":{"timeout":30}}');
    });

    test('reads from file and writes output to file automatically', () => {
        convert(testFilePath).toJson('test_output.json');
        
        // It should save it to the same directory as the testFilePath
        expect(fs.existsSync(outFilePath)).toBe(true);
        const savedData = fs.readFileSync(outFilePath, 'utf-8');
        expect(savedData).toBe('{"project":"Test","version":1,"config":{"timeout":30}}');
    });
});
