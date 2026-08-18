import React from 'react';
import { BarChart3, Info } from 'lucide-react';

export const BenchmarkTable = () => {
  return (
    <div className="benchmark-section" style={{ marginTop: '3rem' }}>
      <div className="panel-header" style={{ borderRadius: '12px 12px 0 0', background: 'rgba(30, 31, 38, 0.9)', display: 'flex', justifyContent: 'space-between' }}>
        <div className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart3 size={18} color="var(--text-highlight)" />
          Token Efficiency Benchmarks
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.5)' }}>
          <Info size={14} />
          Measured with <strong>tiktoken</strong> (cl100k_base)
        </div>
      </div>
      <div className="panel" style={{ borderRadius: '0 0 12px 12px', padding: '0', overflowX: 'auto' }}>
        <table className="bench-table">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Tabular Eligibility</th>
              <th>JSON (minified)</th>
              <th>YAML</th>
              <th style={{ color: 'var(--text-highlight)' }}>ZEON</th>
              <th>vs JSON</th>
              <th>vs YAML</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Employee Records (100)</td>
              <td>100%</td>
              <td>2,804</td>
              <td>3,702</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>1,709</td>
              <td style={{ color: 'var(--accent)' }}>-39.1%</td>
              <td style={{ color: 'var(--accent)' }}>-53.8%</td>
            </tr>
            <tr>
              <td>GitHub Repositories (30)</td>
              <td>100%</td>
              <td>2,083</td>
              <td>2,461</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>1,188</td>
              <td style={{ color: 'var(--accent)' }}>-43.0%</td>
              <td style={{ color: 'var(--accent)' }}>-51.7%</td>
            </tr>
            <tr>
              <td>Time Series Analytics (60)</td>
              <td>100%</td>
              <td>2,332</td>
              <td>2,870</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>1,498</td>
              <td style={{ color: 'var(--accent)' }}>-35.8%</td>
              <td style={{ color: 'var(--accent)' }}>-47.8%</td>
            </tr>
            <tr>
              <td>Contacts + Nested Address (50)</td>
              <td>100%</td>
              <td>2,603</td>
              <td>3,302</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>1,716</td>
              <td style={{ color: 'var(--accent)' }}>-34.1%</td>
              <td style={{ color: 'var(--accent)' }}>-48.0%</td>
            </tr>
            <tr>
              <td>E-commerce Orders (Nested)</td>
              <td>33%</td>
              <td>4,933</td>
              <td>6,220</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>3,581</td>
              <td style={{ color: 'var(--accent)' }}>-27.4%</td>
              <td style={{ color: 'var(--accent)' }}>-42.4%</td>
            </tr>
            <tr>
              <td>Feature Flags (Key-map)</td>
              <td>100%</td>
              <td>825</td>
              <td>963</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>487</td>
              <td style={{ color: 'var(--accent)' }}>-41.0%</td>
              <td style={{ color: 'var(--accent)' }}>-49.4%</td>
            </tr>
            <tr>
              <td>Semi-uniform Event Logs (75)</td>
              <td>50%</td>
              <td>2,944</td>
              <td>3,617</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>2,303</td>
              <td style={{ color: 'var(--accent)' }}>-21.8%</td>
              <td style={{ color: 'var(--accent)' }}>-36.3%</td>
            </tr>
            <tr>
              <td>Deeply Nested Config</td>
              <td>0%</td>
              <td>137</td>
              <td>173</td>
              <td style={{ color: 'var(--text-highlight)', fontWeight: 'bold' }}>105</td>
              <td style={{ color: 'var(--accent)' }}>-23.4%</td>
              <td style={{ color: 'var(--accent)' }}>-39.3%</td>
            </tr>
            <tr style={{ background: 'rgba(255,255,255,0.05)', fontWeight: 'bold' }}>
              <td>TOTAL (All 8 datasets)</td>
              <td>—</td>
              <td>18,661</td>
              <td>23,308</td>
              <td style={{ color: 'var(--text-highlight)' }}>12,587</td>
              <td style={{ color: 'var(--text-highlight)' }}>-32.5%</td>
              <td style={{ color: 'var(--text-highlight)' }}>-46.0%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
