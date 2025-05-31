from base64 import b64encode
from ultralytics import YOLO
from logging import CRITICAL
from asyncio import create_task
from socketio import AsyncServer
from ultralytics.utils import LOGGER
from aiohttp.web import Application, run_app
from cv2 import VideoCapture, imencode, resize, rectangle, putText, FONT_ITALIC
from time import sleep
from threading import Thread

app = Application()
server = AsyncServer(cors_allowed_origins="*")
server.attach(app)
cam = VideoCapture(0)
LOGGER.setLevel(CRITICAL)
current_connections = set()


@server.event
async def connect(socket_id, env):
    print(f"socket with id: {socket_id} connected")
    current_connections.add(socket_id)


def object_outlines(image, model, labels):
    results = model(image, conf=0.3)
    res = []
    for result in results:
        for box in result.boxes:
            index = int(box.cls[0])
            label = model.names[index]
            if label in labels:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                res.append((x1, y1, x2, y2, label))

    return res


def outline_updater(socket_id, outline, frame, model, labels):
    while socket_id in current_connections:
        outline[0] = object_outlines(frame[0], model, labels)
        sleep(0.5)


async def stream_video(socket_id):
    model = YOLO('yolov8n.pt')
    labels = {"person", "car", "bus", "truck"}

    outlines = [[]]
    frame = [None]
    model_thread = Thread(target=outline_updater, args=(
        socket_id, outlines, frame, model, labels))
    model_thread.start()

    while socket_id in current_connections:
        success, f = cam.read()
        frame[0] = resize(f, (300, 200))

        for x1, y1, x2, y2, label in outlines[0]:
            rectangle(frame[0], (x1, y1), (x2, y2), (0, 255, 0), 1)
            putText(frame[0], label, (x1, y1 - 10),
                    FONT_ITALIC, 0.5, (0, 255, 0), 1)

        if not success:
            continue
        _, buffer = imencode('.jpg', frame[0])

        jpg_as_text = b64encode(buffer).decode('utf-8')
        await server.emit('video_frame', jpg_as_text)


@server.event
async def start_stream(socket_id):
    print("Stream requested")
    create_task(stream_video(socket_id))


run_app(app, host="0.0.0.0", port=8000)
