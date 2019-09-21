const path = require('path');
const express = require('express');
const app = express();
var socket = require('socket.io-client')('http://localhost:5000');

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Access-Control-Allow-Origin, Cache-Control");
    next()
});
app.set('port', process.env.PORT || 3000);
app.use(express.json());
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/templates/index.html'));
});

socket.on('connect', function () {
    console.log("connect")
});

socket.on('disconnect', function () {
    console.log("disconnet")

});

socket.on('image', function (msg) {
    console.log('works')
})
socket.on('image', function () {
    console.log('works')
})

socket.on('my event', function (json) {
    console.log('e')
    console.log(json)

});
socket.on('my response', function (msg) {
    console.log('r')
    console.log(msg)
})

app.listen(3000, () => {
    console.log(`Server on port ${app.get('port')}`);
});