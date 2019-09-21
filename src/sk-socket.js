const express = require('express')
const app = express();
const path = require('path');
const server = require('http').Server(app);
const io = require('socket.io')(5000);
const cv = require('opencv4nodejs');
const wCap = new cv.VideoCapture(0);
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/templates/index.html'));
});
io.on('results', (results) => {
    console.log(results)
})
setInterval(() => {
    const frame = wCap.read();
    const image = cv.imencode('.jpg', frame).toString('base64');
    io.emit('wcap', image);
}, 70);

server.listen(3000);

