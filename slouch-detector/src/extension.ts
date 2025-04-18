import * as vscode from 'vscode';
import * as path from 'path';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
    console.log('Congratulations, your extension "slouch-detector" is now active!');

    const disposable = vscode.commands.registerCommand('slouch-detector.helloWorld', () => {
        vscode.window.showInformationMessage('Hello World from Slouch Detector!');
    });

    context.subscriptions.push(disposable);

    context.subscriptions.push(
        vscode.commands.registerCommand('slouch-detector.openCamera', async () => {
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
