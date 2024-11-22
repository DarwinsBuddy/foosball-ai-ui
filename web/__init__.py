import json
import logging
import os
import ssl
import threading
from logging import config

import asyncio
from aiohttp import web
from asyncio import Event, QueueEmpty
from asyncio.tasks import gather

from .zmq import ZMQSub

class Webserver:
    def __init__(self, host="localhost", port=443, assets_dir='assets/web', ssl_dir='assets/ssl', certfile='server.pem', keyfile='server.key', index_file='index.html', zmq_host='localhost', zmq_port=5556, zmq_topic="ws"):
        config.fileConfig('logging.ini')
        self.host = host
        self.port = port
        self.assets_dir = assets_dir
        self.index_file = index_file
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(
            certfile=os.path.join(os.path.dirname(__file__), ssl_dir, certfile),
            keyfile=os.path.join(os.path.dirname(__file__), ssl_dir, keyfile)
        )
        self.active_connections = set()
        self.http_app = web.Application()
        self.stop_event = Event()  # Event to signal stop

        # Set up HTTP routes
        self.http_app.router.add_get('/', self.get_index)
        self.http_app.router.add_get('/ws', self.websocket_handler)  # WebSocket route

        self.start_lock = threading.Lock()
        self.q = asyncio.Queue()

        self.zmq_subscriber = ZMQSub(zmq_address=f"tcp://{zmq_host}:{zmq_port}", zmq_topic=zmq_topic, stop_event=self.stop_event, msg_callback=self.broadcast)

    @staticmethod
    async def get_index(request):
        file_path = os.path.join(os.path.dirname(__file__), request.app['assets_dir'], request.app['index_file'])
        try:
            with open(file_path, "r") as file:
                html_content = file.read()
            return web.Response(text=html_content, content_type='text/html')
        except FileNotFoundError:
            logging.error("Index file not found.")
            return web.Response(text="404 Not Found", status=404)

    @staticmethod
    def ws_error(message, errors:list = None):
        return {
            "type": "server:ws:invalid-json",
            "data": message,
            "errors": errors or []
        }


    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.active_connections.add(ws)
        logging.debug(f">>>> Active connections: {len(self.active_connections)}")
        logging.debug("New WebSocket connection established.")

        try:
            async for msg in ws:
                logging.debug(f"Received message: {msg}")
                if msg.type == web.WSMsgType.TEXT:
                    # Handle text messages
                    try:
                        data = json.loads(msg.data)
                        response_message = json.dumps(data)
                    except json.JSONDecodeError as e:
                        self.broadcast(self.ws_error("Invalid JSON data received.", [e]))
                        response_message = msg.data  # str
                    self.broadcast(response_message)
                elif msg.type == web.WSMsgType.BINARY:
                    logging.debug(f"Received binary data: {msg.data}")
                    self.broadcast(msg.data)
                elif msg.type == web.WSMsgType.CLOSE:
                    logging.debug("Client requested to close the connection.")
                    break

        finally:
            self.active_connections.remove(ws)
            logging.debug("WebSocket connection closed")

        return ws

    def broadcast(self, message: dict | str):
        if self.q is not None:
            print("putting into q", message)
            asyncio.run_coroutine_threadsafe(self.q.put(message), asyncio.get_event_loop())
            print("message put into queue")
        else:
            logging.error("Queue is None")

    async def process_queue(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(0.1)
            try:
                if self.q is not None:
                    m = self.q.get_nowait()
                    await self._broadcast(m)
                else:
                    raise Exception("Queue is None")
            except QueueEmpty:
                pass
            except Exception as e:
                logging.error("GET QUEUE: ", e)
                pass
        logging.debug("shutting down process_queue")


    async def _broadcast(self, message: dict | str | bytes):
        print(f">>>> Active connections: {len(self.active_connections)}")
        logging.debug(f"message: {message}")
        if self.active_connections:
            if isinstance(message, dict):
                await gather(*(ws.send_json(message) for ws in self.active_connections))
            elif type(message) is bytes:
                await gather(*(ws.send_bytes(message) for ws in self.active_connections))
            else:
                await gather(*(ws.send_str(message) for ws in self.active_connections))

    async def start_server(self):
        self.http_app['assets_dir'] = self.assets_dir
        self.http_app['index_file'] = self.index_file
        runner = web.AppRunner(self.http_app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port, ssl_context=self.ssl_context)
        await site.start()
        logging.info(f"Serving HTTP and WebSocket on https://{self.host}:{self.port}")
        # Wait for the stop event to be set
        await self.stop_event.wait()
        # Shutdown logic after stop event is set
        await runner.cleanup()
        logging.debug("shutting down start_server")

    def run(self):
        logging.debug("Running the server...")
        asyncio.get_event_loop().run_until_complete(self.main_task())

    async def main_task(self):
        await asyncio.gather(
            self.start_server(),
            self.zmq_subscriber.start(),
            self.process_queue()
        )

    def stop(self):
        # Signal the event to stop the server
        self.stop_event.set()
        # Close the HTTP server and all WebSocket connections
        asyncio.get_event_loop().run_coroutine_threadsafe(self.shutdown())

    async def shutdown(self):
        for conn in self.active_connections:
            await conn.close()
        logging.info("All WebSocket connections closed.")
