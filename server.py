from socketio import AsyncServer
from aiohttp.web import Application, run_app
from cv2 import VideoCapture, imencode, resize
from base64 import b64encode
from asyncio import sleep, create_task

app = Application()
server = AsyncServer(cors_allowed_origins="*")
server.attach(app)
cam = VideoCapture(0)


@server.event
async def connect(socket_id, env):
    print(f"socket with id: {socket_id} connected")


async def stream_video():
    while True:
        success, frame = cam.read()
        frame = resize(frame, (360, 240))
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
