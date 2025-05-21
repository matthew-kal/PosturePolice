"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
const axios_1 = __importDefault(require("axios"));
let pythonProcess = null;
function activate(context) {
    context.subscriptions.push(vscode.commands.registerCommand('PosturePolice.startApp', async () => {
        const backendPath = path.join(context.extensionPath, 'backend', 'api.py');
        const pythonPath = 'python';
        // 🔹 Start Python backend
        pythonProcess = (0, child_process_1.spawn)(pythonPath, [backendPath], {
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
                await axios_1.default.get('http://localhost:8000/docs'); // FastAPI's default docs page
                serverReady = true;
            }
            catch {
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
    }));
}
function deactivate() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}
//# sourceMappingURL=extension.js.map