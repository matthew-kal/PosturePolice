import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';
import axios from 'axios';

let pythonProcess: ReturnType<typeof spawn> | null = null;

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('PosturePolice.startApp', async () => {
      const backendPath = path.join(context.extensionPath, 'backend', 'api.py');
      const pythonPath = 'python';

      // 🔹 Start Python backend
      pythonProcess = spawn(pythonPath, [backendPath], {
        cwd: path.dirname(backendPath),
        shell: true,
      });

      if (pythonProcess.stdout) {
        pythonProcess.stdout.on('data', (data) => console.log(`[PYTHON]: ${data}`));
      }
      if (pythonProcess.stderr) {
        pythonProcess.stderr.on('data', (data) => console.error(`[PYTHON ERROR]: ${data}`));
      }
      pythonProcess.on('close', (code) => console.log(`Python server exited with code ${code}`));

      // 🔹 Wait for backend to be ready (poll until FastAPI responds)
      const maxRetries = 20;
      let tries = 0;
      let serverReady = false;

      while (!serverReady && tries < maxRetries) {
        try {
          await axios.get('http://localhost:8000/docs'); // FastAPI's default docs page
          serverReady = true;
        } catch {
          await new Promise((res) => setTimeout(res, 500));
          tries++;
        }
      }

      if (!serverReady) {
        vscode.window.showErrorMessage('Failed to start backend server.');
        return;
      }

      // 🔹 Launch frontend after server is ready
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

export function deactivate() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}
