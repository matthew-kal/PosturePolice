/* camera_hub.js  – CommonJS file with one dynamic ESM import ------------ */
const express = require('express');
const cv      = require('opencv4nodejs');
const { once } = require('events');

(async () => {
  /* dynamic import: grab BOTH the default fn and the helper */
  const { default: getPort, portNumbers } = await import('get-port');

  /* first free port in the preferred ranges (fallback → any free port) */
  const CTRL_PORT   = await getPort({ port: portNumbers(3000, 3010) });
  const STREAM_PORT = await getPort({ port: portNumbers(8081, 8090) });

  /* ------------------------------------------------------------------ */
  /* …everything below stays exactly as before…                         */
  let streamServer, cap;

  const ctrl = express();
  ctrl.use((_, res, next) => {
    res.set({
      'Access-Control-Allow-Origin' : '*',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    next();
  });

  /* ---------- /start (unchanged) ------------------------------------ */
  ctrl.get('/start', async (_req, res) => {
    if (streamServer) return res.json({ status: 'running', port: STREAM_PORT });

    cap = new cv.VideoCapture(0);
    cap.set(cv.CAP_PROP_FRAME_WIDTH , 640);
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480);

    const streamApp = express();
    streamApp.get('/stream', (req, rsp) => {
      rsp.writeHead(200, {
        'Content-Type'               : 'multipart/x-mixed-replace; boundary=frame',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control'              : 'no-cache',
        'Connection'                 : 'close'
      });

      const id = setInterval(() => {
        const frame = cap.read();
        if (frame.empty) { cap.reset(); return; }
        const jpg = cv.imencode('.jpg', frame);
        rsp.write(`--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${jpg.length}\r\n\r\n`);
        rsp.write(jpg); rsp.write('\r\n');
      }, 50);

      req.on('close', () => clearInterval(id));
    });

    streamServer = streamApp.listen(STREAM_PORT,
      () => console.log(`🟢 MJPEG → http://localhost:${STREAM_PORT}/stream`));

    await once(streamServer, 'listening');
    res.json({ status: 'started', port: STREAM_PORT });
  });

  /* ---------- /stop (unchanged) ------------------------------------- */
  ctrl.get('/stop', async (_req, res) => {
    if (!streamServer) return res.json({ status: 'already stopped' });

    streamServer.close(); await once(streamServer, 'close');
    streamServer = undefined;

    if (cap) { cap.release(); cap = undefined; }
    res.json({ status: 'stopped' });
  });

  ctrl.listen(CTRL_PORT,
    () => console.log(`🎛️  Controller → http://localhost:${CTRL_PORT}`));

  const shutdown = async () => {
    try { await fetch(`http://localhost:${CTRL_PORT}/stop`).catch(()=>{}); }
    finally { process.exit(0); }
  };
  process.on('SIGINT',  shutdown);
  process.on('SIGTERM', shutdown);
})();
