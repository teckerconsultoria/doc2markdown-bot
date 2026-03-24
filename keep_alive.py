"""
Keep-alive HTTP server para evitar que o Render free tier durma o serviço.

O Render hiberna instâncias free após 15 min de inatividade.
Este módulo sobe um servidor Flask mínimo na porta $PORT que responde
a pings externos (ex: UptimeRobot a cada 5 min).
"""

import os
import threading
import logging
from flask import Flask

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index():
    return "Doc2Markdown Bot — online ✅", 200


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def start_keep_alive() -> None:
    """Inicia o servidor Flask em uma thread daemon."""
    port = int(os.environ.get("PORT", 8080))

    def run():
        logger.info("Keep-alive server rodando na porta %d", port)
        app.run(host="0.0.0.0", port=port, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
