const { app, BrowserWindow, dialog, shell } = require('electron');
const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const http = require('node:http');

let backend = null;
let mainWindow = null;
const API_URL = 'http://127.0.0.1:8000';

function requestHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${API_URL}/api/health`, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        if (res.statusCode < 200 || res.statusCode >= 300) return resolve({ ready: false, incompatible: false });
        try {
          const data = JSON.parse(body);
          const compatible = data?.features?.case_draft === true;
          resolve({ ready: compatible, incompatible: !compatible });
        } catch { resolve({ ready: false, incompatible: true }); }
      });
    });
    req.setTimeout(1200, () => { req.destroy(); resolve({ ready: false, incompatible: false }); });
    req.on('error', () => resolve({ ready: false, incompatible: false }));
  });
}

async function waitForBackend() {
  let incompatibleServerSeen = false;
  for (let i = 0; i < 60; i++) {
    const status = await requestHealth();
    if (status.ready) return { ready: true, incompatible: false };
    incompatibleServerSeen = incompatibleServerSeen || status.incompatible;
    await new Promise((r) => setTimeout(r, 500));
  }
  return { ready: false, incompatible: incompatibleServerSeen };
}

function startBackend() {
  const isPackaged = app.isPackaged;
  const projectRoot = path.resolve(__dirname, '..');
  const exePath = path.join(process.resourcesPath, 'backend', 'draftmate-api.exe');
  const pythonExe = path.join(projectRoot, 'backend', '.venv', 'Scripts', 'python.exe');
  const backendScript = path.join(projectRoot, 'backend', 'desktop_entry.py');
  const userData = app.getPath('userData');
  fs.mkdirSync(userData, { recursive: true });
  const env = {
    ...process.env,
    OLLAMA_BASE_URL: process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434',
    OLLAMA_MODEL: process.env.OLLAMA_MODEL || 'qwen2.5:7b',
    DATABASE_PATH: path.join(userData, 'draftmate.db'),
    MAX_UPLOAD_MB: process.env.MAX_UPLOAD_MB || '15',
    DRAFTMATE_HOST: '127.0.0.1',
    DRAFTMATE_PORT: '8000',
    DRAFTMATE_STATIC_DIR: path.join(projectRoot, 'backend', 'static')
  };
  let command, args;
  if (isPackaged) {
    if (!fs.existsSync(exePath)) throw new Error(`Bundled backend executable is missing:\n${exePath}`);
    command = exePath; args = [];
  } else {
    if (!fs.existsSync(pythonExe)) throw new Error(`Python environment not found:\n${pythonExe}\nRun RUN_DRAFTMATE.bat to set up the app.`);
    if (!fs.existsSync(backendScript)) throw new Error(`Backend entry point not found:\n${backendScript}`);
    command = pythonExe; args = [backendScript];
  }
  backend = spawn(command, args, {
    cwd: isPackaged ? userData : path.join(projectRoot, 'backend'),
    env, windowsHide: true, stdio: isPackaged ? 'ignore' : 'inherit'
  });
  backend.on('error', (err) => console.error('DraftMate backend launch error:', err));
  backend.on('exit', (code) => { if (code && code !== 0) console.error(`DraftMate backend exited with code ${code}`); });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1480, height: 960, minWidth: 1050, minHeight: 700,
    title: 'DraftMate AI', backgroundColor: '#f7f0df',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://') || url.startsWith('http://')) shell.openExternal(url);
    return { action: 'deny' };
  });
  mainWindow.loadURL(API_URL);
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(async () => {
  try {
    startBackend();
    const status = await waitForBackend();
    if (!status.ready) {
      await dialog.showMessageBox({ type: 'error', title: 'DraftMate AI could not start',
        message: status.incompatible ? 'An older or incompatible DraftMate backend is already responding on port 8000.' : 'The local DraftMate backend did not become ready.',
        detail: status.incompatible
          ? 'Close every DraftMate window. In Task Manager, end any leftover DraftMate/Electron or Python process belonging to an older copy, then launch RUN_DRAFTMATE.bat from this extracted project folder again.'
          : 'Close duplicate DraftMate windows and restart this project. If this repeats, check the Command Prompt above for backend startup errors. Ollama is needed for AI drafting; the dashboard can open without it.' });
      app.quit();
      return;
    }
    createWindow();
  } catch (e) {
    await dialog.showMessageBox({ type: 'error', title: 'DraftMate AI startup error', message: e.message });
    app.quit();
  }
});

app.on('before-quit', () => { if (backend && !backend.killed) backend.kill(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0 && backend) createWindow(); });
