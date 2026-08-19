import * as vscode from 'vscode';
import { getPreviewHtml } from './preview';
import { parse } from 'zeon-format';

const tokenTypes = ['class', 'function', 'variable', 'string', 'number', 'enumMember', 'typeParameter', 'keyword'];
const tokenModifiers = ['declaration'];
const legend = new vscode.SemanticTokensLegend(tokenTypes, tokenModifiers);

const semanticProvider: vscode.DocumentSemanticTokensProvider = {
  provideDocumentSemanticTokens(document: vscode.TextDocument): vscode.ProviderResult<vscode.SemanticTokens> {
    const tokensBuilder = new vscode.SemanticTokensBuilder(legend);
    const text = document.getText();
    const lines = text.split('\n');
    
    let inTabularBlock = false;
    let blockIndent = 0;
    let columnTokens: number[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.trim() === '' || line.trim().startsWith('#')) continue;

      const indentMatch = line.match(/^\s*/);
      const currentIndent = indentMatch ? indentMatch[0].length : 0;

      // Check if we left the block
      if (inTabularBlock && currentIndent <= blockIndent && line.trim().length > 0) {
        inTabularBlock = false;
        columnTokens = [];
      }

      // Check for Header (e.g. `teste[]`)
      const headerMatch = line.match(/^(\s*)([a-zA-Z0-9_\-]+)(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))/);
      if (headerMatch) {
        inTabularBlock = true;
        blockIndent = headerMatch[1].length;
        columnTokens = [];
        continue;
      }

      // If we are in a block, and we haven't seen columns yet, this must be the columns line
      if (inTabularBlock && currentIndent > blockIndent && columnTokens.length === 0 && !line.includes('=')) {
        let match;
        // Regex to find words
        const colRegex = /[^\s()\[\]={}]+/g;
        let colIdx = 0;
        while ((match = colRegex.exec(line)) !== null) {
          const typeIdx = colIdx % tokenTypes.length;
          columnTokens.push(typeIdx);
          tokensBuilder.push(
            new vscode.Range(new vscode.Position(i, match.index), new vscode.Position(i, match.index + match[0].length)),
            tokenTypes[typeIdx],
            []
          );
          colIdx++;
        }
        continue;
      }

      // If we are in a block and have columns, these are data rows!
      if (inTabularBlock && columnTokens.length > 0 && currentIndent > blockIndent) {
        let match;
        // Basic lexer regex to find contiguous values
        const valRegex = /"(?:[^"\\]|\\.)*"|\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|[^\s()\[\]={}]+/g;
        let valIdx = 0;
        while ((match = valRegex.exec(line)) !== null) {
          // If this is an inline attribution (e.g. key=value), don't color it as a tabular column
          if (match[0].includes('=')) continue;
          
          if (valIdx < columnTokens.length) {
            tokensBuilder.push(
              new vscode.Range(new vscode.Position(i, match.index), new vscode.Position(i, match.index + match[0].length)),
              tokenTypes[columnTokens[valIdx]],
              []
            );
          }
          valIdx++;
        }
        continue;
      }
    }

    return tokensBuilder.build();
  }
};

const hoverProvider: vscode.HoverProvider = {
  provideHover(document: vscode.TextDocument, position: vscode.Position): vscode.ProviderResult<vscode.Hover> {
    const line = document.lineAt(position.line).text;
    if (line.trim() === '' || line.trim().startsWith('#')) return null;

    const currentIndentMatch = line.match(/^\s*/);
    const currentIndent = currentIndentMatch ? currentIndentMatch[0].length : 0;

    let blockIndent = -1;
    let columnsLine = '';
    
    // Scan upwards to find the tabular header definition
    for (let i = position.line - 1; i >= 0; i--) {
      const prevLine = document.lineAt(i).text;
      if (prevLine.trim() === '' || prevLine.trim().startsWith('#')) continue;
      
      const prevIndentMatch = prevLine.match(/^\s*/);
      const prevIndent = prevIndentMatch ? prevIndentMatch[0].length : 0;
      
      const headerMatch = prevLine.match(/^(\s*)([a-zA-Z0-9_\-]+)(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))/);
      if (headerMatch) {
         if (currentIndent > prevIndent) {
             blockIndent = prevIndent;
             // The columns line is the first non-empty line after the header
             for (let j = i + 1; j <= position.line; j++) {
                const headerNextLine = document.lineAt(j).text;
                if (headerNextLine.trim() === '' || headerNextLine.trim().startsWith('#')) continue;
                if (headerNextLine.includes('=')) continue;
                columnsLine = headerNextLine;
                break;
             }
         }
         break;
      }
    }

    if (!columnsLine || blockIndent === -1) return null;

    // Parse the columns
    const columns: string[] = [];
    const colRegex = /[^\s()\[\]={}]+/g;
    let match;
    while ((match = colRegex.exec(columnsLine)) !== null) {
       columns.push(match[0]);
    }

    if (line === columnsLine) return null;

    // Find the hovered value index
    const valRegex = /"(?:[^"\\]|\\.)*"|\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|[^\s()\[\]={}]+/g;
    let valIdx = 0;
    while ((match = valRegex.exec(line)) !== null) {
      if (match[0].includes('=')) continue;
      
      const start = match.index;
      const end = start + match[0].length;
      
      if (position.character >= start && position.character <= end) {
         if (valIdx < columns.length) {
            const md = new vscode.MarkdownString();
            md.appendMarkdown(`🔑 Key: **\`${columns[valIdx]}\`**\\n\\n*Column ${valIdx + 1} of ${columns.length}*`);
            return new vscode.Hover(md);
         }
      }
      valIdx++;
    }

    return null;
  }
};

const zeonCompletionProvider: vscode.CompletionItemProvider = {
  async provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position
  ): Promise<vscode.CompletionItem[]> {
    const linePrefix = document.lineAt(position).text.substr(0, position.character);
    const match = linePrefix.match(/^(\s*)([a-zA-Z0-9_\-]*)$/);
    if (!match) return [];

    const indent = match[1];
    const prefix = match[2];

    const completions: vscode.CompletionItem[] = [];
    const schemaMap = new Map<string, { modifier: string, columns: string }>();

    // Scan all zeon files in the workspace
    const uris = await vscode.workspace.findFiles('**/*.zeon');
    for (const uri of uris) {
      try {
        const doc = await vscode.workspace.openTextDocument(uri);
        const text = doc.getText();
        const lines = text.split('\n');

        let currentHeader = '';
        let currentModifier = '';
        let headerIndent = 0;

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].replace(/\r$/, '');
          if (line.trim() === '' || line.trim().startsWith('#')) continue;

          const indentMatch = line.match(/^\s*/);
          const currentIndent = indentMatch ? indentMatch[0].length : 0;

          if (currentHeader && currentIndent > headerIndent) {
            // This is the column line
            if (!line.includes('=')) {
               schemaMap.set(currentHeader, { modifier: currentModifier, columns: line.trim() });
            }
            currentHeader = ''; // Reset after finding columns
            continue;
          }

          if (currentIndent <= headerIndent) {
            currentHeader = '';
          }

          const headerMatch = line.match(/^(\s*)([a-zA-Z0-9_\-]+)(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))/);
          if (headerMatch) {
            currentHeader = headerMatch[2];
            currentModifier = headerMatch[3];
            headerIndent = headerMatch[1].length;
          }
        }
      } catch (e) {
         // ignore files that can't be read
      }
    }

    // Now populate completions
    for (const [header, data] of schemaMap.entries()) {
      if (header.startsWith(prefix)) {
        const item = new vscode.CompletionItem(header, vscode.CompletionItemKind.Struct);
        item.detail = `ZEON Schema: ${header}${data.modifier}`;
        item.documentation = new vscode.MarkdownString(`Columns:\n\n\`${data.columns}\``);
        
        const snippet = new vscode.SnippetString();
        snippet.appendText(`${header}${data.modifier}\n`);
        snippet.appendText(`${indent}  ${data.columns}\n`);
        snippet.appendText(`${indent}  `);
        snippet.appendTabstop(1);

        item.insertText = snippet;
        item.range = new vscode.Range(position.line, position.character - prefix.length, position.line, position.character);
        completions.push(item);
      }
    }

    if ("dict".startsWith(prefix)) {
        const item = new vscode.CompletionItem("dict", vscode.CompletionItemKind.Snippet);
        item.detail = "ZEON Generic Dictionary";
        const snippet = new vscode.SnippetString();
        snippet.appendText(`dict()\n${indent}  key1 value1\n${indent}  key2 value2\n${indent}  `);
        snippet.appendTabstop(1);
        item.insertText = snippet;
        completions.push(item);
    }
    
    if ("list".startsWith(prefix)) {
        const item = new vscode.CompletionItem("list", vscode.CompletionItemKind.Snippet);
        item.detail = "ZEON Generic Table";
        const snippet = new vscode.SnippetString();
        snippet.appendText(`list[]\n${indent}  col1 col2\n${indent}  val1 val2\n${indent}  `);
        snippet.appendTabstop(1);
        item.insertText = snippet;
        completions.push(item);
    }

    return completions;
  }
};

export function activate(context: vscode.ExtensionContext) {
  // Register Semantic Token Provider
  context.subscriptions.push(
    vscode.languages.registerDocumentSemanticTokensProvider(
      { language: 'zeon' },
      semanticProvider,
      legend
    )
  );

  // Register Hover Provider
  context.subscriptions.push(
    vscode.languages.registerHoverProvider(
      { language: 'zeon' },
      hoverProvider
    )
  );

  // Register Completion Item Provider
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      { language: 'zeon' },
      zeonCompletionProvider,
      ...['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    )
  );

  // Linter / Diagnostics
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('zeon');
  context.subscriptions.push(diagnosticCollection);

  const updateDiagnostics = (document: vscode.TextDocument) => {
    if (document.languageId !== 'zeon' && !document.fileName.endsWith('.zeon')) return;

    const diagnostics: vscode.Diagnostic[] = [];
    const text = document.getText();
    const lines = text.split('\n');

    let inTabularBlock = false;
    let blockIndent = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].replace(/\r$/, '');
      if (line.trim() === '' || line.trim().startsWith('#')) continue;

      const indentMatch = line.match(/^\s*/);
      const currentIndent = indentMatch ? indentMatch[0].length : 0;

      if (inTabularBlock && currentIndent <= blockIndent) {
        inTabularBlock = false;
      }

      const headerMatch = line.match(/^(\s*)([a-zA-Z0-9_\-]+)(.*)$/);
      if (headerMatch && (currentIndent === 0 || !inTabularBlock)) {
        const suffix = headerMatch[3].trim();
        if (suffix.startsWith('=')) continue;

        if (suffix.length > 0 && /[(\[{]/.test(suffix)) {
          if (!/^(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))$/.test(suffix)) {
            const startIdx = line.indexOf(headerMatch[2]) + headerMatch[2].length;
            diagnostics.push(new vscode.Diagnostic(
              new vscode.Range(i, startIdx, i, startIdx + suffix.length),
              `Invalid ZEON Block Modifier: "${suffix}". Blocks can only use [], {}, (), [][], [2], [3] or {[]}. Do not insert random characters inside the modifiers.`,
              vscode.DiagnosticSeverity.Error
            ));
          }
          inTabularBlock = true;
          blockIndent = headerMatch[1].length;
          continue;
        }
        if (line.match(/^(\s*)([a-zA-Z0-9_\-]+)(\[\]\[\]|\[\]|\[\d+\]|\{\}|\{\[\]\}|\(\))/)) {
          inTabularBlock = true;
          blockIndent = headerMatch[1].length;
          continue;
        }
      }
    }

    try {
      parse(text);
    } catch (e: any) {
      const msg = e.message || String(e);
      // Extrai o número da linha do erro levantado pelo parser nativo do Zeon
      const lineMatch = msg.match(/at line (\d+)/);
      let errorLine = 0;
      
      if (lineMatch) {
          errorLine = parseInt(lineMatch[1], 10) - 1; // Ajustando para 0-index
      }
      
      errorLine = Math.max(0, Math.min(errorLine, document.lineCount - 1));
      const lineText = document.lineAt(errorLine).text;
      
      diagnostics.push(new vscode.Diagnostic(
          new vscode.Range(errorLine, 0, errorLine, lineText.length),
          msg,
          vscode.DiagnosticSeverity.Error
      ));
    }

    diagnosticCollection.set(document.uri, diagnostics);
  };

  // Run diagnostics on open and on change
  if (vscode.window.activeTextEditor) {
    updateDiagnostics(vscode.window.activeTextEditor.document);
  }
  
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(e => updateDiagnostics(e.document))
  );

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(e => updateDiagnostics(e))
  );

  let currentPanel: vscode.WebviewPanel | undefined = undefined;
  let currentTargetDocument: vscode.TextDocument | undefined = undefined;

  let disposable = vscode.commands.registerCommand('zeon.showPreview', async (uri?: vscode.Uri) => {
    if (uri) {
      currentTargetDocument = await vscode.workspace.openTextDocument(uri);
    } else if (vscode.window.activeTextEditor) {
      currentTargetDocument = vscode.window.activeTextEditor.document;
    }

    if (!currentTargetDocument || currentTargetDocument.languageId !== 'zeon') {
      vscode.window.showErrorMessage('No active ZEON document found.');
      return;
    }

    if (currentPanel) {
      currentPanel.reveal(vscode.ViewColumn.Active);
      const showTip = context.globalState.get<boolean>('zeon.showPreviewTip', true);
      currentPanel.webview.html = getPreviewHtml(currentTargetDocument.getText(), showTip);
      currentPanel.title = `Preview: ${currentTargetDocument.fileName.split('/').pop()?.split('\\').pop()}`;
    } else {
      currentPanel = vscode.window.createWebviewPanel(
        'zeonPreview',
        `Preview: ${currentTargetDocument.fileName.split('/').pop()?.split('\\').pop()}`,
        vscode.ViewColumn.Active,
        { enableScripts: true }
      );

      const updateWebview = () => {
        if (currentPanel && currentTargetDocument) {
          const showTip = context.globalState.get<boolean>('zeon.showPreviewTip', true);
          currentPanel.webview.html = getPreviewHtml(currentTargetDocument.getText(), showTip);
        }
      };

      updateWebview();

      const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
        if (currentTargetDocument && e.document.uri.toString() === currentTargetDocument.uri.toString()) {
          updateWebview();
        }
      });

      let messageQueue = Promise.resolve();

      currentPanel.webview.onDidReceiveMessage((message) => {
         messageQueue = messageQueue.then(async () => {
            if (message.command === 'closeTip') {
               context.globalState.update('zeon.showPreviewTip', false);
               return;
            }

            if (message.command === 'save') {
               if (currentTargetDocument) {
                   if (currentTargetDocument.isClosed) {
                       vscode.window.showErrorMessage('ZEON file is closed.');
                       return;
                   }
                   await currentTargetDocument.save();
                   vscode.window.showInformationMessage('ZEON file saved!');
               }
               return;
            }

            if (message.command === 'edit' && currentTargetDocument) {
               if (currentTargetDocument.isClosed) return;
               
               const lineText = currentTargetDocument.lineAt(message.line).text;
               const edit = new vscode.WorkspaceEdit();

               if (message.type === 'blockKey') {
                  const match = lineText.match(/^(\s*)([a-zA-Z0-9_\-]+)/);
                  if (match) {
                     const start = match[1].length;
                     const end = start + match[2].length;
                     const range = new vscode.Range(message.line, start, message.line, end);
                     edit.replace(currentTargetDocument.uri, range, message.newValue);
                  }
               } else if (message.type === 'colKey') {
                  const colRegex = /[^\s()\[\]={}]+/g;
                  let match;
                  let currentIdx = 0;
                  while ((match = colRegex.exec(lineText)) !== null) {
                     if (currentIdx === message.idx) {
                        const range = new vscode.Range(message.line, match.index, message.line, match.index + match[0].length);
                        edit.replace(currentTargetDocument.uri, range, message.newValue);
                        break;
                     }
                     currentIdx++;
                  }
               } else {
                  const valRegex = /"(?:[^"\\]|\\.)*"|\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|[^\s()\[\]={}]+/g;
                  let match;
                  let currentIdx = 0;
                  
                  while ((match = valRegex.exec(lineText)) !== null) {
                     if (match[0].includes('=')) continue;
                     
                     if (currentIdx === message.idx) {
                        const range = new vscode.Range(
                           new vscode.Position(message.line, match.index),
                           new vscode.Position(message.line, match.index + match[0].length)
                        );
                        
                        edit.replace(currentTargetDocument.uri, range, message.newValue);
                        break;
                     }
                     currentIdx++;
                  }
               }
               await vscode.workspace.applyEdit(edit);
               
               if (message.saveAfter && currentTargetDocument) {
                   await currentTargetDocument.save();
                   vscode.window.showInformationMessage('ZEON file saved!');
               }
            }
         });
      }, undefined, context.subscriptions);

      currentPanel.onDidDispose(() => {
        changeDocumentSubscription.dispose();
        currentPanel = undefined;
        currentTargetDocument = undefined;
      }, null, context.subscriptions);
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
