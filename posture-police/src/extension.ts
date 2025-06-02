import * as vscode from 'vscode';
import * as path from 'path';
import * as http from 'http';
import express from 'express';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';

let cameraProcess: ChildProcessWithoutNullStreams | null = null;

export function activate(context: vscode.ExtensionContext) {
  // 🔹 Launch lightweight internal Express server
  const app = express();
  const launcherPort = 3000;
  
  
    app.get('/start-stream', (req: express.Request, res: express.Response) => {
      if (cameraProcess) {
        res.status(200).send('Stream already running.');
        return;
      }
    app.listen(launcherPort, () => {
      console.log(`🟢 Launcher backend ready at http://localhost:${launcherPort}`);
    });
    const scriptPath = path.join(context.extensionPath, 'src', 'camera', 'background_camera.js');

    cameraProcess = spawn('node', [scriptPath]);

    cameraProcess.stdout.on('data', data => console.log(`[camera]: ${data}`));
    cameraProcess.stderr.on('data', data => console.error(`[camera ERROR]: ${data}`));
    cameraProcess.on('close', code => {
      console.log(`[camera] exited with code ${code}`);
      cameraProcess = null;
    });

    res.send('Camera stream started.');
  });

  app.listen(launcherPort, () => {
    console.log(`🟢 Launcher backend ready at http://localhost:${launcherPort}`);
  });

  // 🔹 Register VSCode command to open camera.html
  context.subscriptions.push(
    vscode.commands.registerCommand('PosturePolice.startApp', async () => {
      const chromeLauncher = await import('chrome-launcher');

      chromeLauncher.launch({
        ignoreDefaultFlags: true,
        chromeFlags: [
          `--app=file:///${path.join(context.extensionPath, 'src', 'camera', 'test.html').replace(/\\/g, '/')}`,
          '--disable-background-timer-throttling',
          '--disable-backgrounding-occluded-windows',
          '--disable-renderer-backgrounding',
          '--disable-background-media-suspend',
          '--disable-features=CalculateNativeWinOcclusion',
          '--autoplay-policy=no-user-gesture-required'
        ]
      });
    })
  );
}
