import * as vscode from 'vscode';
import * as path from 'path';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {

    context.subscriptions.push(
        vscode.commands.registerCommand('PosturePolice.startApp', async () => {
            const chromeLauncher = await import('chrome-launcher'); // Dynamically import
            chromeLauncher.launch({
                ignoreDefaultFlags: true,
                chromeFlags: [
                    `--app=file:///${path.join(context.extensionPath, 'camera', 'camera.html').replace('\\', '/')}`,
                ]
            });
        })
    );
}

// This method is called when your extension is deactivated
export function deactivate() {}
