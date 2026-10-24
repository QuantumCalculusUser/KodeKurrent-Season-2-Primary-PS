const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld('draftmateDesktop', Object.freeze({ platform: process.platform }));
