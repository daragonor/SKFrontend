import cv2
from darkflow.net.build import TFNet
import numpy as np
import base64
#import time
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
import eventlet
import asyncio

eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins="*")


class Detector:
    def __init__(self):
        self.tfnet = None
        self.capture = None

    async def proccess(self, ret, frame):
        if ret:
            results = self.tfnet.return_predict(frame)
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                label = result['label']
                confidence = result['confidence']
                text = '{}: {:.0f}%'.format(label, confidence * 100)
                frame = cv2.rectangle(frame, tl, br, color, 5)
                frame = cv2.putText(
                    frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2) 
            cv2.imshow('frame',frame)
            print(data)
            #socketio.emit('results', json.dumps(str(results)))
            # print('FPS {:.1f}'.format(1 / (time.time() - stime)))

    def detect(self):
        # stime = time.time()
        if self.capture == None and self.tfnet == None:
            print(self.tfnet)
            print(self.capture)
            return
        ret, frame = self.capture.read()
        ret, buffer = cv2.imencode('.jpg', frame)
        img = base64.b64encode(buffer)
        socketio.emit('wcap', img.decode("utf-8"))
        asyncio.run(self.proccess(ret, frame))


detector = Detector()
options = {
    'model': 'assets/yolov2-tiny.cfg',
    'load': 'assets/yolov2-tiny_8000.weights',
    'labels': 'assets/classes.txt',
    'threshold': 0.2,
    'gpu': 1.0
}
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]


@app.route('/')
def sessions():
    return render_template('index.html')


def listen():
    while True:
        detector.detect()
        eventlet.sleep(0.1)


@socketio.on('connect')
def on_connection():
    print("connected")
    global detector
    detector.tfnet = TFNet(options)
    detector.capture = cv2.VideoCapture(0)
    detector.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    detector.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    eventlet.spawn(listen)

if __name__ == '__main__':
    socketio.run(app, "127.0.0.1", 5000, debug=True)
