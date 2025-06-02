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
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const express_1 = __importDefault(require("express"));
const child_process_1 = require("child_process");
let cameraProcess = null;
function activate(context) {
    // 🔹 Launch lightweight internal Express server
    const app = (0, express_1.default)();
    const launcherPort = 3000;
    app.get('/start-stream', (req, res) => {
        if (cameraProcess) {
            res.status(200).send('Stream already running.');
            return;
        }
        const scriptPath = path.join(context.extensionPath, 'src', 'camera', 'background_camera.js');
        cameraProcess = (0, child_process_1.spawn)('node', [scriptPath]);
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
    context.subscriptions.push(vscode.commands.registerCommand('PosturePolice.startApp', async () => {
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
    }));
}
//# sourceMappingURL=extension.js.map