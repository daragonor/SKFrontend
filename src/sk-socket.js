const express = require('express')
const app = express();
const path = require('path');
const server = app.listen(5000);
const io = require('socket.io').listen(server);
const cv = require('opencv4nodejs');
const client = require('socket.io-client')('http://localhost:5000')
const wCap = new cv.VideoCapture(0);
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/templates/index.html'));
});
client.on('results', function (results) {
    console.log(results)
})
client.on('results', function () {
    console.log(results)
})
setInterval(() => {
    const frame = wCap.read();
    const image = cv.imencode('.jpg', frame).toString('base64');
    io.emit('wcap', image);
}, 70);

//server.listen(3000);

