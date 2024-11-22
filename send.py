import json

import zmq
import time

def zmq_publisher(zmq_address="tcp://127.0.0.1:5555", topic="ws"):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(zmq_address)  # Bind the socket to the address

    # Allow some time for the subscribers to connect
    time.sleep(1)

    while True:
        # Create a message to send
        message = {"type": 1, "data": "ping"}
        print(f"Sending message: {message}")
        if topic is not None:
            socket.send_multipart([bytes(topic, "utf-8"), bytes(json.dumps(message), "utf-8")])
        else:
            # Send the message
            socket.send_string(json.dumps(message))

        # Wait before sending the next message
        time.sleep(2)  # Send a message every 2 seconds

if __name__ == "__main__":
    zmq_publisher()
