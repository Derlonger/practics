#!/usr/bin/env python3
import os
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler

class ArchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Получаем информацию об архитектуре
        arch = platform.machine()
        system = platform.system()
        python_version = platform.python_version()

        html = f"""
        <html>
        <head>
            <title>Multi-Arch Demo</title>
            <style>
                body {{
                    font-family: monospace;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #1e1e1e;
                    color: #00ff00;
                }}
                .box {{
                    border: 2px solid #00ff00;
                    padding: 20px;
                    margin: 20px 0;
                    background: #000;
                }}
                h1 {{ color: #00ff00; }}
                .label {{ color: #888; }}
                .value {{ color: #00ff00; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>🏗️  Multi-Architecture Build Demo</h1>

            <div class="box">
                <div><span class="label">Architecture:</span> <span class="value">{arch}</span></div>
                <div><span class="label">System:</span> <span class="value">{system}</span></div>
                <div><span class="label">Python:</span> <span class="value">{python_version}</span></div>
            </div>

            <div class="box">
                <h2>Supported Architectures:</h2>
                <ul>
                    <li>linux/amd64 (x86_64) - Intel/AMD 64-bit</li>
                    <li>linux/arm64 (aarch64) - ARM 64-bit (M1/M2 Mac, AWS Graviton)</li>
                    <li>linux/arm/v7 - ARM 32-bit (Raspberry Pi)</li>
                </ul>
            </div>

            <div class="box">
                <p>This image was built for multiple architectures using Docker Buildx!</p>
                <p>Current running architecture: <strong>{arch}</strong></p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        print(f"[{platform.machine()}] {format % args}")

if __name__ == '__main__':
    print("=" * 60)
    print(f"Multi-Arch Demo")
    print(f"Architecture: {platform.machine()}")
    print(f"System: {platform.system()}")
    print("=" * 60)

    server = HTTPServer(('0.0.0.0', 8080), ArchHandler)
    server.serve_forever()
