from base64 import b64encode
from ultralytics import YOLO
from logging import CRITICAL
from asyncio import create_task
from socketio import AsyncServer
from ultralytics.utils import LOGGER
from aiohttp.web import Application, run_app
from cv2 import VideoCapture, imencode, resize, rectangle, putText, FONT_ITALIC

app = Application()
server = AsyncServer(cors_allowed_origins="*")
server.attach(app)
cam = VideoCapture(0)
LOGGER.setLevel(CRITICAL)


@server.event
async def connect(socket_id, env):
    print(f"socket with id: {socket_id} connected")


def object_outlines(image, model, labels):
    results = model(image, conf=0.5)
    res = []
    for result in results:
        for box in result.boxes:
            index = int(box.cls[0])
            label = model.names[index]
            if label in labels:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                res.append((x1, y1, x2, y2, label))

    return res


async def stream_video():
    model = YOLO('yolov8n.pt')
    labels = {"car", "truck", "bus", "person"}

    outlines = []
    frame_count = 0

    while 1:
        success, frame = cam.read()
        frame = resize(frame, (300, 200))
        frame_count = (frame_count + 1) % 20

        if frame_count == 19:
            outlines = object_outlines(frame, model, labels)

        for x1, y1, x2, y2, label in outlines:
            rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            putText(frame, label, (x1, y1 - 10), FONT_ITALIC,
                    0.5, (0, 255, 0), 2)

        if not success:
            continue
        _, buffer = imencode('.jpg', frame)

        jpg_as_text = b64encode(buffer).decode('utf-8')
        await server.emit('video_frame', jpg_as_text)


@server.event
async def start_stream(sid):
    print("Stream requested")
    create_task(stream_video())


run_app(app, host="0.0.0.0", port=8000)
