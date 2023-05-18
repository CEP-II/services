import http.server
import socketserver
import logging
import json
# Set up logging
LOG_FILE = 'server.log'
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILE, format=FORMAT)
log_handler = logging.FileHandler(LOG_FILE)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter(FORMAT)
log_handler.setFormatter(formatter)
logger = logging.getLogger('server')
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Set up socket

HTTP_PORT = 2000
HTTPS_PORT = 2001

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Enable socket reuse
    socketserver.TCPServer.allow_reuse_address = True

    def do_GET(self):
 
        if self.path == '/log':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            with open(LOG_FILE, 'r', encoding="utf-8") as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            logger.info('Received data: %s' , data)
            
            # Write all links with their names to links.txt
            with open('links.txt', 'w',encoding="utf-8") as f:
                for link in data:
                    f.write(f"{link['name']}: {link['url']}\n")
            
            # Write MQTT link to mqtt.txt
            mqtt_link = next((link['url'] for link in data if link['name'] == 'MQTT'), None)
            if mqtt_link:
                with open('mqtt.txt', 'w',encoding="utf-8") as f:
                    f.write(f'{mqtt_link}')
            
            self.send_response(200)
            self.end_headers()
        except ValueError:
            logger.error('Invalid JSON format')
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON format'}).encode())
        
        return


# Create HTTP server
httpd = socketserver.TCPServer(("", HTTP_PORT), MyHttpRequestHandler)
print(f"Listening on port {HTTP_PORT}")
logger.info("Listening on port %s",HTTP_PORT)
# Create HTTPS server
#httpsd = socketserver.TCPServer(("", HTTPS_PORT), MyHttpRequestHandler)
#httpsd.socket = ssl.wrap_socket(httpsd.socket, keyfile=ssl_keyfile, certfile=ssl_certfile)
#print(f"Listening on port {HTTPS_PORT}")
#logger.info(f"Listening on port {HTTPS_PORT}")


# Serve indefinitely
try:
 #  httpsd.serve_forever()
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
#httpsd.server_close()



