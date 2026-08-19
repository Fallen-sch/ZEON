export function getPreviewHtml(text: string, showTip: boolean = true): string {

  function splitZeonLine(line: string): string[] {
    const tokens: string[] = [];
    let current = '';
    let inQuotes = false;
    let stack: string[] = [];
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"' && (i === 0 || line[i-1] !== '\\')) {
            inQuotes = !inQuotes;
            current += char;
        } else if (inQuotes) {
            current += char;
        } else {
            if (char === '(' || char === '[' || char === '{') {
                stack.push(char);
                current += char;
            } else if (char === ')' && stack.length > 0 && stack[stack.length - 1] === '(') {
                stack.pop();
                current += char;
            } else if (char === ']' && stack.length > 0 && stack[stack.length - 1] === '[') {
                stack.pop();
                current += char;
            } else if (char === '}' && stack.length > 0 && stack[stack.length - 1] === '{') {
                stack.pop();
                current += char;
            } else if (char.trim() === '' && stack.length === 0) {
                if (current.length > 0) {
                    tokens.push(current);
                    current = '';
                }
            } else {
                current += char;
            }
        }
    }
    if (current.length > 0) {
        tokens.push(current);
    }
    return tokens;
  }

  function highlightLine(raw: string): string {
    // Single-pass tokenizer to avoid regex self-contamination
    const tokens: string[] = [];
    let i = 0;
    while (i < raw.length) {
      // Quoted string
      if (raw[i] === '"') {
        let j = i + 1;
        while (j < raw.length && raw[j] !== '"') { if (raw[j] === '\\') j++; j++; }
        const str = raw.slice(i, j + 1);
        tokens.push(`<span class="string">${str}</span>`);
        i = j + 1;
        continue;
      }
      // Check for '(' preceded by space to break nested dicts nicely
      if (raw[i] === '(' && i > 0 && raw[i-1] === ' ') {
          tokens.push(`<br>(`);
          i++;
          continue;
      }
      
      // key= pattern: collect identifier then check for '='
      const keyMatch = raw.slice(i).match(/^([a-zA-Z0-9_\-]+)=/);
      if (keyMatch) {
        // If preceded by a space, add a line break for readability
        if (i > 0 && raw[i-1] === ' ') {
            tokens.push(`<br><span class="key">${keyMatch[1]}</span>=`);
        } else {
            tokens.push(`<span class="key">${keyMatch[1]}</span>=`);
        }
        i += keyMatch[1].length + 1;
        continue;
      }
      // keyword: True / False / None (must be whole word)
      const kwMatch = raw.slice(i).match(/^(True|False|None)(?=[\s,)\]"\\]|$)/);
      if (kwMatch) {
        tokens.push(`<span class="keyword">${kwMatch[1]}</span>`);
        i += kwMatch[1].length;
        continue;
      }
      // Regular character
      tokens.push(raw[i]);
      i++;
    }
    return tokens.join('');
  }

  let htmlBody = showTip ? `
    <div class="tip-banner" id="tipBanner">
      <div style="flex-grow: 1;">💡 <strong>Tip:</strong> You can click any data cell to edit its value directly. Press <strong>Ctrl+S</strong> to save. Use <strong>#</strong> on empty lines to separate tables visually.</div>
      <div class="close-btn" onclick="closeTip()" title="Dismiss">✖</div>
    </div>
  ` : '';
  const lines = text.split('\n');

  let inTabularBlock = false;
  let indentLevel = 0;
  let columnsCount = 0;
  let inGrid = false;
  let isMatrix2d = false;
  let isDictOfArrays = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].replace(/\r$/, '');
    if (line.trim() === '') {
      if (inGrid) { htmlBody += `</div>`; inGrid = false; }
      htmlBody += `<div class="empty"></div>`;
      continue;
    }

    const currentIndent = line.search(/\S/);
    
    // Close the current tabular block if indentation drops back to root
    if (inTabularBlock && currentIndent <= indentLevel) {
      inTabularBlock = false;
      isMatrix2d = false;
      isDictOfArrays = false;
      if (inGrid) { htmlBody += `</div>`; inGrid = false; }
      htmlBody += `</div></div>`; // close block-content and tabular-block
    }

    // Skip comment lines AFTER handling block closure
    if (line.trim().startsWith('#')) {
      continue;
    }

    const headerMatch = line.match(/^(\s*)([a-zA-Z0-9_\-]+)(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))?$/);
    
    let formattedLine = highlightLine(line);

    if (headerMatch && (currentIndent === 0 || !inTabularBlock)) {
      isMatrix2d = ['[][]', '[2]', '[3]'].includes(headerMatch[3]);
      isDictOfArrays = headerMatch[3] === '{[]}';
      inTabularBlock = true;
      indentLevel = headerMatch[1].length;
      columnsCount = 0;
      inGrid = false; // always reset grid on new block header
      if (inGrid) { htmlBody += `</div>`; }
      htmlBody += `<div class="tabular-block">`;
      const suffixDisplay = headerMatch[3] || '';
      htmlBody += `<div class="header">
        <button class="toggle-btn" onclick="toggleBlock(this)" title="Collapse/Expand Block">▼</button>
        <strong contenteditable="true" data-type="blockKey" data-line="${i}">${headerMatch[2]}</strong><span class="suffix">${suffixDisplay}</span>
      </div>`;
      
      let blockContentClass = 'block-content';
      if (suffixDisplay === '[3]') {
          blockContentClass += ' matrix-3d-row';
      }
      htmlBody += `<div class="${blockContentClass}">`;
    } else if (inTabularBlock && currentIndent > indentLevel) {
        // For 2D matrix ([][]), treat every row as raw data (no column header row)
        if (isMatrix2d) {
          const vals = line.trim().split(/\s+/).filter(v => v.length > 0);
          if (!inGrid) {
            columnsCount = vals.length;
            inGrid = true;
            htmlBody += `<div class="grid-container matrix-grid" style="margin-left: ${currentIndent * 8}px; grid-template-columns: repeat(${columnsCount}, max-content);">`;  
          }
          for (let ci = 0; ci < vals.length; ci++) {
            htmlBody += `<div class="grid-cell" contenteditable="true" data-line="${i}" data-idx="${ci}">${highlightLine(vals[ci])}</div>`;
          }
          continue;
        }
        
        if (isDictOfArrays) {
          const vals = splitZeonLine(line.trim());
          if (!inGrid) {
            columnsCount = vals.length;
            inGrid = true;
            htmlBody += `<div class="grid-container" style="margin-left: ${currentIndent * 8}px; grid-template-columns: repeat(${columnsCount}, max-content);">`;  
          }
          let colIdx = 0;
          for (let c of vals) {
             let content = highlightLine(c);
             let extraClass = '';
             if (colIdx === 0) {
                 content = `<strong>${content}</strong>`;
                 extraClass = ' dict-array-key';
             }
             htmlBody += `<div class="grid-cell${extraClass}" contenteditable="true" data-line="${i}" data-idx="${colIdx}">${content}</div>`;
             colIdx++;
          }
          continue;
        }

        if (columnsCount === 0 && !line.includes('=')) {
          const cols = splitZeonLine(line.trim());
          columnsCount = cols.length;
          
          if (inGrid) { htmlBody += `</div>`; }
          inGrid = true;
          htmlBody += `<div class="grid-container" style="margin-left: ${currentIndent * 8}px; grid-template-columns: repeat(${columnsCount}, max-content) auto;">`;
          
          let colIdx = 0;
          for (let c of cols) {
             htmlBody += `<div class="grid-header" contenteditable="true" data-type="colKey" data-line="${i}" data-idx="${colIdx}">${c}</div>`;
             colIdx++;
          }
          htmlBody += `<div></div>`;
        } else {
          if (!inGrid) {
             htmlBody += `<div class="row" style="margin-left: ${currentIndent * 8}px">${formattedLine.trim()}</div>`;
          } else {
             const tokens = splitZeonLine(line.trim());
             let valIdx = 0;
             let inlineContent = '';
             let rowHtml = '';

             for (let token of tokens) {
                // Only treat as inline-attr if the token itself IS a key=value assignment
                // e.g. "user=admin" or "flag=True" — NOT complex values that contain '=' inside like (passiva=...)
                if (/^[a-zA-Z0-9_\-]+=/.test(token)) {
                    inlineContent += ' ' + token;
                    continue;
                }
                
                let valStr = highlightLine(token);
                
                if (valIdx < columnsCount) {
                   let rowHtmlInner = `<div class="grid-cell collapsed" contenteditable="true" data-line="${i}" data-idx="${valIdx}">${valStr}</div>`;
                   rowHtml += `<div class="cell-wrapper">${rowHtmlInner}<button class="expand-btn hidden" onclick="toggleText(this)" title="Show more/less">➕</button></div>`;
                } else {
                   inlineContent += ' ' + valStr;
                }
                valIdx++;
             }

             while (valIdx < columnsCount) {
                 rowHtml += `<div class="grid-cell"></div>`;
                 valIdx++;
             }
             
             if (inlineContent.trim().length > 0) {
                 inlineContent = highlightLine(inlineContent);
             }

             htmlBody += rowHtml + `<div class="grid-cell inline-attr">${inlineContent.trim()}</div>`;
          }
        }
    } else {
      if (inGrid) { htmlBody += `</div>`; inGrid = false; }
      htmlBody += `<div class="row" style="margin-left: ${currentIndent * 8}px">${formattedLine.trim()}</div>`;
    }
  }

  if (inGrid) { htmlBody += `</div>`; }
  if (inTabularBlock) { htmlBody += `</div></div>`; }

  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>ZEON Preview</title>
      <style>
        body {
          font-family: var(--vscode-editor-font-family, Consolas, monospace);
          color: var(--vscode-editor-foreground);
          background-color: var(--vscode-editor-background);
          padding: 20px;
          line-height: 1.5;
        }
        .tabular-block {
          border-left: 3px solid var(--vscode-focusBorder);
          background-color: rgba(128, 128, 128, 0.05);
          padding: 8px;
          margin: 10px 0;
          border-radius: 4px;
        }
        .tip-banner {
          background-color: var(--vscode-textBlockQuote-background);
          border-left: 4px solid var(--vscode-textBlockQuote-border);
          padding: 10px 15px;
          margin-bottom: 20px;
          border-radius: 4px;
          font-family: var(--vscode-font-family, system-ui, sans-serif);
          font-size: 0.9em;
          color: var(--vscode-descriptionForeground);
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .tip-banner strong {
          color: var(--vscode-editor-foreground);
        }
        .close-btn {
          cursor: pointer;
          color: var(--vscode-icon-foreground);
          padding: 4px;
          font-size: 1.1em;
        }
        .close-btn:hover {
          color: var(--vscode-editor-foreground);
        }
        .header {
          font-size: 1.1em;
          color: var(--vscode-symbolIcon-classForeground);
          margin-bottom: 5px;
          display: flex;
          align-items: center;
        }
        .toggle-btn {
          background: none; border: none; color: var(--vscode-icon-foreground); 
          cursor: pointer; padding: 0 6px 0 0; font-size: 12px;
        }
        .toggle-btn:hover { color: var(--vscode-editor-foreground); }
        .block-content { display: block; }
        .block-content.hidden { display: none; }
        .matrix-3d-row {
          display: flex;
          flex-direction: row;
          flex-wrap: wrap;
          gap: 15px;
          align-items: flex-start;
        }
        .matrix-3d-row > .empty {
          display: none;
        }
        .suffix {
          color: var(--vscode-descriptionForeground);
          margin-left: 4px;
        }
        .grid-container {
          display: grid;
          column-gap: 25px;
          row-gap: 4px;
          margin-top: 5px;
          width: max-content;
        }
        .matrix-grid {
          border-left: 2px solid var(--vscode-editorLineNumber-foreground);
          border-right: 2px solid var(--vscode-editorLineNumber-foreground);
          padding: 4px 12px;
          border-radius: 3px;
        }
        .dict-array-key {
          border-right: 1px dashed var(--vscode-editorLineNumber-foreground);
          padding-right: 8px;
        }
        .grid-header {
          color: var(--vscode-symbolIcon-propertyForeground);
          font-weight: bold;
          border-bottom: 1px dashed var(--vscode-editorLineNumber-foreground);
          padding-bottom: 4px;
        }
        .grid-container > div:not(.grid-header) {
          border-bottom: 1px dotted var(--vscode-editorLineNumber-activeForeground, rgba(128, 128, 128, 0.3));
          padding-bottom: 4px;
          padding-top: 4px;
        }
        .cell-wrapper {
          display: flex;
          align-items: flex-start;
          max-width: 500px;
        }
        .grid-cell {
          font-family: var(--vscode-editor-font-family, Consolas, monospace);
          color: var(--vscode-editor-foreground);
          max-width: 320px;
          word-wrap: break-word;
          overflow-wrap: break-word;
          white-space: pre-wrap;
        }
        .grid-cell.long-text {
          max-width: 450px;
        }
        .grid-cell.collapsed {
          max-height: 3.2em; /* ~2 lines */
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }
        .expand-btn {
          background: none; border: none; color: var(--vscode-textLink-foreground); cursor: pointer;
          padding: 0 4px; font-size: 12px; flex-shrink: 0; margin-left: 4px; margin-top: 2px;
        }
        .expand-btn.hidden { display: none; }
        .expand-btn:hover { text-decoration: underline; color: var(--vscode-textLink-activeForeground); }
        .grid-cell[contenteditable="true"]:focus {
          outline: 1px solid var(--vscode-focusBorder);
          background-color: var(--vscode-editor-selectionBackground);
        }
        .inline-attr {
          margin-left: 10px;
          max-width: 400px;
          word-wrap: break-word;
          overflow-wrap: break-word;
          white-space: pre-wrap;
        }
        .row { margin-bottom: 2px; }
        .key { color: var(--vscode-symbolIcon-propertyForeground); font-weight: bold; }
        .keyword { color: var(--vscode-symbolIcon-keywordForeground); }
        .string { color: var(--vscode-symbolIcon-stringForeground); }
        .comment { color: var(--vscode-editorLineNumber-foreground); font-style: italic; }
      </style>
    </head>
    <body>
      ${htmlBody}
      <script>
        const vscode = acquireVsCodeApi();
        document.querySelectorAll('[contenteditable="true"]').forEach(cell => {
           // We store the initial raw text. If it's a styled span, innerText extracts just the text nicely.
           cell.addEventListener('focus', (e) => {
              e.target.dataset.initial = e.target.innerText.trim();
           });
           
           cell.addEventListener('blur', (e) => {
              const el = e.target;
              const newValue = el.innerText.trim();
              if (newValue === el.dataset.initial) {
                  return;
              }
              
              const type = el.getAttribute('data-type') || 'val';
              const line = parseInt(el.getAttribute('data-line'), 10);
              const idx = el.hasAttribute('data-idx') ? parseInt(el.getAttribute('data-idx'), 10) : 0;
              
              vscode.postMessage({
                 command: 'edit',
                 type: type,
                 line: line,
                 idx: idx,
                 newValue: newValue
              });
           });
           
           // Prevent newlines
           cell.addEventListener('keydown', (e) => {
              if (e.key === 'Enter') {
                 e.preventDefault();
                 cell.blur();
              }
           });
        });

         // Add Ctrl+S support in preview
         window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
               e.preventDefault();
               
               let isEditing = false;
               if (document.activeElement && document.activeElement.hasAttribute('contenteditable')) {
                   const el = document.activeElement;
                   const newValue = el.innerText.trim();
                   
                   if (newValue !== el.dataset.initial) {
                       const type = el.getAttribute('data-type') || 'val';
                       const line = parseInt(el.getAttribute('data-line'), 10);
                       const idx = el.hasAttribute('data-idx') ? parseInt(el.getAttribute('data-idx'), 10) : 0;
                       
                       vscode.postMessage({
                          command: 'edit',
                          type: type,
                          line: line,
                          idx: idx,
                          newValue: newValue,
                          saveAfter: true // Flag to tell extension to save immediately after edit
                       });
                       isEditing = true;
                   }
                   
                   // Update initial so blur doesn't send duplicate message
                   el.dataset.initial = newValue;
                   el.blur();
               }
               
               if (!isEditing) {
                   vscode.postMessage({ command: 'save' });
               }
            }
         });

        // Determine if cells actually overflow past 2 lines and show/hide buttons
        requestAnimationFrame(() => {
           document.querySelectorAll('.grid-cell.collapsed').forEach(cell => {
              // If scrollHeight > clientHeight (plus a tiny tolerance), it's clamped
              if (cell.scrollHeight > cell.clientHeight + 2) {
                 const btn = cell.nextElementSibling;
                 if (btn && btn.classList.contains('expand-btn')) {
                    btn.classList.remove('hidden');
                 }
              } else {
                 cell.classList.remove('collapsed');
              }
           });
        });

        function closeTip() {
           const banner = document.getElementById('tipBanner');
           if (banner) {
              banner.style.display = 'none';
           }
           vscode.postMessage({ command: 'closeTip' });
        }

        function toggleBlock(btn) {
           const content = btn.parentElement.nextElementSibling;
           if (content.classList.contains('hidden')) {
              content.classList.remove('hidden');
              btn.innerText = '▼';
           } else {
              content.classList.add('hidden');
              btn.innerText = '▶';
           }
        }

        function toggleText(btn) {
           const cell = btn.previousElementSibling;
           if (cell.classList.contains('collapsed')) {
              cell.classList.remove('collapsed');
              btn.innerText = '➖';
           } else {
              cell.classList.add('collapsed');
              btn.innerText = '➕';
           }
        }
      </script>
    </body>
    </html>
  `;
}
