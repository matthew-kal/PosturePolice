// background_camera.js
const express = require('express');
const NodeWebcam = require('node-webcam');

const app = express();
const PORT = 8081;

const webcam = NodeWebcam.create({
  width: 640,
  height: 480,
  delay: 0,
  output: 'jpeg',
  callbackReturn: 'buffer',
  verbose: false
});

let clients = [];

app.get('/stream', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'multipart/x-mixed-replace; boundary=frame',
    'Cache-Control': 'no-cache',
    'Connection': 'close',
    'Pragma': 'no-cache'
  });

  clients.push(res);

  req.on('close', () => {
    clients = clients.filter(client => client !== res);
  });
});

app.listen(PORT, () => {
  console.log(`🟢 MJPEG stream running at http://localhost:${PORT}/stream`);
});

setInterval(() => {
  webcam.capture('frame', (err, buffer) => {
    if (!err && buffer) {
      const header = `--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${buffer.length}\r\n\r\n`;
      clients.forEach(res => {
        res.write(header);
        res.write(buffer);
        res.write('\r\n');
      });
    }
  });
}, 1000 / 20); // 20 FPS
