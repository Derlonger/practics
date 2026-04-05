#!/usr/bin/env python3
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlparse
import socket

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')
APP_NAME = os.getenv('APP_NAME', 'Frontend')

class FrontendHandler(BaseHTTPRequestHandler):

    def proxy_to_backend(self, path, method='GET', body=None):
        try:
            backend_full_url = f"{BACKEND_URL}{path}"
            print(f"Proxying {method} request to: {backend_full_url}")

            req = Request(backend_full_url, method=method)
            if body:
                req.add_header('Content-Type', 'application/json')
                req.data = body.encode('utf-8')

            with urlopen(req, timeout=5) as response:
                self.send_response(response.status)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
                return True
        except URLError as e:
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': f'Backend error: {str(e)}'})
            self.wfile.write(error_response.encode())
            return False

    def do_GET(self):
        if self.path.startswith('/api/'):
            backend_path = self.path[4:]
            if not backend_path:
                backend_path = '/'
            self.proxy_to_backend(backend_path, 'GET')
            return

        # Обработка статических файлов (опционально)
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            return

        # Отдаем HTML страницу для всех остальных запросов
        self.serve_html_page()

    def do_POST(self):
        # Проксируем POST запросы к бэкенду
        if self.path.startswith('/api/'):
            backend_path = self.path[4:]
            if not backend_path:
                backend_path = '/'

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode() if content_length > 0 else None

            self.proxy_to_backend(backend_path, 'POST', body)
            return

        self.send_response(404)
        self.end_headers()

    def serve_html_page(self):
        """Отдает HTML страницу"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Пытаемся получить данные с backend для начальной загрузки
        try:
            with urlopen(f"{BACKEND_URL}/", timeout=2) as response:
                backend_data = json.loads(response.read().decode('utf-8'))
                counter = backend_data.get('counter', 0)
                messages = backend_data.get('messages', [])
                backend_status = '✅ Connected'
                backend_info = f"Connected to {BACKEND_URL}"
        except URLError as e:
            counter = 0
            messages = []
            backend_status = '❌ Error'
            backend_info = f"Cannot connect to {BACKEND_URL}: {e}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{APP_NAME}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    animation: fadeIn 0.5s ease-in;
                }}
                @keyframes fadeIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(-20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 2em;
                }}
                .status {{
                    padding: 15px;
                    background: #f0fdf4;
                    border-left: 4px solid #22c55e;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .status.error {{
                    background: #fef2f2;
                    border-left-color: #ef4444;
                }}
                .info {{
                    margin: 20px 0;
                }}
                .counter-box {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8fafc;
                    border-radius: 12px;
                }}
                .counter-value {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin: 10px 0;
                }}
                button {{
                    padding: 12px 24px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    transition: all 0.3s;
                }}
                button:hover {{
                    background: #2563eb;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
                }}
                button:active {{
                    transform: translateY(0);
                }}
                .error {{
                    color: #ef4444;
                    margin-top: 10px;
                    font-size: 14px;
                }}
                .messages-list {{
                    list-style: none;
                    padding: 0;
                }}
                .messages-list li {{
                    padding: 10px;
                    background: #f1f5f9;
                    margin: 5px 0;
                    border-radius: 6px;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    background: #e2e8f0;
                    border-radius: 12px;
                    font-size: 12px;
                    margin-left: 10px;
                }}
                .loading {{
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #3b82f6;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 {APP_NAME}</h1>

                <div class="status {'error' if '❌' in backend_status else ''}">
                    <strong>🔗 Backend Status:</strong> {backend_status}<br>
                    <small>{backend_info}</small>
                </div>

                <div class="counter-box">
                    <h2>Counter</h2>
                    <div class="counter-value" id="counterValue">{counter}</div>
                    <button id="incrementBtn" {'disabled' if '❌' in backend_status else ''}>
                        ➕ Increment Counter
                    </button>
                    <div id="errorMessage" class="error"></div>
                </div>

                <div class="info">
                    <h3>📝 Messages <span class="badge" id="messagesCount">{len(messages)}</span></h3>
                    <ul class="messages-list" id="messagesList">
                        {''.join(f'<li>{msg}</li>' for msg in messages) or '<li>No messages yet</li>'}
                    </ul>
                </div>

                <div class="info">
                    <h3>ℹ️ System Info</h3>
                    <p><strong>API Endpoint:</strong> All requests go through <code>/api/</code> proxy</p>
                    <p><strong>Example:</strong> <code>GET /api/increment</code> → proxied to backend</p>
                </div>
            </div>

            <script>
                // Все запросы идут через относительный путь /api/
                async function incrementCounter() {{
                    const errorDiv = document.getElementById('errorMessage');
                    const btn = document.getElementById('incrementBtn');
                    errorDiv.textContent = '';

                    // Показываем загрузку
                    const originalText = btn.textContent;
                    btn.textContent = '⏳ Loading...';
                    btn.disabled = true;

                    try {{
                        console.log('Sending request to: /api/increment');
                        const response = await fetch('/api/increment', {{
                            method: 'GET',
                            headers: {{
                                'Content-Type': 'application/json'
                            }}
                        }});

                        if (!response.ok) {{
                            const errorData = await response.json();
                            throw new Error(errorData.error || `HTTP error! status: ${{response.status}}`);
                        }}

                        const data = await response.json();
                        console.log('Response:', data);
                        document.getElementById('counterValue').textContent = data.counter;

                        // Обновляем все данные
                        await loadFullData();
                    }} catch (error) {{
                        console.error('Error:', error);
                        errorDiv.textContent = '❌ ' + error.message;
                    }} finally {{
                        btn.textContent = originalText;
                        btn.disabled = false;
                    }}
                }}

                async function loadFullData() {{
                    try {{
                        const response = await fetch('/api/');
                        if (!response.ok) throw new Error('Failed to fetch data');
                        const data = await response.json();
                        document.getElementById('counterValue').textContent = data.counter;
                        document.getElementById('messagesCount').textContent = data.messages.length;

                        const messagesList = document.getElementById('messagesList');
                        if (data.messages.length === 0) {{
                            messagesList.innerHTML = '<li>No messages yet</li>';
                        }} else {{
                            messagesList.innerHTML = data.messages.map(msg => `<li>${{msg}}</li>`).join('');
                        }}
                    }} catch (error) {{
                        console.error('Error loading data:', error);
                    }}
                }}

                // Добавляем обработчик события
                const btn = document.getElementById('incrementBtn');
                if (btn) {{
                    btn.removeEventListener('click', incrementCounter);
                    btn.addEventListener('click', incrementCounter);
                }}

                // Автоматически обновляем данные каждые 5 секунд
                setInterval(loadFullData, 5000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        print(f"[FRONTEND] {self.address_string()} - {format % args}")

if __name__ == '__main__':
    print(f"=== {APP_NAME} Service ===")
    print(f"Backend URL (internal): {BACKEND_URL}")
    print("Starting frontend on port 8080...")
    print("All /api/* requests will be proxied to backend")
    print("Only frontend port 8080 is exposed to outside")

    server = HTTPServer(('0.0.0.0', 8080), FrontendHandler)
    server.serve_forever()