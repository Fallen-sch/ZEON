import React, { useState, useEffect } from 'react';
import { parse as parseZeon } from '../../parsers/javascript/src/parse';
import { dumps as stringifyZeon } from '../../parsers/javascript/src/stringify';
import { parse as parseYaml, stringify as stringifyYaml } from 'yaml';
import { Zap, AlertTriangle, Download, Database, Settings, ArrowRightLeft, Copy, Check } from 'lucide-react';
import { BenchmarkTable } from './Benchmark';

type Format = 'ZEON' | 'JSON' | 'YAML';

const INITIAL_JSON = `{
  "products": [
    {
      "id": 1,
      "name": "Laptop",
      "specs": {
        "weight": 1.5,
        "color": "silver"
      }
    },
    {
      "id": 2,
      "name": "Mouse",
      "specs": {
        "extra_buttons": true,
        "weight": 0.2,
        "color": "black"
      }
    }
  ]
}`;

function App() {
  const [inputText, setInputText] = useState(INITIAL_JSON);
  const [outputText, setOutputText] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const [inputFormat, setInputFormat] = useState<Format>('JSON');
  const [outputFormat, setOutputFormat] = useState<Format>('ZEON');
  const [copied, setCopied] = useState(false);
  
  // Real-time conversion
  useEffect(() => {
    convert();
  }, [inputText, inputFormat, outputFormat]);

  const convert = () => {
    if (!inputText.trim()) {
      setOutputText('');
      setError(null);
      return;
    }
    
    try {
      setError(null);
      
      // 1. Parse Input to JS Object
      let jsObject: any;
      if (inputFormat === 'ZEON') {
        jsObject = parseZeon(inputText);
      } else if (inputFormat === 'JSON') {
        jsObject = JSON.parse(inputText);
      } else if (inputFormat === 'YAML') {
        jsObject = parseYaml(inputText);
      }
      
      // 2. Stringify JS Object to Output Format
      if (outputFormat === 'ZEON') {
        setOutputText(stringifyZeon(jsObject));
      } else if (outputFormat === 'JSON') {
        setOutputText(JSON.stringify(jsObject, null, 2));
      } else if (outputFormat === 'YAML') {
        setOutputText(stringifyYaml(jsObject));
      }
      
    } catch (err: any) {
      setError(err.message || 'Syntax Error');
    }
  };

  const handleCopy = () => {
    if (outputText) {
      navigator.clipboard.writeText(outputText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const loadExample = (type: 'tuples' | 'keyed' | 'mixed' | 'nested_mixed' | 'matrices') => {
    setInputFormat('JSON');
    setOutputFormat('ZEON');
    if (type === 'tuples') {
      setInputText(JSON.stringify({
        items: [
          { id: 1, name: "sword", stats: { atk: 10, def: 5 } },
          { id: 2, name: "shield", stats: { atk: 0, def: 15 } }
        ]
      }, null, 2));
    } else if (type === 'keyed') {
      setInputText(JSON.stringify({
        servers: {
          "prod-1": { region: "us-east", active: true },
          "prod-2": { region: "eu-west", active: false }
        }
      }, null, 2));
    } else if (type === 'mixed') {
      setInputText(JSON.stringify({
        logs: [
          { time: "10:00", level: "INFO", msg: "Started", user_id: 42 },
          { time: "10:05", level: "ERR", msg: "Fail", trace: "x", code: 500 }
        ]
      }, null, 2));
    } else if (type === 'nested_mixed') {
      setInputText(JSON.stringify({
        products: [
          { id: 1, name: "Laptop", specs: { weight: 1.5, color: "silver" } },
          { id: 2, name: "Mouse", specs: { extra_buttons: true, weight: 0.2, color: "black" } }
        ]
      }, null, 2));
    } else if (type === 'matrices') {
      setInputText(JSON.stringify({
        matrix2D: [
          [1, 0],
          [0, 1]
        ],
        matrix3D: [
          [
            [1, 1],
            [1, 1]
          ],
          [
            [0, 0],
            [0, 0]
          ]
        ],
        keyed: {
          x: [1, 2, 3],
          y: [4, 5, 6]
        }
      }, null, 2));
    }
  };

  const calculateSavings = () => {
    if (error || !outputText || !inputText) return null;
    const outLen = outputText.length;
    const inLen = inputText.length;
    
    // We only calculate savings if outputting TO ZEON from something else, 
    // OR from ZEON to something else.
    if (inputFormat === 'ZEON' && outputFormat !== 'ZEON') {
      const saved = ((outLen - inLen) / outLen) * 100;
      return saved > 0 ? `ZEON is ${saved.toFixed(1)}% smaller than ${outputFormat}` : null;
    } else if (outputFormat === 'ZEON' && inputFormat !== 'ZEON') {
      const saved = ((inLen - outLen) / inLen) * 100;
      return saved > 0 ? `ZEON is ${saved.toFixed(1)}% smaller than ${inputFormat}` : null;
    }
    return null;
  };

  const savingsText = calculateSavings();

  return (
    <div className="playground-container">
      <header className="header">
        <div className="logo">
          <Zap size={24} color="var(--text-highlight)" />
          ZEON <span>Universal Converter</span>
        </div>
        <div className="controls">
          <button className="btn" onClick={() => loadExample('tuples')}>Nested Tuples</button>
          <button className="btn" onClick={() => loadExample('keyed')}>Keyed Tabular</button>
          <button className="btn" onClick={() => loadExample('mixed')}>Mixed Kwargs</button>
          <button className="btn" onClick={() => loadExample('nested_mixed')}>Nested Mixed</button>
          <button className="btn" onClick={() => loadExample('matrices')}>Matrices</button>
        </div>
      </header>

      <main className="main-content">
        {/* Left Panel: Input */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Input: 
              <select 
                className="format-select" 
                value={inputFormat} 
                onChange={(e) => setInputFormat(e.target.value as Format)}
              >
                <option value="ZEON">ZEON</option>
                <option value="JSON">JSON</option>
                <option value="YAML">YAML</option>
              </select>
            </div>
            <div className="stats">{inputText.length} chars</div>
          </div>
          <textarea
            className="editor-area"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            spellCheck="false"
            placeholder={`Paste ${inputFormat} here...`}
          />
        </div>

        {/* Right Panel: Output */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Output:
              <select 
                className="format-select" 
                value={outputFormat} 
                onChange={(e) => setOutputFormat(e.target.value as Format)}
              >
                <option value="ZEON">ZEON</option>
                <option value="JSON">JSON</option>
                <option value="YAML">YAML</option>
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {savingsText && (
                <div className="stats" style={{ color: '#66fcf1' }}>
                  {savingsText}
                </div>
              )}
              <button className="btn" onClick={handleCopy} title="Copy Output" style={{ padding: '4px 8px' }}>
                {copied ? <Check size={16} color="var(--text-highlight)" /> : <Copy size={16} />}
              </button>
            </div>
          </div>
          <textarea
            className="editor-area"
            value={outputText}
            readOnly
            spellCheck="false"
            style={{ color: error ? 'var(--text-main)' : 'var(--text-highlight)' }}
          />
          {error && (
            <div className="error-banner">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}
        </div>
      </main>

      <BenchmarkTable />
    </div>
  );
}

export default App;
