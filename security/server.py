import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from . import auth

_server_instance: HTTPServer | None = None
_server_thread: threading.Thread | None = None


def start_auth_server(auth_port: int = 8765) -> None:
    global _server_instance, _server_thread
    _server_instance = HTTPServer(('localhost', auth_port), _AuthHandler)
    _server_thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
    _server_thread.start()


def stop_auth_server() -> None:
    global _server_instance, _server_thread
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None
    if _server_thread:
        _server_thread.join(timeout=2)
        _server_thread = None


_SUCCESS_HTML = """<!DOCTYPE html><html><head><title>Snake Game</title>
<style>body{font-family:monospace;background:#0c120c;color:#3ce650;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
h1{font-size:2em;}p{color:#c8c8c8;}</style></head>
<body><div><h1>&#10003; Authenticated!</h1>
<p>Return to the game — it should unlock momentarily.</p></div></body></html>"""

_ERROR_HTML = """<!DOCTYPE html><html><head><title>Snake Game</title>
<style>body{font-family:monospace;background:#0c120c;color:#ff4646;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
h1{font-size:2em;}p{color:#c8c8c8;}</style></head>
<body><div><h1>&#10007; Link invalid or expired</h1>
<p>Return to the game and request a new sign-in link.</p></div></body></html>"""


class _AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/auth':
            self._respond(404, b'Not found')
            return

        token = parse_qs(parsed.query).get('token', [None])[0]
        if token and auth.verify_token(token):
            self._respond(200, _SUCCESS_HTML.encode())
        else:
            self._respond(200, _ERROR_HTML.encode())

    def _respond(self, code: int, body: bytes) -> None:
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass
