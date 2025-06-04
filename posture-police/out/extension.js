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
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
let controlServerProcess = null;
function activate(context) {
    // 🟢 Start control server once at activation
    if (!controlServerProcess) {
        const scriptPath = path.join(context.extensionPath, 'src', 'camera', 'camera_hub.js');
        controlServerProcess = (0, child_process_1.spawn)('node', [scriptPath]);
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
    context.subscriptions.push(vscode.commands.registerCommand('PosturePolice.startApp', async () => {
        const chromeLauncher = await import('chrome-launcher');
        chromeLauncher.launch({
            ignoreDefaultFlags: true,
            chromeFlags: [
                `--app=file:///${path.join(context.extensionPath, 'src', 'camera', 'camera.html').replace(/\\/g, '/')}`,
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-background-media-suspend',
                '--autoplay-policy=no-user-gesture-required'
            ]
        });
    }));
}
function deactivate() {
    if (controlServerProcess && !controlServerProcess.killed) {
        controlServerProcess.kill();
        controlServerProcess = null;
    }
}
//# sourceMappingURL=extension.js.map