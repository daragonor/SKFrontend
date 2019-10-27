#from darkflow.net.build import TFNet
import numpy as np
import base64
#import time
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from numpy import array
import eventlet
import asyncio
from core.yolo_tiny import YOLOv3_tiny
import tensorflow.compat.v1 as tf
import cv2

eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins="*")
CAM = 2
NUM_PARALLEL_EXEC_UNITS = 5


def load_class_names():
    """Returns a list of string corresonding to class names and it's length"""
    with open('./assets/obj.names', 'r') as f:
        class_names = f.read().splitlines()

    return class_names


class Detector:
    def __init__(self):
        self.capture = cv2.VideoCapture(CAM)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.model = YOLOv3_tiny(n_classes=36,
                                 iou_threshold=0.2,
                                 confidence_threshold=0.2)
        self.inputs = tf.placeholder(
            tf.float32, [1, *self.model.input_size, 3])
        self.detections = self.model(self.inputs)
        self.saver = tf.train.Saver(
            tf.global_variables(scope=self.model.scope))
        self.class_names = load_class_names()
        self.config = tf.ConfigProto(intra_op_parallelism_threads=NUM_PARALLEL_EXEC_UNITS,
                                     inter_op_parallelism_threads=2,
                                     allow_soft_placement=True,
                                     device_count={'CPU': NUM_PARALLEL_EXEC_UNITS})
        self.sess = tf.Session(config=self.config)

    async def detect(self):
        if self.saver == None or self.capture == None or self.model == None:

            return
        ret, frame = self.capture.read()
        #img = base64.b64encode(buffer)
        #socketio.emit('wcap', img.decode("utf-8"))
        if ret:
            self.proccess(frame)

    def proccess(self, frame):

        data = []
        self.saver.restore(
            self.sess, './assets/weights/model-tiny.ckpt')
        resized_frame = cv2.resize(frame, dsize=tuple(
            (x) for x in self.model.input_size[::-1]), interpolation=cv2.INTER_NEAREST)

        results = self.sess.run(self.detections, feed_dict={
            self.inputs: [resized_frame]})

        frame_size = (1920, 1080)
        boxes_dict = results[0]
        resize_factor = (
            frame_size[0] / self.model.input_size[1], frame_size[1] / self.model.input_size[0])
        for cls in range(len(self.class_names)):
            boxes = boxes_dict[cls]
            if np.size(boxes) != 0:
                for box in boxes:
                    xy, confidence = box[:4], box[4]
                    xy = [int(xy[i] * resize_factor[i % 2]) for i in range(4)]
                    data.append({
                        "label": self.class_names[cls],
                        "confidence": f'{confidence}',
                        "topleft": {
                            "x": xy[0],
                            "y": xy[1]
                        },
                        "bottomright": {
                            "x": xy[2],
                            "y": xy[3]
                        }
                    })
        if data != []:
            print(data)
            socketio.emit('results', json.dumps(data))


@app.route('/')
def sessions():
    return render_template('index.html')


def listen():
    detector = Detector()
    print("init")
    while True:
        asyncio.run(detector.detect())
        print("***")
        eventlet.sleep(0.01)


@socketio.on('connect')
def on_connection():
    print("connected")


eventlet.spawn(listen)

if __name__ == '__main__':
    socketio.run(app, "127.0.0.1", 5000)
