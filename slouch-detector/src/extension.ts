import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Slouch Detector extension is now active!');

    const disposable = vscode.commands.registerCommand('slouch-detector.helloWorld', () => {
        // Create and show a new webview panel
        const panel = vscode.window.createWebviewPanel(
            'slouchDetectorWebview',  // Internal identifier
            'Slouch Detector',  // Title displayed in the VS Code tab
            vscode.ViewColumn.One,  // Show in first column
            {
                enableScripts: true, // Allow JavaScript execution
                retainContextWhenHidden: true // Keep webview active when switching tabs
            }
        );

        // Set the Webview's HTML content
        panel.webview.html = getWebviewContent();
    });

    context.subscriptions.push(disposable);
}

function getWebviewContent(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slouch Detector</title>
</head>
<body>
    <h2>Slouch Detector Webview</h2>
    <p>This is a Webview inside your VS Code extension!</p>
</body>
</html>`;
}

export function deactivate() {}