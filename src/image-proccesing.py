import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import base64
import socketio
import json


options = {
    'model': 'assets/yolov2-tiny.cfg',
    'load': 'assets/yolov2-tiny_8000.weights',
    'labels': 'assets/classes.txt',
    'threshold': 0.2,
    'gpu': 1.0
}

tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]


sio = socketio.Client()


@sio.event
def connect():
    print('connected to server')


@sio.on('wcap')
def onwCap(image):
    decoded_string = base64.b64decode(image)
    nparr = np.fromstring(decoded_string, dtype=np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
    results = tfnet.return_predict(img)
    # json.dumps(results
    print(results)
    sio.emit('results', "holas")


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.wait()

""" capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# eventlet.wsgi.server(eventlet.listen(('', 5000), app)

while True:
    stime = time.time()
    ret, frame = capture.read()
    if ret:
        results = tfnet.return_predict(frame)
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label']
            confidence = result['confidence']
            text = '{}: {:.0f}%'.format(label, confidence * 100)
            frame = cv2.rectangle(frame, tl, br, color, 5)
            frame = cv2.putText(
                frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        # cv2.imshow('frame', frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        # socketio.emit('image', jpg_as_text, methods=['GET', 'POST'])

        print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        capture.release()
        cv2.destroyAllWindows()
 """
