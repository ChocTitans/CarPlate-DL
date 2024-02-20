const { app, BrowserWindow, webContents } = require('electron')

app.whenReady().then(() => {
  const mainWindow = new BrowserWindow({ height: 768, width: 1024 })
  mainWindow.setMenuBarVisibility(false)
  mainWindow.loadFile('index.html')
  setTimeout(() => {
    const contents = webContents.getAllWebContents()[0]
    contents.loadURL('http://localhost:5050')
  }, 1000)
})