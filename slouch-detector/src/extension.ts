import * as vscode from 'vscode';
import * as path from 'path';


export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('PosturePolice.startApp', async () => {

      const chromeLauncher = await import('chrome-launcher');
      chromeLauncher.launch({
        ignoreDefaultFlags: true,
        chromeFlags: [
          `--app=file:///${path.join(context.extensionPath, 'camera', 'camera.html').replace(/\\/g, '/')}`
        ]
      });
    })
  );
}
