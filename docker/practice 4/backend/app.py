#!/usr/bin/env python3
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
APP_NAME = os.getenv('APP_NAME', 'Backend')

# Простое in-memory хранилище
data_store = {
    'counter': 0,
    'messages': []
}

class BackendHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Обработка preflight запросов"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()  # Добавлено
            self.end_headers()
            response = {
                'service': APP_NAME,
                'status': 'ok',
                'db_connection': f'{DB_HOST}:{DB_PORT}',
                'counter': data_store['counter'],
                'messages': data_store['messages']
            }
            self.wfile.write(json.dumps(response).encode())

        elif path == '/increment':
            data_store['counter'] += 1
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()  # Добавлено
            self.end_headers()
            response = {'counter': data_store['counter']}
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_cors_headers()  # Добавлено
            self.end_headers()

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data_store['messages'].append(body)

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()  # Добавлено
            self.end_headers()
            response = {'status': 'added', 'total': len(data_store['messages'])}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_cors_headers()  # Добавлено
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[BACKEND] {self.address_string()} - {format % args}")

if __name__ == '__main__':
    print(f"=== {APP_NAME} Service ===")
    print(f"DB Connection: {DB_HOST}:{DB_PORT}")
    print("Starting backend on port 5000...")

    server = HTTPServer(('0.0.0.0', 5000), BackendHandler)
    server.serve_forever()