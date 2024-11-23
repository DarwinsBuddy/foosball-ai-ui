import logging
import asyncio
import zmq
import zmq.asyncio

class ZMQSub:
    def __init__(self, zmq_address="tcp://127.0.0.1:5555", zmq_topic="ws", stop_event=None, msg_callback=None):
        self.msg_callback = msg_callback
        self.address = zmq_address
        self.context = zmq.Context()
        self.stop_event = stop_event or asyncio.Event()
        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.zmq_topic = zmq_topic

    def close(self):
        self.stop_event.set()

    async def start(self):
        """ZeroMQ listener that passes messages to a msg_callback."""
        self.socket.connect(self.address)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zmq_topic)
        logging.debug(f"Listening on {self.address} for {self.zmq_topic}")
        while not self.stop_event.is_set():
            try:
                message = await self.socket.recv_string()
                m = message.split(" ")
                topic, msg = m[0], " ".join(m[1:])  # noqa: F841
                if self.msg_callback is None:
                    logging.debug(f"MESSAGE: {msg}")
                else:
                    self.msg_callback(msg)
            except Exception as ex:
                logging.error(f"Exception in ZMQSub: {ex}")

if __name__ == "__main__":
    sub = ZMQSub()
    try:
        asyncio.run(sub.start())
    except Exception as e:
        logging.error(f"Exception in main: {e}")
    input("Press Enter")
    sub.stop_event.set()