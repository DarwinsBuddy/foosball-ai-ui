from . import Webserver
import yaml
import os

if __name__ == "__main__":
    import argparse

    # Load defaults from config.yaml
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser(description='Run the web server.')
    parser.add_argument('--host', type=str, default=config.get('http', {}).get('host', 'localhost'), help='Host for the web server')
    parser.add_argument('--port', type=int, default=config.get('http', {}).get('port', 443), help='Port for the web server')
    parser.add_argument('--assets-dir', type=str, default=config.get('assets', {}).get('dir', 'assets/web'), help='Assets directory')
    parser.add_argument('--ssl-dir', type=str, default=config.get('http', {}).get('ssl', {}).get('dir', 'assets/ssl'), help='SSL directory')
    parser.add_argument('--certfile', type=str, default=config.get('http', {}).get('ssl', {}).get('certfile', 'server.pem'), help='Path to SSL certificate file')
    parser.add_argument('--keyfile', type=str, default=config.get('http', {}).get('ssl', {}).get('keyfile', 'server.key'), help='Path to SSL key file')
    parser.add_argument('--index-file', type=str, default=config.get('assets', {}).get('index', 'index.html'), help='Path to index.html file')
    parser.add_argument('--zmq-host', type=str, default=config.get('zmq', {}).get('host', 'localhost'), help='Host for the ZMQ subscriber')
    parser.add_argument('--zmq-port', type=int, default=config.get('zmq', {}).get('port', 5555), help='Port for the ZMQ subscriber')
    parser.add_argument('--zmq-topic', type=str, default=config.get('zmq', {}).get('topic', 'ws'), help='Topic for the ZMQ subscriber')
    args = parser.parse_args()

    webserver = Webserver(
        host=args.host, 
        port=args.port, 
        assets_dir=args.assets_dir, 
        ssl_dir=args.ssl_dir,
        certfile=args.certfile, 
        keyfile=args.keyfile, 
        index_file=args.index_file,
        zmq_topic=args.zmq_topic,
        zmq_host=args.zmq_host,
        zmq_port=args.zmq_port
    )
    webserver.run()