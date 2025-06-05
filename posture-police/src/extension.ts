import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';

let controlServerProcess: ChildProcessWithoutNullStreams | null = null;

export function activate(context: vscode.ExtensionContext) {
  // 🟢 Start control server once at activation
  if (!controlServerProcess) {
    const scriptPath = path.join(context.extensionPath, 'dist', 'camera_hub.js');
    controlServerProcess = spawn('node', [scriptPath]);

    controlServerProcess.stdout.on('data', data => {
      console.log(`[controller]: ${data}`);
    });

    controlServerProcess.stderr.on('data', data => {
      console.error(`[controller ERROR]: ${data}`);
    });

    controlServerProcess.on('close', code => {
      console.log(`[controller] exited with code ${code}`);
      controlServerProcess = null;
    });
  }

  // 🖥️ Launch the Chrome app (frontend)
  context.subscriptions.push(
    vscode.commands.registerCommand('PosturePolice.startApp', async () => {
      const chromeLauncher = await import('chrome-launcher');

      chromeLauncher.launch({
        ignoreDefaultFlags: true,
        chromeFlags: [
          `--app=file:///${path.join(context.extensionPath, 'camera', 'camera.html').replace(/\\/g, '/')}`,
          '--disable-background-timer-throttling',
          '--disable-renderer-backgrounding',
          '--disable-backgrounding-occluded-windows',
          '--disable-background-media-suspend',
          '--autoplay-policy=no-user-gesture-required'
        ]
      });
    })
  );
}

export function deactivate () {
  if (controlServerProcess && !controlServerProcess.killed) {
    controlServerProcess.kill();
    controlServerProcess = null;
  }
}