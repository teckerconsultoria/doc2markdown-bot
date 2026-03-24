"""
Keep-alive HTTP server para evitar que o Render free tier durma o serviço.

Usa apenas a stdlib (http.server) — sem dependência de Flask.
"""

import json
import os
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # silencia logs de acesso
        pass

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b"Doc2Markdown Bot \xe2\x80\x94 online \xe2\x9c\x85"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def start_keep_alive() -> None:
    """Inicia o servidor HTTP em uma thread daemon."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _Handler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Keep-alive server rodando na porta %d", port)
