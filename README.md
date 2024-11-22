# foosball-ai-ui

![Foosball AI UI](bitmap.png)


## Description
This project is a web interface for the [foosball-ai](https://github.com/foosball-ai/foosball-ai) project. It uses websockets to receive updates from the AI and display them in real-time.

## Setup

Run `setup.sh` to

1. create ssl certificate and key (requires `openssl`)
2. setup a venv in `.venv` (requires `python3` and `python3-venv`)
3. install dependencies

## Configure

Edit `config.yaml` to configure the app. Available options:

#### `http`

| Option    | Description            | Default     |
| --------- | ---------------------- | ----------- |
| `host`    | Host to run the app on | `localhost` |
| `port`    | Port to run the app on | `8443`      |

#### `http.ssl`

| Option     | Description                    | Default        |
| ---------- | ------------------------------ | -------------- |
| `dir`      | Directory to store SSL files   | `assets/ssl`   |
| `certfile` | SSL certificate file           | `server.pem`   |
| `keyfile`  | SSL key file                   | `server.key`   |

#### `assets`

| Option | Description                    | Default      |
| ------ | ------------------------------ | ------------ |
| `dir`  | Directory to serve assets from | `assets/web` |
| `index`| Path to index.html file        | `index.html` |

#### `zmq`

| Option  | Description                    | Default     |
| ------- | ------------------------------ | ----------- |
| `host`  | Host for the ZMQ subscriber    | `localhost` |
| `port`  | Port for the ZMQ subscriber    | `5555`      |
| `topic` | Topic for the ZMQ subscriber   | `ws`        |

## Run

Run `run.sh` to

1. activate the venv
2. run the app
