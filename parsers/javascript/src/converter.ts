import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { parse } from './parse';
import { dumps } from './stringify';

export class Converter {
    private isFile: boolean = false;
    private filePath: string | null = null;
    private content: string;

    constructor(dataOrPath: string) {
        if (dataOrPath.length < 1000 && fs.existsSync(dataOrPath)) {
            this.isFile = true;
            this.filePath = path.resolve(dataOrPath);
            this.content = fs.readFileSync(this.filePath, 'utf-8');
        } else {
            this.content = dataOrPath;
        }
    }

    private _saveIfRequested(outPath: string | undefined, result: string) {
        if (outPath) {
            let finalPath = outPath;
            if (this.isFile && this.filePath && !path.dirname(outPath).includes(path.sep)) {
                const originalDir = path.dirname(this.filePath);
                finalPath = path.join(originalDir, outPath);
            }
            fs.writeFileSync(finalPath, result, 'utf-8');
        }
    }

    toJson(outPath?: string, space: number = 0): string {
        const parsedData = this._loadData();
        const result = JSON.stringify(parsedData, null, space);
        this._saveIfRequested(outPath, result);
        return result;
    }

    toYaml(outPath?: string): string {
        const parsedData = this._loadData();
        const result = yaml.dump(parsedData, { indent: 2, lineWidth: -1 });
        this._saveIfRequested(outPath, result);
        return result;
    }

    toZeon(outPath?: string): string {
        const parsedData = this._loadData();
        const result = dumps(parsedData);
        this._saveIfRequested(outPath, result);
        return result;
    }

    private _loadData(): any {
        // Se a entrada for um arquivo JSON ou YAML
        if (this.isFile && this.filePath) {
            if (this.filePath.endsWith('.json')) {
                return JSON.parse(this.content);
            } else if (this.filePath.endsWith('.yaml') || this.filePath.endsWith('.yml')) {
                return yaml.load(this.content);
            }
        }
        
        // Se for uma string pura de JSON
        const trimmed = this.content.trim();
        if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || 
            (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
            try {
                return JSON.parse(trimmed);
            } catch (e) {
                // fall back to ZEON if JSON parsing fails
            }
        }

        // Caso contrário, é ZEON
        return parse(this.content);
    }
}

export function convert(dataOrPath: string): Converter {
    return new Converter(dataOrPath);
}
